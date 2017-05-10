from unittest import TestCase

from django.db.models import Q
from django.test import TestCase as DjangoTestCase
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from . import factories
from ..serializers import (
    TagSerializer, CategorySerializer, VacancySerializer, SearchSerializer)
from ..models import Tag


class TagSerializerTestCase(DjangoTestCase):

    def setUp(self):
        self.tag = factories.TagFactory()
        self.serializer = TagSerializer(instance=self.tag)

    def test_ok_expected_value(self):
        data = self.serializer.data
        self.assertIsInstance(data, str)
        self.assertEqual(data, str(self.tag))


class CategorySerializerTestCase(DjangoTestCase):

    def setUp(self):
        self.category = factories.CategoryFactory()
        self.serializer = CategorySerializer(instance=self.category)

    def test_ok_expected_fields(self):
        data = self.serializer.data
        self.assertSetEqual(set(data.keys()), set(['id', 'parent', 'title']))

    def test_ok_expected_values(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.category.id)
        self.assertEqual(data['parent'], self.category.parent)
        self.assertEqual(data['title'], self.category.title)


class VacancySerializerTestCase(DjangoTestCase):

    def setUp(self):
        self.data = {
            'title': 'Python/Django backend developer',
            'description': 'We need you!!',
        }

        self.request = Request(APIRequestFactory().get('/'))

    def test_ok_expected_fields(self):
        vacancy = factories.VacancyFactory()
        serializer = VacancySerializer(instance=vacancy,
                                       context={'request': self.request})

        data = serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'url', 'title', 'description', 'salary_min',
             'salary_max', 'location', 'keywords', 'busyness',
             'remote_work', 'category', 'created_on', 'modified_on']
        )

    def test_ok_expected_values(self):
        vacancy = factories.VacancyFactory()
        serializer = VacancySerializer(instance=vacancy,
                                       context={'request': self.request})

        data = serializer.data
        self.assertEqual(data['id'], vacancy.id)
        self.assertEqual(data['title'], vacancy.title)
        self.assertEqual(data['description'], vacancy.description)
        self.assertEqual(data['salary_min'], vacancy.salary_min)
        self.assertEqual(data['salary_max'], vacancy.salary_max)
        self.assertDictEqual(data['location'], vacancy.location)
        self.assertCountEqual(data['keywords'], vacancy.keywords.all())
        self.assertEqual(data['busyness'], vacancy.busyness)
        self.assertEqual(data['remote_work'], vacancy.remote_work)
        self.assertEqual(data['category'], vacancy.category)
        self.assertEqual(
            data['created_on'],
            str(timezone.make_naive(vacancy.created_on).isoformat()) + 'Z')
        self.assertEqual(
            data['modified_on'],
            str(timezone.make_naive(vacancy.modified_on).isoformat()) + 'Z')

    def test_ok_create_keywords_exist(self):
        tag = factories.TagFactory()

        data = self.data.copy()
        data['keywords'] = [tag.title]

        serializer = VacancySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.all()[0].title, tag.title)

    def test_ok_create_keywords_new(self):
        data = self.data.copy()
        data['keywords'] = ['new']

        serializer = VacancySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(Tag.objects.all()[0].title, 'new')

    def test_ok_expected_category(self):
        category = factories.CategoryFactory()
        vacancy = factories.VacancyFactory(category=category)

        serializer = VacancySerializer(instance=vacancy,
                                       context={'request': self.request})

        data = serializer.data
        category_data = data['category']
        self.assertIsInstance(category_data, list)
        self.assertEqual(len(category_data), 1)
        self.assertEqual(category_data[0]['id'], category.id)
        self.assertEqual(category_data[0]['title'], category.title)

    def test_ok_expected_category_with_parent(self):
        category = factories.CategoryFactory()
        child_category = factories.CategoryFactory(parent=category)
        vacancy = factories.VacancyFactory(category=child_category)

        request = APIRequestFactory().get('/')
        context = {'request': request}
        serializer = VacancySerializer(instance=vacancy, context=context)

        data = serializer.data
        category_data = data['category']
        self.assertIsInstance(category_data, list)
        self.assertEqual(len(category_data), 2)
        self.assertEqual(category_data[0]['id'], child_category.id)
        self.assertEqual(category_data[1]['id'], category.id)

    def test_ok_create_existing_category(self):
        category = factories.CategoryFactory()

        data = self.data.copy()
        data['category'] = category.pk

        serializer = VacancySerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_ok_create_invalid_category(self):
        data = self.data.copy()
        data['category'] = 1

        serializer = VacancySerializer(data=data)

        self.assertTrue(serializer.is_valid())


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
