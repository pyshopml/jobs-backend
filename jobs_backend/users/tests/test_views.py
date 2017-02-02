from django.core import mail
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from ..models import User
from . import factories


class UserViewSetTestCase(APITestCase):
    url_list = reverse('users:user-list')
    url_create = reverse('users:user-list')
    url_detail = 'users:user-detail'
    url_update = 'users:user-detail'

    def setUp(self):
        self.data = {
            'email': 'john.doe@example.com',
            'name': 'John Doe',
            'password': 'secret',
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_list_empty(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, list())

    def test_ok_list_sort_order(self):
        factories.ActiveUserFactory.create_batch(2)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertGreater(response.data[0]['id'], response.data[1]['id'])

    def test_ok_detail(self):
        user = factories.ActiveUserFactory.create()
        url = reverse(self.url_detail, args=[user.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['name'], user.name)

    def test_ok_detail_not_found(self):
        url = reverse(self.url_detail, args=[99])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ok_create(self):
        response = self.client.post(self.url_create, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], self.data['email'])
        self.assertEqual(response.data['name'], self.data['name'])

    def test_ok_create_without_name(self):
        del self.data['name']
        response = self.client.post(self.url_create, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '')

    def test_fail_create_without_required_field(self):
        for field in ['email', 'password']:
            with self.subTest(field=field):
                data = self.data.copy()
                del data[field]

                response = self.client.post(self.url_create, data)

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )
                self.assertIn(field, response.data)
                self.assertIn('required', response.data[field][0])

    def test_ok_create_activation_email(self):
        self.client.post(self.url_create, self.data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.data['email'], mail.outbox[0].to)
        self.assertIn('activation', mail.outbox[0].subject)

    def test_ok_update_name(self):
        user = factories.ActiveUserFactory.create()
        data = {
            'name': 'Jane Doe'
        }
        url = reverse(self.url_update, args=[user.pk])
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, data)
        self.assertTrue(User.objects.get(name='Jane Doe'))


class LoginViewTestCase(APITestCase):
    url = reverse('account:login')

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'email': self.user.email,
            'password': 'secret'
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_login(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_email(self):
        self.data['email'] = 'invalid@example.com'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_password(self):
        self.data['password'] = 'invalid'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_user_inactive(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTestCase(APITestCase):
    url_logout = reverse('account:logout')

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_successful_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url_logout)

        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(dict(self.client.session))

    def test_fail_not_auth(self):
        factories.ActiveUserFactory.create()
        response = self.client.post(self.url_logout)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PasswordChangeViewTestCase(APITestCase):
    url_login = reverse('account:login')
    url_pwd_change = reverse('account:password_change')

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'new_password': 'shadow',
            'new_password2': 'shadow',
            'current_password': 'secret',
        }

    def tearDown(self):
        User.objects.all().delete()

    def test_ok_successful_change(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url_pwd_change, self.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_fail_not_auth(self):
        self.assertFalse(dict(self.client.session))
        response = self.client.post(self.url_pwd_change, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fail_wrong_current_password(self):
        self.client.force_login(self.user)
        self.data['current_password'] = 'invalid'
        response = self.client.post(self.url_pwd_change, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('invalid', response.data['detail'])

    def test_fail_new_password_mismatch(self):
        self.client.force_login(self.user)
        self.data['new_password2'] = 'invalid'
        response = self.client.post(self.url_pwd_change, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_required_fields(self):
        for field in ['new_password', 'new_password2', 'current_password']:
            with self.subTest(field=field):
                self.client.force_login(self.user)
                data = self.data.copy()
                del data[field]

                response = self.client.post(self.url_pwd_change, data)

                self.assertEqual(
                    response.status_code, status.HTTP_400_BAD_REQUEST
                )
                self.assertIn(field, response.data)
                self.assertIn('required', response.data[field][0])


class PasswordResetViewTestCase(APITestCase):
    url = reverse('account:password_reset')

    def setUp(self):
        self.user = factories.ActiveUserFactory.create()
        self.data = {
            'email': self.user.email
        }

    def tearDown(self):
        pass

    def test_ok_successful_change(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.data['email'], mail.outbox[0].to)
        self.assertIn('password', mail.outbox[0].subject.lower())

    def test_fail_invalid_email(self):
        self.data['email'] = 'invalid@example.com'
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
