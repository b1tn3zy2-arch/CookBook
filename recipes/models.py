"""Модели данных приложения «Рецепты»."""

from django.conf import settings
from django.db import models


class Category(models.Model):
    """Справочник категорий. Заполняется через админку Django."""

    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт, принадлежащий конкретному пользователю."""

    title = models.CharField('Название блюда', max_length=200)
    description = models.TextField('Способ приготовления')
    cooking_time = models.PositiveIntegerField('Время приготовления, мин')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='recipes',
    )
    is_favorite = models.BooleanField('Избранное', default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='recipes',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        # Сначала избранные, затем по названию
        ordering = ['-is_favorite', 'title']

    def __str__(self):
        return self.title
