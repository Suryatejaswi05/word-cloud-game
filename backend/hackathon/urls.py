from django.urls import path
from .views import (
    create_word_cloud_round, get_round_details, submit_word_response,
    get_word_cloud_data, record_share_event, get_leaderboard, end_round
)
from .views import get_questions, submit_answer, get_wordcloud
from .views import ApiLoginView, ApiLogoutView, ApiMeView, ApiOtpRequestView, ApiOtpVerifyView, HealthView
from .views import join_shared_game,create_game_session
urlpatterns = [
    path('', HealthView.as_view(), name='health'),
    path('api/login', ApiLoginView.as_view(), name='api_login'),
    path('api/otp/request', ApiOtpRequestView.as_view(), name='api_otp_request'),
    path('api/otp/verify', ApiOtpVerifyView.as_view(), name='api_otp_verify'),
    path('api/me', ApiMeView.as_view(), name='api_me'),
    path('api/logout', ApiLogoutView.as_view(), name='api_logout'),
    path("api/questions/", get_questions),
    path("api/submit-answer/", submit_answer),  
    path("api/wordcloud/", get_wordcloud),
        # Word Cloud Game Routes
    path('api/game/create/', create_game_session, name='create_game'),
    path('api/game/<uuid:game_id>/', join_shared_game, name='join_game'),
    path('api/word-cloud/create/', create_word_cloud_round, name='create_word_cloud_round'),
    path('api/word-cloud/<str:share_token>/details/', get_round_details, name='get_round_details'),
    path('api/word-cloud/<str:share_token>/respond/', submit_word_response, name='submit_word_response'),
    path('api/word-cloud/<str:share_token>/data/', get_word_cloud_data, name='get_word_cloud_data'),
    path('api/word-cloud/<str:share_token>/share/', record_share_event, name='record_share_event'),
    path('api/word-cloud/<str:share_token>/leaderboard/', get_leaderboard, name='get_leaderboard'),
    path('api/word-cloud/<str:share_token>/end/', end_round, name='end_round'),
    path('api/wordcloud/',get_wordcloud, name='get_wordcloud'),
]
