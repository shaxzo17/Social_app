from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# from share.utilty import check_email_or_phone_number
from .models import CustomUser, CodeVerified, VIA_PHONE, PHOTO_DONE
# from django.core.mail import send_mail
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as JwtTokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings

class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status', 'phone_number']

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        code = user.create_verify_code(VIA_PHONE)
        # send_phone(user.phone, code)
        user.save()
        return user

    def validate_phone_number(self, data):
        if data and CustomUser.objects.filter(phone_number=data).exists():
            raise ValidationError('Bu telefon raqam mavjud')
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
    phone_number = serializers.CharField(write_only=True)
    # password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        # password = attrs.get("password")

        if not phone_number:
            raise ValidationError("Telefon raqam va parol kiritilishi shart!")

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise ValidationError("Bunday foydalanuvchi mavjud emas!")

        # if not user.check_password(password):
        #     raise ValidationError("Parol xato")

        tokens = user.token()

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }
