from django.contrib.auth import update_session_auth_hash


class PasswordChangeMixin(object):
    """
    Change password for user from request
    """
    def change_user_password(self, request, invalidate_sessions=False):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.data['new_password']
        request.user.set_password(new_password)
        request.user.save()

        if invalidate_sessions:
            update_session_auth_hash(request, serializer.user)
