"""Регистрация моделей приложения blog в админ-зоне."""

from django.contrib import admin

from .models import Location
from .models import Category
from .models import Post

admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Post)
