from django.test import TestCase

from . import factories


class TagTestCase(TestCase):

    def test_string_representation(self):
        tag = factories.TagFactory.build()
        self.assertEqual(str(tag), tag.title)


class CategoryTestCase(TestCase):

    def test_string_representation(self):
        category = factories.CategoryFactory.build()
        self.assertEqual(str(category), category.title)


class VacancyTestCase(TestCase):

    def test_string_representation(self):
        vacancy = factories.VacancyFactory.build()
        self.assertEqual(str(vacancy), vacancy.title)

    def test_absolute_url(self):
        v = factories.VacancyFactory.create()
        self.assertEqual(v.get_absolute_url(), '/api/vacancies/%s/' % v.pk)
