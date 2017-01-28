from unittest import TestCase

from django.contrib.auth import get_user_model

from . import factories
from .. import serializers

User = get_user_model()


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

    def test_ok_valid_save(self):
        serializer = serializers.UserCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
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
