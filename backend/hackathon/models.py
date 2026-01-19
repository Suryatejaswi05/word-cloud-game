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

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username


class AppUserMember(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='members')
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
