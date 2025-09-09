from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from share.utilty import check_email_or_phone_number
from .models import CustomUser, CodeVerified, VIA_EMAIL, VIA_PHONE , PHOTO_DONE
from django.core.mail import send_mail
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as JwtTokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status']

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_mail(
                subject="Tasdiqlash kodi",
                message=f"Sizning tasdiqlash kodingiz: {code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            # send_phone(user.phone, code)
        user.save()
        return user

    def validate(self, data):
        super().validate(data)
        data = self.auth_validate(data)
        return data

    def validate_email_phone_number(self, data):
        if data and CustomUser.objects.filter(email=data).exists():
            raise ValidationError("Bu email mavjud")
        elif data and CustomUser.objects.filter(phone_number=data).exists():
            raise ValidationError('Bu telefon raqam mavjud')
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        auth_type = check_email_or_phone_number(user_input)

        if auth_type == 'email':
            data = {
                'auth_type' : VIA_EMAIL,
                'email' : user_input
            }
        elif auth_type == 'phone_number':
            data = {
                'auth_type' : VIA_PHONE,
                'phone_number' : user_input
            }
        else:
            data = {
                'succes' : False,
                'msg' : 'Siz telefon raqam yoki email kiritishingiz kerak'
            }
            raise ValidationError(data)
        return data

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class PhotoDoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'photo', 'auth_status']

    def update(self, instance, validated_data):
        photo = validated_data.get('photo', None)
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save(update_fields=['photo', 'auth_status'])
        return instance



class TokenRefreshSerializer(JwtTokenRefreshSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return data


from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email_phone_number = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        user_input = attrs.get("email_phone_number")
        password = attrs.get("password")

        if not user_input or not password:
            raise ValidationError("Email/telefon va parol kiritilishi shart!")

        auth_type = check_email_or_phone_number(user_input)

        if auth_type == "email":
            kwargs = {"email": user_input.lower()}
        elif auth_type == "phone_number":
            kwargs = {"phone_number": user_input}
        else:
            raise ValidationError("Email yoki telefon raqam xato ")

        try:
            user = CustomUser.objects.get(**kwargs)
        except CustomUser.DoesNotExist:
            raise ValidationError("Bunday foydalanuvchi mavjud emas!")

        if not user.check_password(password):
            raise ValidationError("Parol xato")

        tokens = user.token()

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }
