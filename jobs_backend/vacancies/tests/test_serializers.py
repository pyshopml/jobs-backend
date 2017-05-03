from unittest import TestCase

from jobs_backend.vacancies.serializers import SearchSerializer


class UserRetrieveSerializerTestCase(TestCase):
    def setUp(self):
        self.serializer_class = SearchSerializer

    def test_ok_expected_fields(self):
        data = {
            'phrase': 'test_phrase',
            'section': self.serializer_class.DESC
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.data
        self.assertCountEqual(data.keys(), ['phrase', 'section'])

    def test_fail_bad_choice(self):
        data = {
            'phrase': 'test_phrase',
            'section': 'another_choise'
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertFalse(bound_serializer.is_valid())

    def test_fail_lt_minlen_phrase(self):
        data = {
            'phrase': 'te',
            'section': 'another_choise'
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertFalse(bound_serializer.is_valid())

    def test_fail_gt_maxlen_phrase(self):
            data = {
                'phrase': 'test' * 6,
                'section': 'another_choise'
            }
            bound_serializer = self.serializer_class(data=data)
            self.assertFalse(bound_serializer.is_valid())
