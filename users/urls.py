from django.urls import path
from .views import SignUpView, PhotoDoneAPIView, CustomTokenRefreshView, LoginAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('signup/', SignUpView.as_view()),
    path('photo-done/', PhotoDoneAPIView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
]
