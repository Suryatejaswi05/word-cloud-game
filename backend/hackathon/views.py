import json
import re
import uuid
import random
from datetime import timedelta

from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.views import View

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Word
from .models import Question, WordCloud

from .models import Question, WordCloud, UserAnswer, AnswerEvent, ShareEvent

from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.http import JsonResponse

import json
from .models import Word, UserAnswer, ShareEvent
from .models import Word, AnswerEvent, ShareEvent


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

from .models import AppUser, AppUserMember, AuthSession, OtpChallenge, Hackathon, Submission, Question, GameRound, Response, ShareEvent

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



def _generate_share_token() -> str:
    return str(uuid.uuid4())


def _augment_responses(round_id: int, word: str):
    # Add 10 random words for simulation
    random_words = ['happy', 'sad', 'excited', 'tired', 'angry', 'joyful', 'frustrated', 'calm', 'energetic', 'relaxed']
    for _ in range(10):
        augmented_word = random.choice(random_words)
        Response.objects.create(
            round_id=round_id,
            player_id=f'augmented_{uuid.uuid4()}',
            word=augmented_word,
            is_augmented=True
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
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        payload = _json_body(request)
        username_raw = (payload.get('username') or '').strip()
        password = (payload.get('password') or '').strip()

        if not username_raw or not password:
            return JsonResponse({'error': 'Please enter username and password.'}, status=400)

        # Simple hardcoded authentication
        if password != '1234':
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        # Reset user score on fresh login - clear previous answer and share events
        user_id = 1  # Using hardcoded user_id from the system
        try:
            AnswerEvent.objects.filter(user_id=user_id).delete()
            ShareEvent.objects.filter(player_id=str(user_id)).delete()
        except Exception as e:
            print(f"Error clearing user events on login: {e}")

        # Generate a mock token
        raw_token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=1)

        return JsonResponse(
            {
                'token': raw_token,
                'expires_at': expires_at.isoformat(),
                'user': {
                    'id': 1,
                    'username': username_raw,
                    'team_no': '001',
                    'points': 0,
                },
            }
        )


class ApiMeView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        # Mock authentication - just check if there's a Bearer token
        token = _get_bearer_token(request)
        if not token:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        # Return mock user data
        return JsonResponse(
            {
                'user': {
                    'id': 1,
                    'username': 'user',
                    'team_no': '001',
                    'points': 0,
                },
                'member': {
                    'id': 1,
                    'member_id': 'M001',
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'phone': '1234567890',
                },
            }
        )


class ApiQuestionsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        try:
            # Try to fetch questions from default database
            questions_qs = Question.objects.all()
            questions = []
            
            for q in questions_qs:
                # Use text field if available, otherwise question_text
                question_text = getattr(q, 'text', None) or getattr(q, 'question_text', None) or ''
                if question_text:
                    questions.append({
                        'id': q.id,
                        'text': question_text,
                        'question_text': question_text,
                    })
            
            # If no questions in database, return default questions
            if not questions:
                questions = [
                    {'id': 1, 'text': 'How are you feeling today?', 'question_text': 'How are you feeling today?'},
                    {'id': 2, 'text': 'What is your favorite color?', 'question_text': 'What is your favorite color?'},
                    {'id': 3, 'text': 'What motivates you the most?', 'question_text': 'What motivates you the most?'},
                    {'id': 4, 'text': 'How was your day?', 'question_text': 'How was your day?'},
                    {'id': 5, 'text': 'What are you grateful for?', 'question_text': 'What are you grateful for?'},
                    {'id': 6, 'text': 'What makes you happy?', 'question_text': 'What makes you happy?'},
                    {'id': 7, 'text': 'What is your biggest challenge?', 'question_text': 'What is your biggest challenge?'},
                    {'id': 8, 'text': 'What are you looking forward to?', 'question_text': 'What are you looking forward to?'},
                    {'id': 9, 'text': 'How do you relax?', 'question_text': 'How do you relax?'},
                    {'id': 10, 'text': 'What inspires you?', 'question_text': 'What inspires you?'},
                ]
            
            return JsonResponse({'questions': questions})
        except Exception as e:
            # If database query fails (table doesn't exist), return default questions
            questions = [
                {'id': 1, 'text': 'How are you feeling today?', 'question_text': 'How are you feeling today?'},
                {'id': 2, 'text': 'What is your favorite color?', 'question_text': 'What is your favorite color?'},
                {'id': 3, 'text': 'What motivates you the most?', 'question_text': 'What motivates you the most?'},
                {'id': 4, 'text': 'How was your day?', 'question_text': 'How was your day?'},
                {'id': 5, 'text': 'What are you grateful for?', 'question_text': 'What are you grateful for?'},
                {'id': 6, 'text': 'What makes you happy?', 'question_text': 'What makes you happy?'},
                {'id': 7, 'text': 'What is your biggest challenge?', 'question_text': 'What is your biggest challenge?'},
                {'id': 8, 'text': 'What are you looking forward to?', 'question_text': 'What are you looking forward to?'},
                {'id': 9, 'text': 'How do you relax?', 'question_text': 'How do you relax?'},
                {'id': 10, 'text': 'What inspires you?', 'question_text': 'What inspires you?'},
            ]
            return JsonResponse({'questions': questions})


