from django.test import TestCase

from . import factories


class UserTestCase(TestCase):

    def test_string_representation(self):
        user = factories.BaseUserFactory.build()
        self.assertEqual(str(user), user.email)

    def test_absolute_url(self):
        user = factories.BaseUserFactory.create()
        self.assertEqual(user.get_absolute_url(), '/users/%s/' % user.pk)
