from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from jobs_backend.vacancies.models import Vacancy
from jobs_backend.users.tests.factories import ActiveUserFactory
from . import factories

User = get_user_model()


class VacancyViewSetTestCase(APITestCase):

    def setUp(self):
        self.url_create = 'vacancies:vacancy-list'
        self.url_detail = 'vacancies:vacancy-detail'
        self.url_list = 'vacancies:vacancy-list'

    def test_vacancies_list_empty(self):
        """
        If there are no vacancies we will get empty list
        """
        url = reverse(self.url_list)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, list())

    def test_list_vacancies(self):
        """
        Checks if have vacancies we should see them
        """
        factories.VacancyFactory.create_batch(2)
        url = reverse(self.url_list)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Vacancy.objects.count())

    def test_detail_vacancy(self):
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

    def test_detail_vacancy_not_found(self):
        """
        Getting message about non-existent vacancy
        """
        url = reverse(self.url_detail, args=(1,))

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Not found', response.data.get('detail', ''))

    def test_unauth_create_vacancy(self):
        """
        Attempt to create a vacancy without authorization
        """
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}
        url = reverse(self.url_create)
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vacancy.objects.count(), 0)

    def test_auth_create_vacancy(self):
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
        self.assertEqual(response.data.get('title'), 'awesome vacancy')
        self.assertEqual(response.data.get('description'), 'be awesome')
