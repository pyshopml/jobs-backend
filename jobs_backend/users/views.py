from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

from rest_framework import (
    generics,
    mixins,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .mixins import PasswordChangeMixin
from . import serializers
from . import utils


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-pk')
    serializer_class = serializers.UserRetrieveSerializer
    permission_classes = (AllowAny,)  # todo: Deal with permissions later

    def get_permissions(self):
        # todo: Implement later for ability to change only your account
        return super(UserViewSet, self).get_permissions()

    def get_serializer_class(self):
        """
        Decides which serializer to use
        """
        action = self.action
        if action == 'create':
            return serializers.UserCreateSerializer
        elif 'update' in action:
            return serializers.UserUpdateSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        user = serializer.save()

        mail = utils.UserActivationEmail(self.request, user)
        user.email_user(**dict(mail))


class LoginView(generics.GenericAPIView):
    """
    Authenticate active user.
    """
    serializer_class = serializers.LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        utils.login_user(request, user)
        return Response(
            data=serializers.UserRetrieveSerializer(user).data, # todo: change to token
            status=status.HTTP_200_OK,
        )


class LogoutView(views.APIView):
    """
    With session-based auth requires to set
    `X-CSRFToken` header at HTTP-request
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class PasswordChangeView(PasswordChangeMixin, generics.GenericAPIView):
    """
    Common password change view. Requires current password
    """
    serializer_class = serializers.PasswordChangeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        self.change_user_password(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetView(generics.GenericAPIView):
    """
    Sends password reset link to user's email
    """
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email, is_active=True)

        mail = utils.UserPasswordResetEmail(request, user)
        user.email_user(**dict(mail))

        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(PasswordChangeMixin, generics.GenericAPIView):
    """
    Resets password with new one
    """
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        self.change_user_password(request, invalidate_sessions=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivationView(generics.GenericAPIView):
    """
    Activates user account if provided UID/token pair is valid
    """
    serializer_class = serializers.ActivationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.is_active = True
        serializer.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
