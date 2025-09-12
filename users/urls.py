from django.urls import path
from .views import SignUpView, PhotoDoneAPIView, CustomTokenRefreshView, LoginAPIView , VerifyCodeView
urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('signup/', SignUpView.as_view()),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),  # <-- shu qo‘shiladi
    path('photo-done/', PhotoDoneAPIView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
]
