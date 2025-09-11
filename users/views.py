from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import SignUpSerializer, PhotoDoneSerializer, TokenRefreshSerializer, LoginSerializer
from .models import CustomUser
from rest_framework.generics import ListCreateAPIView , UpdateAPIView
from rest_framework.permissions import AllowAny , IsAuthenticated

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


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
