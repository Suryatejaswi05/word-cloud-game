from django.db import models
from django.utils import timezone
import uuid
class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    current_question_index = models.IntegerField(default=0)
    questions = models.JSONField(default=list)  # Store question IDs
    is_active = models.BooleanField(default=True)
    
    def get_shareable_link(self):
        return f"/game/{self.id}/"
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

# hackathon/models.py
from django.db import models

class WordCloud(models.Model):
    word = models.CharField(max_length=100)  # Unique word
    freq = models.IntegerField(default=1)            # Frequency count
    
    def __str__(self):
        return f"{self.word}: {self.freq}"
    class Meta:
        managed = False
        db_table = 'wordcloud' 
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.TextField()

    class Meta:
        db_table = 'Questions'  # Match the table name


class UserAnswer(models.Model):
    user_id = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hackathon_useranswer'  # Match the table name


class WordFrequency(models.Model):
    word = models.CharField(max_length=50, primary_key=True)
    freq = models.IntegerField(default=1)

    class Meta:
        db_table = 'wordcloud'  # Your existing table name

from django.db import models
import uuid

class WordCloudRound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='word_cloud_rounds')
    created_by = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='created_rounds')
    share_token = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

class WordCloudResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word_cloud_round = models.ForeignKey(WordCloudRound, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='word_responses')
    response_word = models.CharField(max_length=255)
    augmented_words = models.JSONField(default=list)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

class WordFrequencyByRound(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word_cloud_round = models.ForeignKey(WordCloudRound, on_delete=models.CASCADE, related_name='word_frequencies')
    word = models.CharField(max_length=255)
    freq = models.IntegerField(default=1)

class ShareEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word_cloud_round = models.ForeignKey(WordCloudRound, on_delete=models.CASCADE, related_name='share_events')
    user = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='share_events')
    platform = models.CharField(max_length=50, default='copy')
    created_at = models.DateTimeField(default=timezone.now)

class RoundScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word_cloud_round = models.ForeignKey(WordCloudRound, on_delete=models.CASCADE, related_name='scores')
    player = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, related_name='round_scores')
    response_score = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
class UserScore(models.Model):
    user_id = models.IntegerField(primary_key=True)
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'hackathon_userscore'  # Match the table name