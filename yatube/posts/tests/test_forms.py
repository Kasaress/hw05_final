import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import CommentForm, PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='slug2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostCreateFormTests.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.close()
        self.not_authorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост для формы',
            'group': PostCreateFormTests.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост для формы',
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group.pk,
                image='posts/small.gif',
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', args=[PostCreateFormTests.user.username]),
            HTTPStatus.FOUND)

    def test_not_create_post_not_authorizate(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост для формы',
            'group': PostCreateFormTests.group.pk,
        }
        response = self.not_authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            '/auth/login/?next=%2Fcreate%2F',
            HTTPStatus.FOUND)

    def test_edit_post(self):
        """Валидная форма редактирует запись Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост',
            'group': PostCreateFormTests.group2.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[PostCreateFormTests.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Отредактированный пост',
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group2.pk,
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст',
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group.pk,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[PostCreateFormTests.post.pk]))

    def test_not_edit_post_not_authorizate(self):
        """Неавторизованный пользователь не может редактировать пост."""
        form_data = {
            'text': 'Отредактированный пост',
            'group': PostCreateFormTests.group.pk,
        }
        self.not_authorized_client.post(
            reverse('posts:post_edit', args=[PostCreateFormTests.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(
                text='Отредактированный пост',
                author=PostCreateFormTests.user,
                group=PostCreateFormTests.group.pk,
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthorComment')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='testslug1',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.not_authorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentCreateFormTests.user)

    def test_create_comment(self):
        """Валидная форма создает комментарий"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий для формы',
            'author': CommentCreateFormTests.user,
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            args=[CommentCreateFormTests.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий для формы',
                author=CommentCreateFormTests.user,
            ).exists()
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[CommentCreateFormTests.post.pk]))

    def test_not_create_comment_not_authorizate(self):
        """Неавторизованный пользователь не может создать комментарий."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый пост для формы',
            'author': self.not_authorized_client,
        }
        self.not_authorized_client.post(
            reverse(
                'posts:add_comment',
                args=[CommentCreateFormTests.post.pk]),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
