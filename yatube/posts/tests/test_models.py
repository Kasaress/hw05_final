
from django.conf import settings
from django.contrib.auth import get_user_model
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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            str(PostModelTest.post),
            PostModelTest.post.text[:settings.POST_TEXT_SHORT]
        )
        self.assertEqual(str(PostModelTest.group), 'Тестовая группа')

    def test_post_help_text(self):
        """help_text полей text и group модели post совпадает с ожидаемым."""
        help_text_text = PostModelTest.post._meta.get_field('text').help_text
        help_text_group = PostModelTest.post._meta.get_field('group').help_text
        self.assertEqual(help_text_text, 'Введите текст поста')
        self.assertEqual(help_text_group,
                         'Группа, к которой будет относиться пост')

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
