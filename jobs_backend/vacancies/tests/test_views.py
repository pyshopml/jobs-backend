from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from jobs_backend.vacancies.models import Vacancy

User = get_user_model()


class VacancyViewSetTestCase(APITestCase):

    def test_unauth_create_vacancy(self):
        url = reverse('vacancies:vacancy-list')
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Vacancy.objects.count(), 0)

    def test_auth_create_vacancy(self):
        url = reverse('vacancies:vacancy-list')
        data = {'title': 'awesome vacancy',
                'description': 'be awesome'}

        # todo: как правильно создать юзера до авторизации?
        user = User.objects.count()
        print(user)
        self.client.login(username='user', password='pass')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vacancy.objects.count(), 1)
