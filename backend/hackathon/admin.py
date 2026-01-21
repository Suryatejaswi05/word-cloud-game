from django.contrib import admin
from .models import AppUser, AppUserMember, AuthSession, OtpChallenge, Hackathon, Submission, Question, GameRound, Response, ShareEvent

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'team_no', 'email', 'phone', 'is_active')

@admin.register(AppUserMember)
class AppUserMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'email', 'phone')

@admin.register(Hackathon)
class HackathonAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'hackathon', 'team', 'submitted_at')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_by', 'created_at')

@admin.register(GameRound)
class GameRoundAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'status', 'created_at')

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('round', 'player_id', 'word', 'is_augmented', 'submitted_at')

@admin.register(ShareEvent)
class ShareEventAdmin(admin.ModelAdmin):
    list_display = ('round', 'player_id', 'shared_at')
