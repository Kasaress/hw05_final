from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Введите текст поста',
                'class': 'form-control',
            }),
            'group': forms.Select(attrs={'class': 'form-control'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Текст комментария',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Введите текст комментария',
                'class': 'form-control',
                'rows': 4,
                'cols': 20,
            }),
        }
