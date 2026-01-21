from rest_framework import serializers
from django.core.mail import send_mail ,EmailMessage
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Validates and Create Users Email and Password and keeps is_active to False.
    The user must verify their email first to activate the account.
    """
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError({'confirmed_password': 'Passwords do not match'})
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password'],
            is_active=False
        )
        return user


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()



class EmailTokenObtainSerializer(TokenObtainPairSerializer):
    """allows user to use JWT login with email instead of username
    and prevents inactive users from login"""

    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = self.fields.pop('username')
        self.fields['email'].help_text = 'Email Adresse'

    """
    The email address is used as the username before authentication."""
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        attrs['username'] = email

        try:
            data = super().validate(attrs)
        except Exception:
            raise AuthenticationFailed('invalid login data.')
        if not self.user.is_active:
            raise AuthenticationFailed(
                'Account is not yet activated please check your emails.'
            )

        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset via email."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming and setting a new password."""
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)


    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({ "confirm_password": "passwords do not match"})

        try:
            validate_password(data['new_password'])
        except ValidationError as error:
            raise serializers.ValidationError({
                "new_password": list(error.messages)
            })

        return data