class ApiLogoutView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        # Mock logout - just return success
        return JsonResponse({'ok': True})


class ApiOtpRequestView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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



class ApiHackathonsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        hackathons = Hackathon.objects.filter(is_active=True).order_by('-start_date')
        data = []
        for h in hackathons:
            data.append({
                'id': h.id,
                'name': h.name,
                'description': h.description,
                'start_date': h.start_date.isoformat(),
                'end_date': h.end_date.isoformat(),
                'registration_deadline': h.registration_deadline.isoformat(),
            })
        return JsonResponse({'hackathons': data})


class ApiSubmissionsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        submissions = Submission.objects.filter(team=session.user).select_related('hackathon')
        data = []
        for s in submissions:
            data.append({
                'id': s.id,
                'hackathon': {
                    'id': s.hackathon.id,
                    'name': s.hackathon.name,
                },
                'title': s.title,
                'description': s.description,
                'github_url': s.github_url,
                'demo_url': s.demo_url,
                'submitted_at': s.submitted_at.isoformat(),
            })
        return JsonResponse({'submissions': data})

    def post(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        payload = _json_body(request)
        hackathon_id = payload.get('hackathon_id')
        title = (payload.get('title') or '').strip()
        description = (payload.get('description') or '').strip()
        github_url = (payload.get('github_url') or '').strip()
        demo_url = (payload.get('demo_url') or '').strip()

        if not hackathon_id or not title or not description:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            hackathon = Hackathon.objects.get(id=hackathon_id, is_active=True)
        except Hackathon.DoesNotExist:
            return JsonResponse({'error': 'Hackathon not found'}, status=404)

        if Submission.objects.filter(hackathon=hackathon, team=session.user).exists():
            return JsonResponse({'error': 'Submission already exists for this hackathon'}, status=400)

        submission = Submission.objects.create(
            hackathon=hackathon,
            team=session.user,
            title=title,
            description=description,
            github_url=github_url,
            demo_url=demo_url,
        )

        return JsonResponse({
            'id': submission.id,
            'message': 'Submission created successfully'
        })


class ApiCreateRoundView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        payload = _json_body(request)
        question_text = (payload.get('question') or '').strip()

        if not question_text:
            return JsonResponse({'error': 'Question is required'}, status=400)

        with transaction.atomic():
            question = Question.objects.create(
                text=question_text,
                created_by=session.user
            )
            share_token = _generate_share_token()
            round_obj = GameRound.objects.create(
                question=question,
                created_by=session.user,
                share_token=share_token
            )
            session.user.points += 1
            session.user.save(update_fields=['points'])

        return JsonResponse({
            'round_id': round_obj.id,
            'share_token': share_token,
            'share_url': f'/respond/{share_token}'
        })


class ApiRoundDetailsView(View):
    def get(self, request: HttpRequest, round_id: int) -> JsonResponse:
        try:
            round_obj = GameRound.objects.select_related('question').get(id=round_id)
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)

        response_count = Response.objects.filter(round=round_obj, is_augmented=False).count()

        return JsonResponse({
            'id': round_obj.id,
            'question': round_obj.question.text,
            'status': round_obj.status,
            'response_count': response_count,
            'created_at': round_obj.created_at.isoformat()
        })


