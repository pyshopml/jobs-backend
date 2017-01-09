from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

from rest_framework import (
    mixins,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from . import serializers


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


class LoginView(views.APIView):

    def post(self, request, format=None):
        data = request.data

        email = data.get('email', None)
        password = data.get('password', None)

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                serialized = serializers.UserRetrieveSerializer(user)
                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):
    """
    With session-based auth requires to set
    `X-CSRFToken` header at HTTP-request
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
