"""Модели данных для приложения blog."""

from django.db import models
from django.contrib.auth import get_user_model


# Получение модели пользователя.
User = get_user_model()


class Location(models.Model):
    """Модель, описывающая местоположение."""

    name = models.CharField(
        'Название места',
        max_length=256
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        # Имена для использования в админ-зоне.
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель, описывающая категорию."""

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text="""Идентификатор страницы для URL;"""
        """ разрешены символы латиницы, цифры, дефис и подчёркивание."""
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        # Имена для использования в админ-зоне.
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель, описывающая пост в блоге."""

    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")
    image = models.ImageField(
        'Фото', upload_to='posts_images', blank=True
    )
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="""Если установить дату и время в будущем """
        """— можно делать отложенные публикации.""",
        # auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='locations',
        verbose_name='Местоположение',
        null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='categories',
        verbose_name='Категория',
        null=True,
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True
    )

    class Meta:
        # Имена для использования в админ-зоне.
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Mодель, описывающая комментарий в блоге."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        related_name='comments',
    )
    created_at = models.DateTimeField(
        verbose_name='Время создания',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text
