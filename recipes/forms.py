"""Формы на основе моделей (ModelForm)."""

from django import forms

from .models import Recipe


class RecipeForm(forms.ModelForm):
    """Форма добавления и редактирования рецепта.

    Поле user намеренно исключено: владелец подставляется в представлении
    из request.user, чтобы пользователь не мог назначить рецепт другому.
    """

    class Meta:
        model = Recipe
        fields = ['title', 'category', 'cooking_time', 'is_favorite', 'description']
        labels = {
            'title': 'Название блюда',
            'category': 'Категория',
            'cooking_time': 'Время приготовления (минут)',
            'is_favorite': 'Добавить в избранное',
            'description': 'Способ приготовления',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например, борщ'},),
            'cooking_time': forms.NumberInput(attrs={'min': 1, 'placeholder': '30'}),
            'description': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': '1. Подготовьте ингредиенты...\n2. ...',
            }),
        }
