
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый постаментище',
        )

    def setUp(self):
        cache.close()

    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели корректно работает __str__."""
        strs = (
            (str(PostModelTest.post),
                PostModelTest.post.text[:settings.POST_TEXT_SHORT]),
            (str(PostModelTest.group), 'Тестовая группа'),
        )
        for model_str, test_str in strs:
            with self.subTest():
                self.assertEqual(model_str, test_str)

    def test_post_names(self):
        """Help_text полей модели post совпадает с ожидаемым."""
        help_texts = (
            (PostModelTest.post._meta.get_field('text').help_text,
                'Введите текст поста'),
            (PostModelTest.post._meta.get_field('group').help_text,
                'Группа, к которой будет относиться пост'),
        )
        for model_name, test_name in help_texts:
            with self.subTest():
                self.assertEqual(model_name, test_name)

    def test_post_verbose_name(self):
        """verbose_name всех полей модели post совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Опубликовано',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_group_verbose_name(self):
        """verbose_name всех полей модели group совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Группа',
            'slug': 'Адрес группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(field).verbose_name,
                    expected_value)
