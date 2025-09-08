from django.urls import path
from .views import SignUpView , PhotoDoneAPIView , CustomTokenRefreshView

urlpatterns = [
    path('signup/' , SignUpView.as_view()),
    path('photo-done/', PhotoDoneAPIView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
]