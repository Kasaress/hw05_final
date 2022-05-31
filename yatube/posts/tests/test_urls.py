from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostURLTests.user,
        )

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )

    def setUp(self):
        self.user_not_author = User.objects.create(username='TestNameNoAuthor')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_pages_for_everybody(self):
        """Проверяем доступность общедоступных страниц."""
        pages = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, status_code in pages.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.guest_client.get(address).status_code, status_code)

    def test_pages_for_authorized_user(self):
        """Проверяем доступность страниц для авторизованного пользователя."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_author_only(self):
        """Проверяем доступность редактирования поста автором."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect(self):
        """Проверяем недоступность создания поста без авторизации."""
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_pages_redirect(self):
        """Проверяем недоступность редактирования поста не автором."""
        response = self.authorized_client_not_author.get(
            f'/posts/{PostURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostURLTests.group
        user = PostURLTests.user
        post = PostURLTests.post
        templates_url = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user}/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            f'/posts/{post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for url, template in templates_url.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