class ApiRespondView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request: HttpRequest, share_token: str) -> JsonResponse:
        try:
            round_obj = GameRound.objects.select_related('question').get(share_token=share_token, status='active')
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive round'}, status=404)

        return JsonResponse({
            'round_id': round_obj.id,
            'question': round_obj.question.text
        })

    def post(self, request: HttpRequest, share_token: str) -> JsonResponse:
        try:
            round_obj = GameRound.objects.get(share_token=share_token, status='active')
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive round'}, status=404)

        payload = _json_body(request)
        word = (payload.get('word') or '').strip().lower()
        player_id = (payload.get('player_id') or str(uuid.uuid4())).strip()

        if not word:
            return JsonResponse({'error': 'Word is required'}, status=400)

        # Validate single word, no spaces, punctuation
        if ' ' in word or not word.isalnum():
            return JsonResponse({'error': 'Please enter a single word with letters only'}, status=400)

        session = _get_session(request)

        with transaction.atomic():
            response, created = Response.objects.get_or_create(
                round=round_obj,
                player_id=player_id,
                defaults={'word': word}
            )
            if not created:
                return JsonResponse({'error': 'You have already responded to this round'}, status=400)

            # Augment with 10 random words
            _augment_responses(round_obj.id, word)

            if session:
                session.user.points += 1
                session.user.save(update_fields=['points'])

        return JsonResponse({'message': 'Response submitted successfully'})


class ApiWordCloudView(View):
    def get(self, request: HttpRequest, round_id: int) -> JsonResponse:
        try:
            round_obj = GameRound.objects.get(id=round_id)
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)

        # Aggregate word frequencies
        from django.db.models import Count
        frequencies = Response.objects.filter(round=round_obj).values('word').annotate(count=Count('word')).order_by('-count')

        data = []
        for f in frequencies:
            word = f['word'].upper()
            if word.replace(' ', '').isalnum() and ' ' not in word:
                data.append({'word': word, 'count': f['count']})

        return JsonResponse({'frequencies': data})


class ApiShareView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest, round_id: int) -> JsonResponse:
        try:
            round_obj = GameRound.objects.get(id=round_id, status='active')
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Round not found or inactive'}, status=404)

        payload = _json_body(request)
        player_id = (payload.get('player_id') or str(uuid.uuid4())).strip()

        ShareEvent.objects.create(round=round_obj, player_id=player_id)

        return JsonResponse({'message': 'Share recorded'})


class ApiLeaderboardView(View):
    def get(self, request: HttpRequest, round_id: int) -> JsonResponse:
        try:
            round_obj = GameRound.objects.get(id=round_id)
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)

        # Calculate scores: responses + shares per player
        response_scores = Response.objects.filter(round=round_obj, is_augmented=False).values('player_id').annotate(score=Count('player_id'))
        share_scores = ShareEvent.objects.filter(round=round_obj).values('player_id').annotate(shares=Count('player_id'))

        scores = {}
        for r in response_scores:
            scores[r['player_id']] = r['score']
        for s in share_scores:
            scores[s['player_id']] = scores.get(s['player_id'], 0) + s['shares']

        leaderboard = [{'player_id': pid, 'score': score} for pid, score in scores.items()]
        leaderboard.sort(key=lambda x: x['score'], reverse=True)

        return JsonResponse({'leaderboard': leaderboard})


class ApiEndRoundView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest, round_id: int) -> JsonResponse:
        session = _get_session(request)
        if session is None or not session.user.is_active:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        try:
            round_obj = GameRound.objects.get(id=round_id, created_by=session.user)
        except GameRound.DoesNotExist:
            return JsonResponse({'error': 'Round not found'}, status=404)

        round_obj.status = 'ended'
        round_obj.save()

        return JsonResponse({'message': 'Round ended'})

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
from django.http import JsonResponse
from .models import Word




