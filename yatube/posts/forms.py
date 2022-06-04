from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
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
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Введите текст комментария',
                'class': 'form-control',
                'rows': 4,
                'cols': 20,
            }),
        }
