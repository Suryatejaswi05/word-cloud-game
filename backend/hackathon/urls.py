# hackathon/urls.py
from django.urls import path
from django.urls import path
from .views import HealthView, submit_answer, get_wordcloud
from . import views
from .views import (
    # Health & Auth
    HealthView,
    ApiLoginView,
    ApiLogoutView,
    ApiMeView,
    ApiOtpRequestView,
    ApiOtpVerifyView,

    # Questions
    ApiQuestionsView,

    # Simple Word Cloud (USED BY StartGame + WordCloudPage)
    submit_answer,
    get_wordcloud,
    get_sample_wordcloud,
    get_user_score,

    # Optional: game / round features (keep if needed)
    create_game_session,
    join_shared_game,
)

urlpatterns = [
    # ---------------- HEALTH ----------------
    path("", HealthView.as_view(), name="health"),

    # ---------------- AUTH ----------------
    path("api/login", ApiLoginView.as_view()),
    path("api/logout", ApiLogoutView.as_view()),
    path("api/me", ApiMeView.as_view()),
    path("api/otp/request", ApiOtpRequestView.as_view()),
    path("api/otp/verify", ApiOtpVerifyView.as_view()),

    # ---------------- QUESTIONS ----------------
    path("api/questions", ApiQuestionsView.as_view()),

    # ---------------- WORD CLOUD (THIS IS THE IMPORTANT PART) ----------------
    path("api/submit-answer", submit_answer),   # 👈 StartGame writes here
    path("api/wordcloud", get_wordcloud),       # 👈 WordCloudPage reads here
    path("api/sample-wordcloud", get_sample_wordcloud),  # 👈 Sample cloud reads here
    path("api/user-score", get_user_score),
    path("api/record-share", views.record_share),

    # ---------------- OPTIONAL GAME ----------------
    path("api/game/create", create_game_session),
    path("api/game/<uuid:game_id>", join_shared_game),
    path("", HealthView.as_view()),
    path("api/submit-answer", submit_answer),
    path("api/wordcloud", get_wordcloud),
]
