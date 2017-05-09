from django.test import TestCase

from . import factories


class VacancyTestCase(TestCase):

    def test_string_representation(self):
        vacancy = factories.VacancyFactory.build()
        self.assertEqual(str(vacancy), vacancy.title)

    def test_absolute_url(self):
        v = factories.VacancyFactory.create()
        self.assertEqual(v.get_absolute_url(), '/api/vacancies/%s/' % v.pk)

    def test_get_location(self):
        vacancy = factories.VacancyFactory.build()

        self.assertIsInstance(vacancy.location, dict)
        self.assertSetEqual(set(vacancy.location.keys()), set(('city', 'country',)))

    def test_ok_set_location(self):
        vacancy = factories.VacancyFactory.build()
        location_value = {'country': 'country', 'city': 'city'}

        vacancy.location = location_value

        self.assertDictEqual(location_value, vacancy.location)

    def test_ok_set_location_invalid_type(self):
        vacancy = factories.VacancyFactory.build()
        location_empty_value = vacancy.location
        location_value = ('country', 'city')

        vacancy.location = location_value

        self.assertDictEqual(location_empty_value, vacancy.location)

    def test_ok_set_location_expected_fields(self):
        vacancy = factories.VacancyFactory.build()
        location_empty_value = vacancy.location

        vacancy.location = {}

        self.assertDictEqual(location_empty_value, vacancy.location)
