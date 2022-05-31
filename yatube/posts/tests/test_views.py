import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestNameAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.small_gif2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded2 = SimpleUploadedFile(
            name='small2.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.small_gif3 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded3 = SimpleUploadedFile(
            name='small3.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostPagesTests.user,
            group=cls.group,
            image=cls.uploaded3,
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст2',
            author=PostPagesTests.user,
            group=cls.group,
            image=cls.uploaded2,
        )
        cls.user2 = User.objects.create(username='TestNameAuthor2')
        cls.group_for_user2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
        )
        cls.post_user2 = Post.objects.create(
            text='Тестовый текст3',
            author=PostPagesTests.user2,
            group=cls.group_for_user2,
            image=cls.uploaded,
        )
        cls.user3 = User.objects.create(username='TestNameAuthor3')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(PostPagesTests.user3)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        group = PostPagesTests.group
        user = PostPagesTests.user
        post = PostPagesTests.post
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[group.slug]): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[user.username]
            ): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[post.pk]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=[post.pk]): 'posts/create_post.html',
            reverse('posts:post_delete',
                    args=[post.pk]): 'posts/post_delete.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:index')))
        # Получаем первый пост из списка, переданного пагинатором
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = str(first_object.author)
        post_group_0 = str(first_object.group)
        post_image = str(first_object.image)
        post = PostPagesTests.post_user2
        # проверяем, что в контексте есть список постов
        self.assertIn('page_obj', response.context)
        # проверяем, что список постов действительно
        # относитеся к классу, отданному пагинатором
        self.assertIsInstance(
            response.context['page_obj'], Page)
        # проверяем равенство свойств поста,
        # полученного из контекста и поста из фикстур
        self.assertEqual(post_text_0, f'{post.text}')
        self.assertEqual(post_author_0, f'{post.author}')
        self.assertEqual(post_group_0, f'{post.group}')
        self.assertEqual(post_image, 'posts/small.gif')
        # проверяем, что у поста верная группа
        self.assertNotEqual(post_group_0, str(PostPagesTests.group))

    def test_post_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostPagesTests.group
        response = (self.authorized_client.get(reverse('posts:group_list',
                    args=[group.slug])))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group
        post_image = str(first_object.image)
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertEqual(post_image, 'posts/small2.gif')
        self.assertEqual(group, response.context['group'])
        self.assertEqual(post_group_0, response.context['group'])
        self.assertNotEqual(PostPagesTests.group_for_user2,
                            response.context['group'])

    def test_post_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        author = PostPagesTests.user
        response = (self.authorized_client.get(reverse('posts:profile',
                    args=[author.username])))
        first_object = response.context['page_obj'][0]
        post_group_0 = str(first_object.group)
        post_image = str(first_object.image)
        post = PostPagesTests.post
        # проверяем, что контекст, отправленный во вью, пришел и корректен
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertIn('posts', response.context)
        self.assertIn('posts_amount', response.context)
        self.assertEqual(post_image, 'posts/small2.gif')
        self.assertEqual(author.username, str(response.context['author']))
        self.assertNotEqual(PostPagesTests.user2,
                            first_object.author)
        self.assertNotEqual(PostPagesTests.group_for_user2,
                            post_group_0)
        self.assertEqual(post_group_0, f'{post.group}')

    def test_post_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = PostPagesTests.post
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    args=[post.pk])))
        self.assertIn('posts_amount', response.context)
        self.assertIn('title', response.context)
        self.assertEqual(post, response.context['post'])
        self.assertEqual(post.text, str(response.context['post']))
        self.assertEqual(post.image, 'posts/small3.gif')

    def test_post_edit_post_show_correct_context(self):
        """Шаблон create_post для редактирования поста сформирован
        с правильным контекстом."""
        post = PostPagesTests.post
        response = (self.authorized_client.get(reverse('posts:post_edit',
                    args=[post.pk])))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_post_show_correct_context(self):
        """Шаблон create_post для создания поста сформирован
        с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_index_cache(self):
        """Кэш на главной странице работает правильно."""
        # очищаем кэш
        cache.clear()
        # делаем первый запрос
        self.authorized_client.get(reverse('posts:index'))
        # создаем пост
        new_post = Post.objects.create(text="тестируем кэш",
                                       author=PostPagesTests.user)
        # делаем второй запрос
        response2 = self.authorized_client.get(reverse('posts:index'))
        # пост не должен появиться во втором запросе
        self.assertNotIn(new_post.text, response2.content.decode())
        # очищаем кэш
        cache.clear()
        # делаем третий запрос
        response3 = self.authorized_client.get(reverse('posts:index'))
        # проверяем, что пост есть в третьем запросе
        self.assertIn(new_post.text, response3.content.decode())

    def test_authorizate_can_follow(self):
        """ Авторизованный пользователь может подписаться на автора """
        # запросим количество подписок юзера
        follow_list_old = PostPagesTests.user.follower.count()
        # делаем запрос подписки от юзера на страницу автора юзер2
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[PostPagesTests.user2.username]))
        # снова запросим подписки юзера
        follow_list_new = PostPagesTests.user.follower.count()
        # сравним количество подписок
        self.assertEqual(follow_list_old + 1, follow_list_new)

    def test_authorizate_can_unfollow(self):
        """ Авторизованный пользователь может отписаться от автора."""
        # делаем запрос подписки от юзера на страницу автора юзер2
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[PostPagesTests.user2.username]))
        # запросим количество подписок юзера
        follow_list_old = PostPagesTests.user.follower.count()
        # делаем запрос отписки от юзера на страницу автора юзер2
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            args=[PostPagesTests.user2.username]))
        # снова запросим подписки юзера
        follow_list_new = PostPagesTests.user.follower.count()
        # сравним количество подписок
        self.assertEqual(follow_list_old, follow_list_new + 1)

    def test_follow_post(self):
        """Новая запись автора появляется в ленте подписчиков,
        и не появляется в ленте подписок не подписчиков"""
        # создаем подписку от юзера на юзера2
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[PostPagesTests.user2.username]))
        # считаем посты в ленте у юзера (подписан)
        response1 = (self.authorized_client.get(reverse('posts:follow_index')))
        post_list_old = len(response1.context['page_obj'])
        # считаем посты в ленте у юзера3 (не подписан)
        response2 = (self.authorized_client3.get(
            reverse('posts:follow_index')))
        post_list_unsubcribe_old = len(response2.context['page_obj'])
        # юзер2 создает новый пост
        Post.objects.create(
            text='Текс только для подписчиков',
            author=PostPagesTests.user2,
            group=PostPagesTests.group,
        )
        # считаем посты в ленте у юзера (подписан)
        response3 = (self.authorized_client.get(reverse('posts:follow_index')))
        post_list_new = len(response3.context['page_obj'])
        # считаем посты в ленте у юзера3 (не подписан)
        response4 = (self.authorized_client3.get(
            reverse('posts:follow_index')))
        post_list_unsubcribe_new = len(response4.context['page_obj'])
        # сравниваем
        self.assertEqual(post_list_old + 1, post_list_new)
        self.assertEqual(post_list_unsubcribe_old, post_list_unsubcribe_new)
