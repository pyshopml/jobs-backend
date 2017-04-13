from django.contrib.auth import update_session_auth_hash

from .models import User
from . import utils


class PasswordChangeMixin(object):
    """
    Change password for user from request
    """
    def change_user_password(self, request, invalidate_sessions=False):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data.get('uid')
        if uid:
            uid = utils.decode_uid(uid)

        new_password = serializer.data['new_password']

        if request.user.is_authenticated():
            user = request.user
        else:
            user = User.objects.get(pk=uid, is_active=True)
        user.set_password(new_password)
        user.save()

        if invalidate_sessions:
            update_session_auth_hash(request, serializer.user)
