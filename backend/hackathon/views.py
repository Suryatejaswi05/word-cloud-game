import json
import re
from datetime import timedelta

from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views import View
from .models import Question, UserAnswer, WordFrequency, UserScore,WordCloud
from .models import WordCloudRound, WordCloudResponse, WordFrequencyByRound, ShareEvent, RoundScore
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
import random
from .auth import (
    create_session_token,
    OtpDispatchError,
    OtpVerifyError,
    get_session_times,
    hash_session_token,
    dispatch_otp,
    verify_otp_via_gateway,
    verify_password,
)
from .models import AppUser, AppUserMember, AuthSession, OtpChallenge
# views.py
from django.shortcuts import get_object_or_404
from .models import GameSession

def create_game_session(request):
    """Create a new game session for sharing"""
    questions = list(Question.objects.values_list('id', flat=True)[:25])  # Get 25 question IDs
    game = GameSession.objects.create(questions=questions)
    return JsonResponse({
        'game_id': str(game.id),
        'share_url': f"/game/{game.id}/"
    })

def join_shared_game(request, game_id):
    """Join an existing shared game"""
    game = get_object_or_404(GameSession, id=game_id)
    return JsonResponse({
        'questions': game.questions,
        'current_index': game.current_question_index
    })
# views.py
from django.http import JsonResponse
from .models import Question  # Make sure this exists!
import json

def get_questions(request):
    try:
        questions = Question.objects.all()
        # Serialize questions
        questions_data = [
            {
                'id': q.id,
                'text': q.question,
                # ... other fields
            }
            for q in questions
        ]
        return JsonResponse({'questions': questions_data})
    except Exception as e:
        # This is returning the 500 error
        return JsonResponse({'error': str(e)}, status=500)

def _normalize_phone(raw: str) -> str:
    return re.sub(r'\D+', '', (raw or '').strip())


def _get_bearer_token(request: HttpRequest) -> str | None:
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    prefix = 'Bearer '
    if not auth_header.startswith(prefix):
        return None

    token = auth_header[len(prefix) :].strip()
    return token or None


def _get_session(request: HttpRequest) -> AuthSession | None:
    token = _get_bearer_token(request)
    if not token:
        return None

    token_hash = hash_session_token(token)
    return (
        AuthSession.objects.select_related('user', 'member')
        .filter(token_hash=token_hash, revoked_at__isnull=True, expires_at__gt=timezone.now())
        .first()
    )


    # Word Cloud Game API Views
import secrets
import string
from collections import Counter
import colorsys

def generate_share_token():
    """Generate a unique 32-character share token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def get_random_colors(n):
    """Generate n distinct colors for word cloud visualization"""
    colors = []
    for i in range(n):
        hue = (i / n) % 1.0
        saturation = 0.6 + (i % 3) * 0.15
        lightness = 0.5
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(hex_color)
    return colors

@csrf_exempt
def create_word_cloud_round(request):
    """Create a new word cloud round"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        session = _get_session(request)
        if not session:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        data = json.loads(request.body)
        question_id = data.get('question_id')
        
        if not question_id:
            return JsonResponse({"error": "question_id is required"}, status=400)
        
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"error": "Question not found"}, status=404)
        
        # Create new round
        share_token = generate_share_token()
        round_obj = WordCloudRound.objects.create(
            question=question,
            created_by=session.member,
            share_token=share_token
        )
        
        # Initialize score for creator
        RoundScore.objects.create(
            word_cloud_round=round_obj,
            player=session.member
        )
        
        return JsonResponse({
            "id": round_obj.id,
            "share_token": share_token,
            "question": question.question,
            "created_at": round_obj.created_at.isoformat()
        }, status=201)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_round_details(request, share_token):
    """Get details of a word cloud round by share token"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        try:
            round_obj = WordCloudRound.objects.select_related('question', 'created_by').get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        response_count = WordCloudResponse.objects.filter(word_cloud_round=round_obj).count()
        
        return JsonResponse({
            "id": round_obj.id,
            "question": round_obj.question.question,
            "created_by": round_obj.created_by.name,
            "response_count": response_count,
            "is_active": round_obj.is_active,
            "created_at": round_obj.created_at.isoformat()
        }, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def submit_word_response(request, share_token):
    """Submit a word response to a word cloud round"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        session = _get_session(request)
        if not session:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        try:
            round_obj = WordCloudRound.objects.get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        if not round_obj.is_active:
            return JsonResponse({"error": "Round is not active"}, status=400)
        
        data = json.loads(request.body)
        word = data.get('word', '').strip()
        
        # Input validation
        if not word:
            return JsonResponse({"error": "Word cannot be empty"}, status=400)
        
        if len(word.split()) > 1:
            return JsonResponse({"error": "Only single word responses allowed"}, status=400)
        
        # Normalize word (lowercase)
        word_normalized = word.lower()
        
        # Check if user already responded
        existing_response = WordCloudResponse.objects.filter(
            word_cloud_round=round_obj,
            respondent=session.member
        ).first()
        
        if existing_response:
            return JsonResponse({"error": "You have already submitted a response"}, status=400)
        
        # Create response with augmented words (10+ variations)
        augmented_words = [
            word_normalized,
            word.upper(),
            word.capitalize(),
        ]
        
        # Add variations with common prefixes/suffixes
        if len(word_normalized) > 3:
            augmented_words.extend([
                word_normalized[:-1],
                word_normalized + 's',
                word_normalized + 'ing',
                word_normalized + 'ed',
                word_normalized + 'ly',
                word_normalized + 'ness',
                word_normalized[1:],
                word_normalized + 'er',
            ])
        
        response_obj = WordCloudResponse.objects.create(
            word_cloud_round=round_obj,
            respondent=session.member,
            response_word=word_normalized,
            augmented_words=augmented_words,
            is_valid=True
        )
        
        # Update word frequency
        freq_obj, created = WordFrequencyByRound.objects.get_or_create(
            word_cloud_round=round_obj,
            word=word_normalized,
            defaults={'freq': 1}
        )
        
        if not created:
            freq_obj.freq += 1
            freq_obj.save()
        
        # Update or create score
        score_obj, score_created = RoundScore.objects.get_or_create(
            word_cloud_round=round_obj,
            player=session.member
        )
        
        if not score_created and score_obj.response_score == 0:
            score_obj.response_score = 1
            score_obj.total_score = 1 + score_obj.share_count
            score_obj.save()
        
        return JsonResponse({
            "success": True,
            "word": word_normalized,
            "message": "Response submitted successfully"
        }, status=201)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _json_body(request: HttpRequest) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return {}


