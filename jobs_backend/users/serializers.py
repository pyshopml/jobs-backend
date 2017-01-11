from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator

from rest_framework import (
    exceptions,
    serializers,
)

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


class UserPasswordChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        instance.set_password(password)
        instance.save()

        update_session_auth_hash(self.context.get('request'), instance)

        return instance


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
