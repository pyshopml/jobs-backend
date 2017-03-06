from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator

from rest_framework import (
    exceptions,
    serializers,
)
from rest_framework.authtoken.models import Token

from . import utils
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for create new user
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Call `create_user` to properly store hashed password
        user = User.objects.create_user(**validated_data)
        return user


class UserRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieve user object(s)
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'name')


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for update user info
    """
    class Meta:
        model = User
        fields = ('name',)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'auth_failed': 'Invalid credentials or user account is inactive.'
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField()

    def validate(self, data):
        self.user = authenticate(username=data.get(User.USERNAME_FIELD),
                                 password=data.get('password'))
        if self.user is not None:
            return data
        else:
            raise serializers.ValidationError(
                self.error_messages['auth_failed'])


class AuthTokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = ('auth_token',)


class AuthTokenValidateSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')
    user = UserRetrieveSerializer(read_only=True)

    class Meta:
        model = Token
        fields = ('auth_token', 'user')

    default_error_messages = {
        'authtoken_invalid' : 'Invalid token'
    }

    def validate_auth_token(self, value):
        value = super(AuthTokenValidateSerializer, self).validate(value)
        self.token = Token.objects.filter(key=value).select_related('user')
        if not self.token:
            raise serializers.ValidationError(
                self.error_messages['authtoken_invalid'])
        return value

    def validate(self, data):
        data = super(AuthTokenValidateSerializer, self).validate(data)
        data['user'] = self.token[0].user
        return data


class UidTokenSerializer(serializers.Serializer):
    """
    Base UID and token serializer. Checks provided UID/token pair is valid
    """
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate_uid(self, value):
        try:
            uid = utils.decode_uid(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError('Invalid UID')
        return value

    def validate(self, data):
        data = super(UidTokenSerializer, self).validate(data)
        if not default_token_generator.check_token(self.user, data['token']):
            raise serializers.ValidationError('Invalid token')
        return data


class ActivationSerializer(UidTokenSerializer):
    """
    Checks UID/token pair is valid for activation
    """
    def validate(self, data):
        data = super(ActivationSerializer, self).validate(data)
        if self.user.is_active:
            err = 'UID/token pair is invalid or user already activated'
            raise exceptions.ParseError(err)
        return data


class PasswordResetSerializer(serializers.Serializer):
    """
    Checks registered active user with provided email
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError(
                'User with this email is not found')
        return value


class PasswordsIdentitySerializer(serializers.Serializer):
    """
    Checks new password
    """
    # todo: Add password complexity validation
    new_password = serializers.CharField()
    new_password2 = serializers.CharField()

    def validate(self, data):
        data = super(PasswordsIdentitySerializer, self).validate(data)
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError('Password mismatch')
        return data


class PasswordResetConfirmSerializer(UidTokenSerializer,
                                     PasswordsIdentitySerializer):
    """
    Password check during password reset
    """
    pass


class PasswordChangeSerializer(PasswordsIdentitySerializer):
    """
    Common password change serializer
    """
    current_password = serializers.CharField()

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise exceptions.AuthenticationFailed('Current password is invalid')
