from unittest import TestCase

from django.contrib.auth.tokens import default_token_generator
from django.test import RequestFactory
from rest_framework.exceptions import ParseError, AuthenticationFailed

from .. import serializers
from .. import utils
from ..models import User
from . import factories


class UserRetrieveSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.serializer = serializers.UserRetrieveSerializer(instance=self.user)

    def test_ok_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'email', 'name'])

    def test_ok_expected_values(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['name'], self.user.name)


class UserCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {
            'email': 'obi-wan.kenobi@example.com',
            'name': 'Obi-Wan Kenobi',
            'password': "These aren't the Droids your looking for",
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_valid_save(self):
        serializer = serializers.UserCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertNotIn('password', serializer.data)

    def test_ok_create(self):
        serializer = serializers.UserCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        user = serializer.create(serializer.validated_data)
        self.assertIsInstance(user, User)
        self.assertEqual(User.objects.count(), 1)

    def test_fail_required_field(self):
        """
        Checks serializer validation without required fields
        """
        for field in ['email', 'password']:
            with self.subTest(field=field):
                data = self.data.copy()
                del data[field]

                serializer = serializers.UserCreateSerializer(data=data)

                self.assertFalse(serializer.is_valid())

                self.assertIn(field, serializer.errors)
                self.assertIn('required', serializer.errors[field][0])

    def test_ok_optional_fields(self):
        del self.data['name']
        serializer = serializers.UserCreateSerializer(data=self.data)

        self.assertTrue(serializer.is_valid())
        self.assertNotIn('name', serializer.data)


class UserUpdateSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'name': 'Obi-Wan Kenobi'
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_change_name(self):
        serializer = serializers.UserUpdateSerializer(self.user, self.data)
        if serializer.is_valid():
            serializer.save()
            # Check that we have updated the existing object and not create new
            self.assertEqual(serializer.instance.pk, self.user.pk)
            self.assertEqual(serializer.data['name'], self.data['name'])


class UidTokenSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.BaseUserFactory.create()
        self.data = {
            'uid': utils.encode_uid(self.user.pk),
            'token': default_token_generator.make_token(self.user)
        }

    def test_ok_validate(self):
        serializer = serializers.UidTokenSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_fail_validate_uid(self):
        self.data['uid'] = utils.encode_uid(999)
        serializer = serializers.UidTokenSerializer(data=self.data)

        self.assertFalse(serializer.is_valid())
        self.assertIn(['Invalid UID'], serializer.errors.values())

    def test_fail_validate_token(self):
        self.data['token'] = 'aBcd-1234'
        serializer = serializers.UidTokenSerializer(data=self.data)

        self.assertFalse(serializer.is_valid())
        self.assertIn(['Invalid token'], serializer.errors.values())


class ActivationSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.BaseUserFactory.create()
        self.data = {
            'uid': utils.encode_uid(self.user.pk),
            'token': default_token_generator.make_token(self.user)
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_validate(self):
        serializer = serializers.ActivationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertDictEqual(serializer.data, self.data)

    def test_fail_validate(self):
        self.user.is_active = True
        self.user.save()
        serializer = serializers.ActivationSerializer(data=self.data)

        self.assertRaises(ParseError, serializer.is_valid)


class PasswordResetSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'email': self.user.email
        }

    def test_ok_validate_email(self):
        serializer = serializers.PasswordResetSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_fail_validate_email(self):
        self.user.is_active = False
        self.user.save()
        serializer = serializers.PasswordResetSerializer(data=self.data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class PasswordsIdentitySerializerTestCase(TestCase):

    def setUp(self):
        self.data = {
            'new_password': 'secret',
            'new_password2': 'secret'
        }

    def test_ok_validate(self):
        serializer = serializers.PasswordsIdentitySerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_fail_validate(self):
        self.data['new_password2'] = 'public'
        serializer = serializers.PasswordsIdentitySerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(serializer.validated_data, {})


class PasswordChangeSerializerTestCase(TestCase):

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'new_password': 'shadow',
            'new_password2': 'shadow',
            'current_password': 'secret',
        }
        self.rf = RequestFactory()
        self.req = self.rf.get('/')
        self.req.user = self.user

    def test_ok_current_password(self):
        serializer = serializers.PasswordChangeSerializer(data=self.data)
        serializer.context['request'] = self.req
        self.assertTrue(serializer.is_valid())

    def test_fail_current_password(self):
        self.data['current_password'] = 'public'
        serializer = serializers.PasswordChangeSerializer(data=self.data)
        serializer.context['request'] = self.req

        self.assertRaises(AuthenticationFailed, serializer.is_valid)
