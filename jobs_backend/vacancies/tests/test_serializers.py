from unittest import TestCase
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from jobs_backend.vacancies.serializers import SearchSerializer


class VacancySearchSerializerTestCase(TestCase):
    def setUp(self):
        self.serializer_class = SearchSerializer

    def test_ok_expected_fields(self):
        data = {
            'phrase': 'test_phrase',
            'section': [self.serializer_class.DESCRIPTION]
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.data
        self.assertCountEqual(data.keys(), ['phrase', 'section'])

    def test_ok_save_method_description_field(self):
        data = {
            'phrase': 'test_phrase',
            'section': [self.serializer_class.DESCRIPTION]
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.save()
        self.assertIsInstance(data, Q)
        self.assertEqual(Q.AND, data.connector)
        self.assertEqual(len(data.children), 1)
        self.assertEqual(data.children[0], ('description__icontains', 'test_phrase'))

    def test_ok_save_method_description_title_fields(self):
        data = {
            'phrase': 'test_phrase',
            'section': [self.serializer_class.DESCRIPTION, self.serializer_class.TITLE]
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.save()
        self.assertIsInstance(data, Q)
        self.assertEqual(Q.OR, data.connector)
        self.assertEqual(len(data.children), 2)
        self.assertIn(('description__icontains', 'test_phrase'), data.children)
        self.assertIn(('title__icontains', 'test_phrase'), data.children)

    def test_ok_save_method_any_param(self):
        data = {
            'phrase': 'test_phrase',
            'section': [self.serializer_class.ANY]
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.save()
        self.assertIsInstance(data, Q)
        self.assertEqual(Q.OR, data.connector)
        expected_nodes = (('{}__icontains'.format(field), 'test_phrase')
                          for field in self.serializer_class.search_sections)
        redunrant_fields = set(expected_nodes) ^ set(data.children)
        self.assertSetEqual(set(), redunrant_fields)

    def test_ok_save_method_any_param_and_another_fields(self):
        data = {
            'phrase': 'test_phrase',
            'section': [self.serializer_class.ANY, self.serializer_class.DESCRIPTION, self.serializer_class.TITLE]
        }
        bound_serializer = self.serializer_class(data=data)
        self.assertTrue(bound_serializer.is_valid())
        data = bound_serializer.save()
        self.assertIsInstance(data, Q)
        self.assertEqual(Q.OR, data.connector)
        expected_nodes = (('{}__icontains'.format(field), 'test_phrase')
                          for field in self.serializer_class.search_sections)
        redunrant_fields = set(expected_nodes) ^ set(data.children)
        self.assertSetEqual(set(), redunrant_fields)

    def test_fail_bad_choice(self):
        data = {
            'phrase': 'test_phrase',
            'section': ['another_choise']
        }
        bound_serializer = self.serializer_class(data=data)
        with self.assertRaises(ValidationError) as exc:
            bound_serializer.is_valid(raise_exception=True)
        self.assertTrue('"another_choise" is not a valid choice.' in exc.exception.detail.get('section', ''))

    def test_fail_lt_minlen_phrase(self):
        data = {
            'phrase': 'te',
            'section': [SearchSerializer.ANY]
        }
        bound_serializer = self.serializer_class(data=data)
        with self.assertRaises(ValidationError) as exc:
            bound_serializer.is_valid(raise_exception=True)
        self.assertTrue('Ensure this field has at least 3 characters.' in exc.exception.detail.get('phrase', ''))

    def test_fail_gt_maxlen_phrase(self):
        data = {
            'phrase': 'test' * 20,
            'section': [SearchSerializer.ANY]
        }
        bound_serializer = self.serializer_class(data=data)
        with self.assertRaises(ValidationError) as exc:
            bound_serializer.is_valid(raise_exception=True)
        self.assertTrue('Ensure this field has no more than 50 characters.' in exc.exception.detail.get('phrase', ''))

    def test_fail_no_section_field(self):
        data = {
            'phrase': 'test' * 6,
        }
        bound_serializer = self.serializer_class(data=data)
        with self.assertRaises(ValidationError) as exc:
            bound_serializer.is_valid(raise_exception=True)
        self.assertTrue('This field is required.' in exc.exception.detail.get('section', ''))