class HealthView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'status': 'ok'})


class ApiLoginView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        payload = _json_body(request)
        username_raw = (payload.get('username') or '').strip()
        password = (payload.get('password') or '').strip()

        if not username_raw or not password:
            return JsonResponse({'error': 'Please enter username and password.'}, status=400)

        members_qs = AppUserMember.objects.select_related('user').filter(user__is_active=True)
        if '@' in username_raw:
            members_qs = members_qs.filter(email__iexact=username_raw)
        else:
            phone = _normalize_phone(username_raw)
            if not phone:
                return JsonResponse({'error': 'Please enter username and password.'}, status=400)
            members_qs = members_qs.filter(phone=phone)

        members = list(members_qs)
        if not members:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        matched_user: AppUser | None = None
        matched_member: AppUserMember | None = None
        for member in members:
            user = member.user
            if verify_password(
                password,
                salt_b64=user.password_salt_b64,
                password_hash_b64=user.password_hash_b64,
                iterations=user.password_iterations,
            ):
                matched_user = user
                matched_member = member
                break

        if matched_user is None:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        user = matched_user

        raw_token = create_session_token()
        times = get_session_times()
        AuthSession.objects.create(
            user=user,
            member=matched_member,
            token_hash=hash_session_token(raw_token),
            created_at=times.created_at,
            expires_at=times.expires_at,
        )

        return JsonResponse(
            {
                'token': raw_token,
                'expires_at': times.expires_at.isoformat(),
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
            }
        )


class ApiMeView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        if session.member is None:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        return JsonResponse(
            {
                'user': {
                    'id': session.user.id,
                    'username': session.user.username,
                    'team_no': session.user.team_no,
                },
                'member': {
                    'id': session.member.id,
                    'member_id': session.member.member_id,
                    'name': session.member.name,
                    'email': session.member.email,
                    'phone': session.member.phone,
                },
            }
        )


class ApiLogoutView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None:
            return JsonResponse({'ok': True})

        session.revoked_at = timezone.now()
        session.save(update_fields=['revoked_at'])
        return JsonResponse({'ok': True})


