from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        cache.close()
        self.guest_client = Client()

    def test_pages_for_everybody(self):
        """Проверяем доступность страниц."""
        pages = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for address, status_code in pages.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.guest_client.get(address).status_code, status_code)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_about_page_uses_correct_template(self):
        """При запросах к именам приложения about используются
           корректные шаблоны."""
        templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
