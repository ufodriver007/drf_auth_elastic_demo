from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth.models import User
import time
import requests


class AuthenticateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='12345qwE')

    def test_jwt(self):
        data = {
            'username': 'test_user',
            'password': '12345qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/jwt/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_token(self):
        data = {
            'username': 'test_user',
            'password': '12345qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/token/login/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('auth_token' in response.data)


class UserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='12345qwE')
        data = {
            'username': 'test_user',
            'password': '12345qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/jwt/create/', data, format='json')
        jwt_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + jwt_token)

    def test_create(self):
        data = {
            'username': 'test_175_user',
            'password': '1227221qwE',
            're_password': '1227221qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/users/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('id' in response.data)

    def test_read(self):
        response = self.client.get('http://127.0.0.1:8000/auth/users/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('test_user', response.data['username'])

    def test_update(self):
        response = self.client.patch('http://127.0.0.1:8000/auth/users/me/', {'email': 'asdf@mail.ru'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('asdf@mail.ru', response.data['email'])

    def test_delete(self):
        response = self.client.delete('http://127.0.0.1:8000/auth/users/me/', {"current_password": '12345qwE'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class VKOAuthTest(TestCase):
    # http://127.0.0.1:8000/social-auth/login/vk-oauth2/ login page
    pass


class DocTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test_admin', password='1227221qwE')
        data = {
            'username': 'test_admin',
            'password': '1227221qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/jwt/create/', data, format='json')
        jwt_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + jwt_token)

    def test_authorized_access(self):
        response = self.client.get('http://127.0.0.1:8000/api/schema/swagger-ui/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_access(self):
        self.client.credentials()
        response = self.client.get('http://127.0.0.1:8000/api/schema/swagger-ui/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)


class UploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='1227221qwE')
        data = {
            'username': 'test_user',
            'password': '1227221qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/jwt/create/', data, format='json')
        jwt_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + jwt_token)

    def test_upload(self):
        test_file = SimpleUploadedFile(
            name='test_file.txt',
            content=b'This is a test file.',
            content_type='text/plain'
        )
        response = self.client.post('http://127.0.0.1:8000/upload/', {'file': test_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['result'] == 'success')

    def test_big_file_upload(self):
        test_file = SimpleUploadedFile(
            name='test_file.txt',
            content=b'This is a big test file.' * 100000,
            content_type='text/plain'
        )
        response = self.client.post('http://127.0.0.1:8000/upload/', {'file': test_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        self.assertTrue(response.data['result'] == 'fail. File is too big. You can upload file < 1Mb')


class ResultTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test_user', password='1227221qwE')
        data = {
            'username': 'test_user',
            'password': '1227221qwE'
        }
        response = self.client.post('http://127.0.0.1:8000/auth/jwt/create/', data, format='json')
        jwt_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + jwt_token)

    def test_upload_result(self):
        test_file = SimpleUploadedFile(
            name='test_file.txt',
            content=b'This is a test file.\nThis is a test file',
            content_type='text/plain'
        )
        response = self.client.post('http://127.0.0.1:8000/upload/', {'file': test_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['result'] == 'success')
        time.sleep(3)
        response = self.client.get('http://127.0.0.1:8000/result/')
        self.assertEqual(response.content, b'{"Download result":"2"}')


class SearchTest(TestCase):
    def test_search(self):
        response = requests.get('http://127.0.0.1:9200/file_index/_search/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
