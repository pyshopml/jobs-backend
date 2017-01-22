from django.test import TestCase

from . import factories


class VacancyTestCase(TestCase):

    def test_string_representation(self):
        vacancy = factories.VacancyFactory.build()
        self.assertEqual(str(vacancy), vacancy.title)

    def test_absolute_url(self):
        v = factories.VacancyFactory.create()
        self.assertEqual(v.get_absolute_url(), '/vacancies/%s/' % v.pk)