# ---------------- USER SCORE ----------------
def get_user_score(request):
    user_id = request.GET.get("user_id")

    if not user_id:
        return JsonResponse({"total_score": 0})

    answer_score = AnswerEvent.objects.filter(user_id=user_id).count()
    share_score = ShareEvent.objects.filter(player_id=str(user_id)).count()

    total_score = answer_score + share_score

    return JsonResponse({
        "total_score": total_score
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from .models import Word


# ---------------- HEALTH ----------------
class HealthView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})


# ---------------- SUBMIT ANSWER (StartGame) ----------------
@csrf_exempt
def submit_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        answer = data.get("answer", "").strip().lower()
        user_id = data.get("user_id")

        # ✅ Validation
        if not answer:
            return JsonResponse({"error": "Answer cannot be empty"}, status=400)

        # ✅ Programming Language Validation
        programming_languages = [
            'python', 'javascript', 'java', 'c', 'c++', 'cpp', 'c#', 'csharp',
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'typescript',
            'scala', 'perl', 'r', 'matlab', 'dart', 'lua', 'haskell',
            'objective-c', 'objectivec', 'shell', 'bash', 'powershell', 'sql',
            'html', 'css', 'xml', 'json', 'yaml', 'markdown', 'assembly',
            'fortran', 'cobol', 'lisp', 'scheme', 'elixir', 'erlang',
            'clojure', 'f#', 'fsharp', 'groovy', 'julia', 'racket', 'solidity',
            'vb', 'vba', 'pascal', 'ada', 'prolog', 'smalltalk', 'tcl',
            'ocaml', 'nim', 'crystal', 'zig', 'v', 'd'
        ]
        
        # Normalize the answer for comparison
        normalized_answer = answer.replace(' ', '').replace('-', '').replace('_', '')
        
        is_valid = any(
            normalized_answer == lang.replace(' ', '').replace('-', '').replace('_', '')
            for lang in programming_languages
        )
        
        if not is_valid:
            return JsonResponse({
                "error": "Only programming languages are allowed! Please enter a valid programming language."
            }, status=400)

        # Removed isalpha check to allow numbers/special chars if desired
        # if not answer.isalpha():
        #     return JsonResponse(
        #         {"error": "Only letters allowed. No special characters."},
        #         status=400
        #     )

        # ✅ CHECK IF USER ALREADY SUBMITTED
        # (Disabled: Users can submit multiple words)
        # if user_id:
        #     already_submitted = AnswerEvent.objects.filter(user_id=user_id).exists()
        #     if already_submitted:
        #         return JsonResponse(
        #             {"error": "You have already submitted a word. One submission only!"},
        #             status=400
        #         )

        # ✅ STORE IN WORD TABLE
        word, created = Word.objects.get_or_create(
            text=answer,
            defaults={"frequency": 1}
        )

        if not created:
            word.frequency += 1
            word.save()

        # ✅ RECORD SCORING EVENT
        if user_id:
            AnswerEvent.objects.create(
                user_id=user_id,
                question_id=1,  # Default or dynamic
                answer=answer
            )

        return JsonResponse({
            "success": True,
            "word": word.text,
            "frequency": word.frequency
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------- RECORD SHARE ----------------
@csrf_exempt
def record_share(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        platform = data.get("platform", "generic")

        if user_id:
            ShareEvent.objects.create(
                player_id=str(user_id),
                event_name=f"share_{platform}"
            )
            return JsonResponse({"success": True})
        
        return JsonResponse({"error": "Missing user_id"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------- WORD CLOUD ----------------
def get_wordcloud(request):
    try:
        words = Word.objects.all().order_by("-frequency")

        return JsonResponse({
            "words": [
                {
                    "text": w.text,
                    "frequency": w.frequency
                }
                for w in words
            ]
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_sample_wordcloud(request):
    """Get all words from WordCloudResponse table for sample cloud"""
    try:
        from django.db.models import Sum
        from .models import WordCloudResponse
        
        # Get top 500 unique words with their total count (sum of count field) from WordCloudResponse table
        word_data = (
            WordCloudResponse.objects
            .values('word')
            .annotate(frequency=Sum('count'))
            .order_by('-frequency')[:500]  # Get top 500 words
        )
        
        words = [
            {
                "text": item['word'],
                "frequency": item['frequency'] or 0
            }
            for item in word_data
        ]
        
        return JsonResponse({"words": words})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
