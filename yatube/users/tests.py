from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User


class AboutTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_for_everybody(self):
        """Проверяем доступность страниц."""
        pages = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
        }
        for address, status_code in pages.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.guest_client.get(address).status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for url, template in templates_url.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_users_signup_accessible_by_name(self):
        """URL, генерируемый при помощи имени signup, доступен."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)

    def test_users_page_uses_correct_template(self):
        """При запросах к именам приложения users используются
           корректные шаблоны."""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_signup_show_correct_context(self):
        """Форма для логина пользователя передается правильно."""
        response = (self.guest_client.get(reverse('users:signup')))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_users_create_user(self):
        """Валидная форма signup создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тест',
            'last_name': 'Тестовый',
            'username': 'TestUserForms1',
            'email': 'bujhvh@mail.ru',
            'password1': '12345qwert_y',
            'password2': '12345qwert_y',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='TestUserForms1',
                email='bujhvh@mail.ru',
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:index'))
