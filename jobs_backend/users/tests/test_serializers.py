import unittest

from . import factories
from .. import serializers


class UserRetrieveSerializerTest(unittest.TestCase):

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.serializer = serializers.UserRetrieveSerializer(instance=self.user)

    def test_ok_expected_fields(self):
        data = self.serializer.data

        self.assertCountEqual(data.keys(), ['id', 'email', 'name'])
