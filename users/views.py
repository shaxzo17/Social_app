from django.shortcuts import render
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import SignUpSerializer , PhotoDoneSerializer , TokenRefreshSerializer
from .models import CustomUser
from rest_framework.generics import ListCreateAPIView , UpdateAPIView
from rest_framework.permissions import AllowAny , IsAuthenticated

# Create your views here.

class SignUpView(ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny , ]


class PhotoDoneAPIView(UpdateAPIView):
    serializer_class = PhotoDoneSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
