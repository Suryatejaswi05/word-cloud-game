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
                    'points': session.user.points,
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


class ApiQuestionsView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        questions = [
            "How are you feeling today?",
            "What is your favorite color?",
            "What motivates you the most?",
            "How was your day?",
            "What are you grateful for?",
            "What makes you happy?",
            "What is your biggest challenge?",
            "What are you looking forward to?",
            "How do you relax?",
            "What inspires you?",
        ]
        return JsonResponse({'questions': questions})


class ApiLogoutView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        session = _get_session(request)
        if session is None:
            return JsonResponse({'ok': True})

        session.revoked_at = timezone.now()
        session.save(update_fields=['revoked_at'])
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
