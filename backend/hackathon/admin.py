# Admin disabled temporarily to unblock server startup

from django.contrib import admin
from .models import (
    AppUser,
    AppUserMember,
    AuthSession,
    OtpChallenge,
    Question,
    GameSession,
    WordCloud,
    WordCloudRound,
    WordCloudResponse,
    WordFrequencyByRound,
    ShareEvent,
    RoundScore,
    UserScore,
)

admin.site.register(AppUser)
admin.site.register(AppUserMember)
admin.site.register(AuthSession)
admin.site.register(OtpChallenge)
admin.site.register(Question)
admin.site.register(GameSession)
admin.site.register(WordCloud)
admin.site.register(WordCloudRound)
admin.site.register(WordCloudResponse)
admin.site.register(WordFrequencyByRound)
admin.site.register(ShareEvent)
admin.site.register(RoundScore)
admin.site.register(UserScore)
