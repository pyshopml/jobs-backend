from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

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
