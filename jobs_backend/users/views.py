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
    Authenticate active user. Returns authentication token.

    To make authorized requests use it in HTTP header:
    `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
    """
    serializer_class = serializers.LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        auth_token = utils.login_user(request, user)

        return Response(
            data=serializers.AuthTokenSerializer(auth_token).data,
            status=status.HTTP_200_OK,
        )


class LogoutView(views.APIView):
    """
    Session: Requires to set `X-CSRFToken` header at HTTP-request\n
    Token: Send authorized POST with HTTP header:
        `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        utils.logout_user(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class AuthTokenValidationView(generics.GenericAPIView):
    """
    Validates auth token. Returns user info if token is valid.
    """
    serializer_class = serializers.AuthTokenValidateSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
