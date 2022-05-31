from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        for i in range(14):
            Post.objects.create(
                text=f'тестовый текст {i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_index_page_contains_ten_posts(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), settings.AMOUNT_POSTS
        )

    def test_group_list_contains_ten_posts(self):
        response = self.client.get(
            reverse('posts:group_list',
                    args=[PaginatorViewsTest.group.slug]))
        self.assertEqual(
            len(response.context['page_obj']), settings.AMOUNT_POSTS
        )

    def test_profile_contains_ten_posts(self):
        response = self.client.get(
            reverse('posts:profile',
                    args=[PaginatorViewsTest.user.username]))
        self.assertEqual(
            len(response.context['page_obj']), settings.AMOUNT_POSTS
        )
