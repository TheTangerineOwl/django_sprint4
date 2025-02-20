"""Формы для взаимодействия в блоге."""

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста в блоге."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
        }


class UserForm(forms.ModelForm):
    """Форма для профиля пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserRegistrationForm(UserCreationForm):
    """Форма для регистрации."""

    class Meta:
        model = User
        fields = ('username', 'email',)


class CommentForm(forms.ModelForm):
    """Форма для создания и редактирования комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
