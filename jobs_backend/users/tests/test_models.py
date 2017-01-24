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
        self.assertEqual(user.get_absolute_url(), '/users/%s/' % user.pk)

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

        self.assertTrue(user.pk)
        self.assertEqual(user.email, self.data['email'])
        self.assertEqual(user.name, self.data['name'])

        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password(self.data['password']))

    def test_fail_common_create_user_with_empty_email(self):
        self.data['email'] = ''
        self.assertRaises(ValueError, User.objects._create_user, **self.data)

    def test_ok_common_create_user_normalize_email(self):
        self.data['email'] = 'obi-wan.kenobi@ExAmPlE.cOm'
        user = User.objects._create_user(**self.data)
        self.assertEqual(user.email, 'obi-wan.kenobi@example.com')
