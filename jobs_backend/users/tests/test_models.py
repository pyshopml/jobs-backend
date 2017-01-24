from django.conf import settings
from django.core import mail
from django.test import TestCase

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
    pass
