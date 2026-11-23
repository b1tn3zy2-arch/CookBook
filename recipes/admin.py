"""Регистрация моделей в админке (в том числе заполнение категорий)."""

from django.contrib import admin

from .models import Category, Recipe


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'cooking_time', 'is_favorite', 'user')
    list_filter = ('category', 'is_favorite')
    search_fields = ('title', 'user__username')
