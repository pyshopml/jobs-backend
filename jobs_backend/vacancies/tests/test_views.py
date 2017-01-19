from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from jobs_backend.vacancies.models import Vacancy
from . import factories

User = get_user_model()


class VacancyViewSetTestCase(APITestCase):

    def setUp(self):
        self.url_create = reverse('vacancies:vacancy-list')
        self.url_detail = reverse('vacancies:vacancy-detail', args=(1,))
        self.url_list = reverse('vacancies:vacancy-list')

        self.vacancies = factories.VacancyFactory.create_batch(2)

    def test_list_vacancies(self):
        response = self.client.get(self.url_list, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vacancy.objects.count(), 2)
        self.assertEqual(list(Vacancy.objects.all()), self.vacancies)

    def test_detail_vacancy(self):
        vacancy = Vacancy.objects.get(id=1)

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(vacancy.id, response.data.get('id'))
        self.assertEqual(vacancy.title, response.data.get('title'))
        self.assertEqual(vacancy.description, response.data.get('description'))

    def test_unauth_create_vacancy(self):
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}

        response = self.client.post(self.url_create, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vacancy.objects.count(), 2)

    # def test_auth_create_vacancy(self):
    #     url = reverse('vacancies:vacancy-list')
    #     data = {'title': 'awesome vacancy',
    #             'description': 'be awesome'}
    #
    #     # todo: как правильно создать юзера до авторизации?
    #     user = User.objects.count()
    #     print(user)
    #     self.client.login(username='user', password='pass')
    #
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Vacancy.objects.count(), 1)
