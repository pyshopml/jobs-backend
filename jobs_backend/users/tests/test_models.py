from django.conf import settings
from django.core import mail
from django.test import TestCase

from ..models import User
from . import factories


class UserTestCase(TestCase):

    def setUp(self):
        self.user_obj = factories.BaseUserFactory.build()

    def test_string_representation(self):
        self.assertEqual(str(self.user_obj), self.user_obj.email)

    def test_absolute_url(self):
        user = factories.BaseUserFactory.create()
        self.assertEqual('/api/users/%s/' % user.pk, user.get_absolute_url())


    def test_get_full_name(self):
        self.assertEqual(self.user_obj.get_full_name(), self.user_obj.email)

    def test_get_short_name(self):
        self.assertEqual(self.user_obj.get_short_name(), self.user_obj.email)

    def test_email_user(self):
        envelope = {
            'subject': 'test subject',
            'message': 'test message',
        }
        self.user_obj.email_user(**envelope)

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject, envelope['subject'])
        self.assertEqual(mail.outbox[0].body, envelope['message'])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertIn(self.user_obj.email, mail.outbox[0].to)


class UserManagerTestCase(TestCase):

    def setUp(self):
        self.data = {
            'email': 'obi-wan.kenobi@example.com',
            'name': 'Obi-Wan Kenobi',
            'password': "These aren't the Droids your looking for",
        }

    def test_ok_common_create_user(self):
        user = User.objects._create_user(**self.data)

        self.assertIsInstance(user, User)
        self.assertTrue(user.pk)
        self.assertEqual(user.email, self.data['email'])
        self.assertEqual(user.name, self.data['name'])

        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(self.data['password']))

    def test_ok_common_create_user_without_name(self):
        del self.data['name']
        user = User.objects._create_user(**self.data)
        self.assertEqual(user.name, '')

    def test_fail_common_create_user_with_empty_email(self):
        self.data['email'] = ''
        self.assertRaises(ValueError, User.objects._create_user, **self.data)

    def test_ok_common_create_user_normalize_email(self):
        self.data['email'] = 'obi-wan.kenobi@ExAmPlE.cOm'
        user = User.objects._create_user(**self.data)
        self.assertEqual(user.email, 'obi-wan.kenobi@example.com')

    def test_ok_create_user(self):
        user = User.objects.create_user(**self.data)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)

    def test_fail_create_user_with_empty_password(self):
        del self.data['password']
        user = User.objects.create_user(**self.data)
        self.assertFalse(user.has_usable_password())

    def test_ok_create_superuser(self):
        user = User.objects.create_superuser(**self.data)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_fail_create_superuser_with_false_is_superuser(self):
        self.data['is_superuser'] = False
        self.assertRaises(
            ValueError, User.objects.create_superuser, **self.data
        )
