"""Конфигурация приложения blog."""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    # Имя для использования в админ-зоне.
    verbose_name = 'Блог'
