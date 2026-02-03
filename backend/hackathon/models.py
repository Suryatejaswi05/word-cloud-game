from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class AppUser(models.Model):
    team_no = models.PositiveIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=32, unique=True, null=True, blank=True)
    
    # Password related fields (from 0001_initial)
    password_salt_b64 = models.CharField(max_length=64, default='')
    password_hash_b64 = models.CharField(max_length=128, default='')
    password_iterations = models.PositiveIntegerField(default=1000)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class AppUserMember(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='members')
    
    member_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=32)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'phone'], name='uniq_member_phone_per_team')
        ]

    def __str__(self):
        return self.name

class AuthSession(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    member = models.ForeignKey(AppUserMember, on_delete=models.CASCADE, null=True, blank=True)
    token_hash = models.CharField(max_length=255, unique=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session for {self.user}"

class OtpChallenge(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OTP for {self.phone}"


class Hackathon(models.Model):
    title = models.CharField(max_length=255, default='Hackathon')
    description = models.TextField(default='')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Submission(models.Model):
    hackathon = models.ForeignKey('Hackathon', on_delete=models.CASCADE)
    team = models.ForeignKey('AppUser', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255, default='Project')
    description = models.TextField(default='')
    github_url = models.URLField(null=True, blank=True)
    demo_url = models.URLField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_name


class Question(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions'
        managed = False  # Don't let Django manage this table

    def __str__(self):
        return self.text or "Question"


class UserAnswer(models.Model):
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    answer = models.CharField(max_length=255)

    class Meta:
        db_table = 'hackathon_useranswer'


class WordCloud(models.Model):
    word = models.CharField(max_length=50, primary_key=True)
    freq = models.IntegerField(default=1)

    class Meta:
        db_table = 'wordcloud'
        managed = False

    def __str__(self):
        return self.word
class WordCloudRound(models.Model):
    round_number = models.IntegerField(default=1)
    share_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Round {self.round_number}"


class WordCloudResponse(models.Model):
    round = models.ForeignKey('WordCloudRound', on_delete=models.CASCADE)
    word_cloud_round = models.ForeignKey('WordCloudRound', on_delete=models.CASCADE, related_name='responses', null=True, blank=True)
    word = models.CharField(max_length=100)
    count = models.IntegerField(default=1)
    player_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WordFrequencyByRound(models.Model):
    round = models.ForeignKey('WordCloudRound', on_delete=models.CASCADE)
    word = models.CharField(max_length=100, default='')
    frequency = models.IntegerField(default=0)


class ShareEvent(models.Model):
    event_name = models.CharField(max_length=100, null=True, blank=True)
    round = models.ForeignKey('GameRound', on_delete=models.CASCADE, null=True, blank=True)
    player_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)


class RoundScore(models.Model):
    round = models.ForeignKey('WordCloudRound', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    class Meta:
        db_table = 'hackathon_roundscore_v2'


class GameRound(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    share_token = models.CharField(max_length=255, unique=True, default='token')
    created_by = models.ForeignKey('AppUser', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Round {self.id} - {self.status}"


class Response(models.Model):
    round = models.ForeignKey('GameRound', on_delete=models.CASCADE)
    player_id = models.CharField(max_length=255, default='player')
    word = models.CharField(max_length=100, default='')
    is_augmented = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.word} by {self.player_id}"


class GameSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questions = models.JSONField(default=list)
    current_question_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game Session {self.id}"


class WordFrequency(models.Model):
    word = models.CharField(max_length=100, unique=True)
    freq = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.word} ({self.freq})"
class AnswerEvent(models.Model):
    user_id = models.IntegerField()
    question_id = models.IntegerField()
    answer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Word(models.Model):
    text = models.CharField(max_length=50, unique=True)
    frequency = models.IntegerField(default=1)

    class Meta:
        db_table = 'hackathon_word_v2'

    def __str__(self):
        return f"{self.text} ({self.frequency})"
