from django.db import models
from django.utils import timezone


class AppUser(models.Model):
    team_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=32, unique=True, null=True, blank=True)

    password_salt_b64 = models.CharField(max_length=64)
    password_hash_b64 = models.CharField(max_length=128)
    password_iterations = models.PositiveIntegerField()

    points = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username


class AppUserMember(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='members')
    member_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, null=True, blank=True)
    phone = models.CharField(max_length=32)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'phone'], name='uniq_member_phone_per_team'),
        ]
        indexes = [
            models.Index(fields=['user', 'phone']),
        ]

    def __str__(self) -> str:
        return f'{self.user.username}:{self.phone}'


class AuthSession(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='sessions')
    member = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='sessions', null=True, blank=True)
    token_hash = models.CharField(max_length=64, unique=True)

    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['member', 'expires_at']),
        ]

    def is_valid(self) -> bool:
        if self.revoked_at is not None:
            return False
        return self.expires_at > timezone.now()


class OtpChallenge(models.Model):
    identifier = models.CharField(max_length=255)
    member = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='otp_challenges', null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['identifier', 'expires_at']),
            models.Index(fields=['member', 'expires_at']),
            models.Index(fields=['expires_at']),
        ]

    def is_valid(self) -> bool:
        if self.consumed_at is not None:
            return False
        return self.expires_at > timezone.now()


class Hackathon(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Submission(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='submissions')
    team = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hackathon', 'team')

    def __str__(self) -> str:
        return f'{self.team.username}: {self.title}'


class Question(models.Model):
    text = models.TextField()
    created_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.text[:50]


class GameRound(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='rounds')
    created_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='rounds')
    share_token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('ended', 'Ended')], default='active')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'Round for {self.question.text[:30]}'


class Response(models.Model):
    round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='responses')
    player_id = models.CharField(max_length=255)  # Unique identifier for the player in this round
    word = models.CharField(max_length=100)
    is_augmented = models.BooleanField(default=False)  # True for programmatically added words
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('round', 'player_id')  # One response per player per round

    def __str__(self) -> str:
        return f'{self.player_id}: {self.word}'


class ShareEvent(models.Model):
    round = models.ForeignKey(GameRound, on_delete=models.CASCADE, related_name='share_events')
    player_id = models.CharField(max_length=255)
    shared_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f'Share by {self.player_id} for round {self.round.id}'
