from django.urls import path
from .views import SignUpView, PhotoDoneAPIView, CustomTokenRefreshView, LoginAPIView , VerifyCodeView , ForgotPasswordView , ResetPasswordView , UpdatePasswordView
urlpatterns = [
    path('login/', LoginAPIView.as_view()),
    path('signup/', SignUpView.as_view()),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),  # <-- shu qo‘shiladi
    path('photo-done/', PhotoDoneAPIView.as_view()),
    path('token/refresh/', CustomTokenRefreshView.as_view()),
    path("forgot-password/", ForgotPasswordView.as_view()),
    path("reset-password/", ResetPasswordView.as_view()),
    path("update-password/", UpdatePasswordView.as_view()),
]
