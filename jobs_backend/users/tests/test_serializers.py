from unittest import TestCase

from . import factories
from .. import serializers


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
