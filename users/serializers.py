from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from share.sms_services import send_phone
from .models import CustomUser, CodeVerified, VIA_PHONE, PHOTO_DONE , CODE_VERIFIED
from rest_framework_simplejwt.serializers import TokenRefreshSerializer as JwtTokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'auth_type', 'auth_status', 'phone_number']

    def create(self, validated_data):
        user = super().create(validated_data)

        code = user.create_verify_code(VIA_PHONE)
        send_phone(user.phone_number, code)

        return user

    def validate_phone_number(self, data):
        if data and CustomUser.objects.filter(phone_number=data).exists():
            raise ValidationError('Bu telefon raqam mavjud')
        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(instance.token())
        return data


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, attrs):
        phone = attrs.get("phone_number")
        code = attrs.get("code")

        try:
            user = CustomUser.objects.get(phone_number=phone)
        except CustomUser.DoesNotExist:
            raise ValidationError("Bunday foydalanuvchi mavjud emas!")

        verify = CodeVerified.objects.filter(user=user, code=code, code_status=False).order_by('-id').first()
        if not verify:
            raise ValidationError("Kod noto‘g‘ri yoki eskirgan!")

        # Mark code as used
        verify.code_status = True
        verify.save(update_fields=["code_status"])

        # Update user status
        user.auth_status = CODE_VERIFIED  # constant from models
        user.save(update_fields=["auth_status"])

        return {
            "message": "Telefon raqam tasdiqlandi!",
            "tokens": user.token()
        }



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


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        if not phone_number:
            raise ValidationError("Telefon raqam kiritilishi shart!")

        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            raise ValidationError("Bunday foydalanuvchi mavjud emas!")

        if user.auth_status != CODE_VERIFIED:
            raise ValidationError("Telefon raqam hali tasdiqlanmagan!")

        tokens = user.token()
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"]
        }


class TokenRefreshSerializer(JwtTokenRefreshSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return data