class ApiOtpRequestView(View):
    OTP_TTL = timedelta(minutes=5)

    def post(self, request: HttpRequest) -> JsonResponse:
        payload = _json_body(request)
        channel = (payload.get('channel') or '').strip().lower()
        phone = _normalize_phone(payload.get('phone') or payload.get('username') or '')
        email = (payload.get('email') or payload.get('username') or '').strip()
        team_no_raw = payload.get('team_no')

        if channel not in {'whatsapp', 'email'}:
            return JsonResponse({'error': 'Invalid OTP channel.'}, status=400)

        if channel == 'whatsapp' and not phone:
            return JsonResponse({'error': 'Please enter mobile number.'}, status=400)
        if channel == 'email' and not email:
            return JsonResponse({'error': 'Please enter email id.'}, status=400)

        if channel == 'whatsapp':
            members_qs = (
                AppUserMember.objects.select_related('user')
                .filter(phone=phone)
                .filter(user__is_active=True)
            )
        else:
            members_qs = (
                AppUserMember.objects.select_related('user')
                .filter(email__iexact=email)
                .filter(user__is_active=True)
            )

        if team_no_raw is not None and str(team_no_raw).strip() != '':
            try:
                team_no = int(team_no_raw)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Invalid team number.'}, status=400)
            members_qs = members_qs.filter(user__team_no=team_no)

        members = list(members_qs)
        if not members:
            if channel == 'whatsapp':
                return JsonResponse({'error': 'Mobile number not registered.'}, status=404)
            return JsonResponse({'error': 'Email id not registered.'}, status=404)

        if len(members) > 1:
            identifier_label = 'mobile number' if channel == 'whatsapp' else 'email id'
            teams = []
            for m in members:
                teams.append({'team_no': m.user.team_no, 'username': m.user.username})
            teams = sorted(teams, key=lambda t: (t['team_no'] is None, t['team_no'] or 0))
            return JsonResponse(
                {
                    'error': f'Multiple team accounts found for this {identifier_label}. Please select team number.',
                    'teams': teams,
                },
                status=409,
            )

        member = members[0]

        identifier = phone if channel == 'whatsapp' else (member.email or email)

        try:
            dispatch_otp(channel=channel, identifier=identifier, display_name=member.name)
        except OtpDispatchError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        now = timezone.now()
        expires_at = now + self.OTP_TTL

        with transaction.atomic():
            OtpChallenge.objects.filter(
                member=member,
                identifier=identifier,
                consumed_at__isnull=True,
                expires_at__gt=now,
            ).update(consumed_at=now)

            challenge = OtpChallenge.objects.create(
                identifier=identifier,
                member=member,
                created_at=now,
                expires_at=expires_at,
            )

        return JsonResponse({'challenge_id': challenge.id, 'expires_at': expires_at.isoformat()})


class ApiOtpVerifyView(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        payload = _json_body(request)
        challenge_id = payload.get('challenge_id')
        otp = (payload.get('otp') or '').strip()

        if not challenge_id or not otp:
            return JsonResponse({'error': 'Please enter OTP.'}, status=400)

        try:
            challenge_id_int = int(challenge_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid OTP request.'}, status=400)

        challenge = (
            OtpChallenge.objects.select_related('member', 'member__user')
            .filter(id=challenge_id_int)
            .first()
        )
        if challenge is None or not challenge.is_valid() or challenge.member is None:
            return JsonResponse({'error': 'Invalid or expired OTP.'}, status=401)

        try:
            ok = verify_otp_via_gateway(identifier=challenge.identifier, otp=otp)
        except OtpVerifyError as exc:
            return JsonResponse({'error': str(exc)}, status=502)

        if not ok:
            return JsonResponse({'error': 'Invalid or expired OTP.'}, status=401)

        now = timezone.now()

        with transaction.atomic():
            updated = OtpChallenge.objects.filter(id=challenge.id, consumed_at__isnull=True).update(consumed_at=now)
            if updated != 1:
                return JsonResponse({'error': 'Invalid or expired OTP.'}, status=401)

            member = challenge.member
            user = member.user

            raw_token = create_session_token()
            times = get_session_times()
            AuthSession.objects.create(
                user=user,
                member=member,
                token_hash=hash_session_token(raw_token),
                created_at=times.created_at,
                expires_at=times.expires_at,
            )

        return JsonResponse(
            {
                'token': raw_token,
                'expires_at': times.expires_at.isoformat(),
                'user': {'id': user.id, 'username': user.username},
            }
        )

# def get_questions(request):
#     questions = list(Question.objects.all())
#     random_questions = random.sample(questions, 25)

#     return JsonResponse({
#         "questions": [
#             {"id": q.id, "text": q.question_text}
#             for q in random_questions
#         ]
#     })

@csrf_exempt
def submit_answer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            answer_text = data.get('answer', '').strip().lower()
            
            if not answer_text:
                return JsonResponse({'error': 'Answer cannot be empty'}, status=400)
            
            # Check if word already exists in wordcloud table
            try:
                word_obj = WordFrequency.objects.get(word=answer_text)
                # Increment frequency
                word_obj.freq += 1
                word_obj.save()
                created = False
            except WordFrequency.DoesNotExist:
                # Create new word entry
                word_obj = WordFrequency.objects.create(
                    word=answer_text,
                    freq=1
                )
                created = True
            
            # Return success response
            return JsonResponse({
                'success': True,
                'word': word_obj.word,
                'frequency': word_obj.freq,
                'created': created
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_wordcloud(request):
    try:
        words = WordFrequency.objects.all().order_by('-freq')[:50]  # Use freq
        return JsonResponse({
            "words": [
                {
                    "text": w.word, 
                    "value": w.freq,  # Use freq
                    "frequency": w.freq  # Add for compatibility
                } 
                for w in words
            ]
        })
    except Exception as e:
        print(f"Error in get_wordcloud: {str(e)}")
        return JsonResponse({"error": str(e) }, status=500)


    # Word Cloud Game - Get Word Cloud Data
@csrf_exempt
def get_word_cloud_data(request, share_token):
    """Get aggregated word cloud data for visualization"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        try:
            round_obj = WordCloudRound.objects.get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        # Get all word frequencies
        word_freqs = WordFrequencyByRound.objects.filter(
            word_cloud_round=round_obj
        ).order_by('-freq')
        
        if not word_freqs.exists():
            return JsonResponse({"words": []}, status=200)
        
        # Generate colors for words
        words_data = []
        max_freq = word_freqs.first().freq if word_freqs else 1
        colors = get_random_colors(len(word_freqs))
        
        for idx, freq_obj in enumerate(word_freqs):
            # Font size proportional to frequency
            font_size = max(14, min(72, 14 + (freq_obj.freq / max_freq) * 58))
            words_data.append({
                "text": freq_obj.word,
                "value": freq_obj.freq,
                "size": font_size,
                "color": colors[idx % len(colors)]
            })
        
        return JsonResponse({"words": words_data}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def record_share_event(request, share_token):
    """Record a share event for scoring"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        session = _get_session(request)
        if not session:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        try:
            round_obj = WordCloudRound.objects.get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        data = json.loads(request.body)
        platform = data.get('platform', 'copy')
        
        if platform not in ['copy', 'whatsapp', 'facebook', 'twitter', 'email']:
            platform = 'copy'
        
        # Record share event
        share_event = ShareEvent.objects.create(
            word_cloud_round=round_obj,
            shared_by=session.member,
            share_platform=platform
        )
        
        # Update score
        score_obj, created = RoundScore.objects.get_or_create(
            word_cloud_round=round_obj,
            player=session.member
        )
        
        score_obj.share_count += 1
        score_obj.total_score = score_obj.response_score + score_obj.share_count
        score_obj.save()
        
        return JsonResponse({
            "success": True,
            "message": "Share event recorded",
            "share_count": score_obj.share_count,
            "total_score": score_obj.total_score
        }, status=201)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_leaderboard(request, share_token):
    """Get leaderboard for a word cloud round"""
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        try:
            round_obj = WordCloudRound.objects.get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        scores = RoundScore.objects.filter(
            word_cloud_round=round_obj
        ).select_related('player').order_by('-total_score')
        
        leaderboard = []
        for idx, score in enumerate(scores, 1):
            leaderboard.append({
                "rank": idx,
                "player": score.player.name,
                "response_score": score.response_score,
                "share_count": score.share_count,
                "total_score": score.total_score
            })
        
        return JsonResponse({"leaderboard": leaderboard}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def end_round(request, share_token):
    """End a word cloud round"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        session = _get_session(request)
        if not session:
            return JsonResponse({"error": "Unauthorized"}, status=401)
        
        try:
            round_obj = WordCloudRound.objects.get(share_token=share_token)
        except WordCloudRound.DoesNotExist:
            return JsonResponse({"error": "Round not found"}, status=404)
        
        # Only creator can end the round
        if round_obj.created_by != session.member:
            return JsonResponse({"error": "Only round creator can end the round"}, status=403)
        
        round_obj.is_active = False
        round_obj.save()
        
        # Get final leaderboard
        scores = RoundScore.objects.filter(
            word_cloud_round=round_obj
        ).select_related('player').order_by('-total_score')
        
        final_scores = []
        for idx, score in enumerate(scores, 1):
            final_scores.append({
                "rank": idx,
                "player_id": score.player.id,
                "player_name": score.player.name,
                "total_score": score.total_score
            })
        
        return JsonResponse({
            "success": True,
            "message": "Round ended successfully",
            "final_scores": final_scores
        }, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
