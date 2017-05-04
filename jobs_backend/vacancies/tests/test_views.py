from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from jobs_backend.vacancies.models import Vacancy
from jobs_backend.users.tests.factories import ActiveUserFactory
from jobs_backend.vacancies.serializers import SearchSerializer
from . import factories


class VacancyViewSetTestCase(APITestCase):
    url_create = 'api:vacancies:vacancy-list'
    url_detail = 'api:vacancies:vacancy-detail'
    url_list = 'api:vacancies:vacancy-list'

    def test_ok_list_empty(self):
        """
        If there are no vacancies we will get empty list
        """
        url = reverse(self.url_list)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data.get('results', ''), list())

    def test_ok_list(self):
        """
        Checks if have vacancies we should see them
        """
        factories.VacancyFactory.create_batch(2)
        url = reverse(self.url_list)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('results', list())), Vacancy.objects.count())

    def test_ok_detail(self):
        """
        Checks retrieved data for existed vacancy object
        """
        obj = factories.VacancyFactory.create()
        url = reverse(self.url_detail, args=(obj.id,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), obj.id)
        self.assertEqual(response.data.get('title'), obj.title)
        self.assertEqual(response.data.get('description'), obj.description)

    def test_fail_detail_not_found(self):
        """
        Getting message about non-existent vacancy
        """
        url = reverse(self.url_detail, args=(1,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Not found', response.data.get('detail', ''))

    def test_fails_unauth_create(self):
        """
        Attempt to create a vacancy without authorization
        """
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}
        url = reverse(self.url_create)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vacancy.objects.count(), 0)

    def test_ok_auth_create(self):
        """
        Attempt to create a vacancy with authorization
        """
        url = reverse(self.url_create)
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}
        user = ActiveUserFactory.create()

        self.client.force_login(user)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vacancy.objects.count(), 1)
        self.assertEqual(response.data.get('title'), data['title'])
        self.assertEqual(response.data.get('description'), data['description'])


class SearchVacancyTestCase(APITestCase):
    search_url = 'api:vacancies:search'
    url = reverse(search_url)

    def setUp(self):
        self.batch_vac_count = 20
        self.vacancies = factories.VacancyFactory.create_batch(self.batch_vac_count)
        self.search_serializer = SearchSerializer

    def tearDown(self):
        Vacancy.objects.all().delete()

    def test_ok_search_1_vacancy_on_title(self):
        requested_title = self.vacancies[self.batch_vac_count - 1].title
        requested_description = self.vacancies[self.batch_vac_count - 1].description
        search_section = self.search_serializer.TITLE
        response = self.client.get(self.url, data={
            'phrase': requested_title,
            'section': search_section
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('title', ''), requested_title)
        self.assertEqual(results[0].get('description', ''), requested_description)

    def test_ok_search_1_vacancy_in_description(self):
        requested_title = self.vacancies[self.batch_vac_count - 1].title
        requested_description = self.vacancies[self.batch_vac_count - 1].description
        search_section = self.search_serializer.DESCRIPTION
        response = self.client.get(self.url, data={
            'phrase': requested_description,
            'section': search_section
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('title', ''), requested_title)
        self.assertEqual(results[0].get('description', ''), requested_description)

    def test_ok_search_2_vacancy_in_description_title(self):
        vac1 = Vacancy.objects.create(title='first', description='1st vacancy')
        vac2 = Vacancy.objects.create(title='second', description='2nd vacancy with first in desc')
        requested_phrase = vac1.title
        search_section = self.search_serializer.DESCRIPTION
        search_section2 = self.search_serializer.TITLE
        response = self.client.get(self.url, data={
            'phrase': requested_phrase,
            'section': [search_section, search_section2]
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].get('title', ''), requested_phrase)
        self.assertIn(requested_phrase, results[1].get('description', ''))

    def test_ok_search_1_vacancy_in_any_fields(self):
        requested_title = self.vacancies[self.batch_vac_count - 2].title
        requested_description = self.vacancies[self.batch_vac_count - 2].description
        search_section = self.search_serializer.ANY
        response = self.client.get(self.url, data={
            'phrase': requested_description,
            'section': search_section
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('title', ''), requested_title)
        self.assertEqual(results[0].get('description', ''), requested_description)
        response = self.client.get(self.url, data={
            'phrase': requested_title,
            'section': search_section
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get('title', ''), requested_title)
        self.assertEqual(results[0].get('description', ''), requested_description)

    def test_ok_search_20_vacancy_on_title(self):
        partial_phrase = 'title'
        search_section = self.search_serializer.ANY
        response = self.client.get(self.url, data={
            'phrase': partial_phrase,
            'section': search_section
        })
        expected_title1 = self.vacancies[0].title
        expected_title2 = self.vacancies[1].title
        results = response.data.get('results', list())
        self.assertEqual(len(results), 20)
        self.assertEqual(results[0].get('title', ''), expected_title1)
        self.assertEqual(results[1].get('title', ''), expected_title2)

    def test_ok_search_20_vacancy_on_description(self):
        partial_phrase = 'description'
        search_section = self.search_serializer.ANY
        response = self.client.get(self.url, data={
            'phrase': partial_phrase,
            'section': search_section
        })
        results = response.data.get('results', list())
        self.assertEqual(len(results), 20)

    def test_ok_no_results_on_fail_data(self):
        search_section = self.search_serializer.ANY
        response = self.client.get(self.url, data={
            'phrase': 'failed_phrase',
            'section': search_section
        })
        results = response.data.get('results', None)
        self.assertEqual(len(results), 0)

    def test_fail_on_fail_section(self):
        requested_title = self.vacancies[self.batch_vac_count - 2].title
        search_section = 'fail_section'
        response = self.client.get(self.url, data={
            'phrase': requested_title,
            'section': search_section
        })
        fail_section_results = response.data.get('section', None)
        self.assertEqual(response.status_code, 400)
        self.assertIn('"fail_section" is not a valid choice.', fail_section_results)

    def test_fail_on_absent_param_phrase(self):
        search_section = self.search_serializer.ANY
        response = self.client.get(self.url, data={
            'section': search_section
        })
        fail_param_results = response.data.get('phrase', None)
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field is required.', fail_param_results)

    def test_fail_on_absent_param_section(self):
        requested_title = self.vacancies[self.batch_vac_count - 1].title
        response = self.client.get(self.url, data={
            'phrase': requested_title
        })
        fail_section_results = response.data.get('section', None)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Choise search section must be set!', fail_section_results)
