from django.urls import path

from .views import (
    ApiLoginView, ApiLogoutView, ApiMeView, ApiQuestionsView, ApiOtpRequestView, ApiOtpVerifyView, HealthView,
    ApiHackathonsView, ApiSubmissionsView, ApiCreateRoundView, ApiRoundDetailsView,
    ApiRespondView, ApiWordCloudView, ApiShareView, ApiLeaderboardView, ApiEndRoundView
)

urlpatterns = [
    path('', HealthView.as_view(), name='health'),
    path('api/login', ApiLoginView.as_view(), name='api_login'),
    path('api/otp/request', ApiOtpRequestView.as_view(), name='api_otp_request'),
    path('api/otp/verify', ApiOtpVerifyView.as_view(), name='api_otp_verify'),
    path('api/me', ApiMeView.as_view(), name='api_me'),
    path('api/questions', ApiQuestionsView.as_view(), name='api_questions'),
    path('api/logout', ApiLogoutView.as_view(), name='api_logout'),
    path('api/hackathons', ApiHackathonsView.as_view(), name='api_hackathons'),
    path('api/submissions', ApiSubmissionsView.as_view(), name='api_submissions'),
    path('api/create-round', ApiCreateRoundView.as_view(), name='api_create_round'),
    path('api/round/<int:round_id>', ApiRoundDetailsView.as_view(), name='api_round_details'),
    path('api/round/<int:round_id>/wordcloud', ApiWordCloudView.as_view(), name='api_wordcloud'),
    path('api/round/<int:round_id>/share', ApiShareView.as_view(), name='api_share'),
    path('api/round/<int:round_id>/leaderboard', ApiLeaderboardView.as_view(), name='api_leaderboard'),
    path('api/round/<int:round_id>/end', ApiEndRoundView.as_view(), name='api_end_round'),
    path('respond/<str:share_token>', ApiRespondView.as_view(), name='api_respond'),
]
