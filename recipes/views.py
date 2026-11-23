"""Представления приложения: регистрация, вход, список с фильтрами и CRUD.

Ключевое правило безопасности: каждый запрос к рецепту начинается с фильтра
``user=request.user`` (или ``queryset`` с таким фильтром). Чужие рецепты
не попадают ни в список, ни в формы, ни в удаление.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import RecipeForm
from .models import Category, Recipe


class RegisterView(CreateView):
    """Регистрация: логин, пароль и подтверждение пароля.

    Используется встроенная UserCreationForm — пароль хешируется Django.
    После успешной регистрации пользователь сразу авторизуется.
    """

    form_class = UserCreationForm
    template_name = 'recipes/register.html'
    success_url = reverse_lazy('recipe_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация завершена. Добро пожаловать!')
        return response


class RecipeListView(LoginRequiredMixin, ListView):
    """Главная страница: список рецептов текущего пользователя + фильтры."""

    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        # 1) Базовый набор — ТОЛЬКО рецепты вошедшего пользователя
        queryset = Recipe.objects.filter(user=self.request.user).select_related('category')

        # 2) Фильтр по категории (выпадающий список)
        category = self.request.GET.get('category')
        if category and category.isdigit():
            queryset = queryset.filter(category_id=int(category))

        # 3) Фильтр «только избранные»
        if self.request.GET.get('favorite') == '1':
            queryset = queryset.filter(is_favorite=True)

        # 4) Фильтр по времени приготовления «не больше N минут»
        max_time = self.request.GET.get('max_time')
        if max_time and max_time.isdigit():
            queryset = queryset.filter(cooking_time__lte=int(max_time))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['only_favorites'] = self.request.GET.get('favorite') == '1'
        context['max_time'] = self.request.GET.get('max_time', '')
        context['query_string'] = self.request.GET.urlencode()
        return context


class RecipeCreateView(LoginRequiredMixin, CreateView):
    """Добавление нового рецепта."""

    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'
    success_url = reverse_lazy('recipe_list')

    def form_valid(self, form):
        # Владелец подставляется сервером, а не из формы
        form.instance.user = self.request.user
        messages.success(self.request, 'Рецепт добавлен.')
        return super().form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рецепта. get_queryset закрывает доступ к чужим записям."""

    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'
    success_url = reverse_lazy('recipe_list')

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Рецепт обновлён.')
        return super().form_valid(form)


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рецепта после подтверждения."""

    model = Recipe
    template_name = 'recipes/recipe_confirm_delete.html'
    success_url = reverse_lazy('recipe_list')

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рецепт удалён.')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def toggle_favorite(request, pk):
    """Быстрое переключение признака «избранное» без редактирования рецепта."""
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
    recipe.is_favorite = not recipe.is_favorite
    recipe.save(update_fields=['is_favorite'])

    # Возвращаемся к списку, сохранив выбранные фильтры
    query = request.POST.get('query_string', '')
    url = str(reverse_lazy('recipe_list'))
    if query:
        url = f'{url}?{query}'
    return redirect(url)
