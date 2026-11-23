# Кулинарная книга — учебный проект на Django

## Запуск

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_categories      # справочник: Супы, Вторые блюда, Десерты, Напитки
python manage.py createsuperuser      # для входа в /admin/
python manage.py runserver
```

Откройте http://127.0.0.1:8000/ . Админка: http://127.0.0.1:8000/admin/
(через неё можно добавлять категории).

Проверка функционала:

```bash
python manage.py test recipes
```

## Структура

```
cookbook/          — проект (settings.py, urls.py)
recipes/           — приложение
  models.py        — Category, Recipe
  forms.py         — RecipeForm (ModelForm)
  views.py         — регистрация, список с фильтрами, CRUD, избранное
  urls.py          — маршруты
  admin.py         — регистрация моделей в админке
  management/commands/seed_categories.py — заполнение справочника
  templates/recipes/                     — base.html и 5 страниц
  tests.py         — 9 смоук-тестов
static/style.css   — оформление
```
