from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        # Call `create_user` to properly store hashed password
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.email= validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)

        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)

        instance.save()
        update_session_auth_hash(self.context.get('request'), instance)

        return instance
