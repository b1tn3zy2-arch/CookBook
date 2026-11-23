"""Смоук-тесты основного функционала."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Recipe

User = get_user_model()


class CookbookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Супы')
        cls.other_category = Category.objects.create(name='Десерты')
        cls.user = User.objects.create_user(username='cook', password='supersecret123')
        cls.other = User.objects.create_user(username='other', password='supersecret123')
        cls.recipe = Recipe.objects.create(
            title='Борщ',
            description='Сварить бульон, добавить овощи.',
            cooking_time=90,
            category=cls.category,
            user=cls.user,
        )

    def test_unauthorized_redirected_to_login(self):
        response = self.client.get(reverse('recipe_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_registration_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'HardPass123!',
            'password2': 'HardPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('recipe_list'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']),
                         User.objects.get(username='newuser').pk)

    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'cook', 'password': 'supersecret123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('recipe_list'))

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('login'))

    def test_create_recipe_sets_owner(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recipe_create'), {
            'title': 'Гаспачо',
            'category': self.category.pk,
            'cooking_time': 20,
            'is_favorite': 'on',
            'description': 'Взбить овощи.',
        })
        self.assertEqual(response.status_code, 302)
        recipe = Recipe.objects.get(title='Гаспачо')
        self.assertEqual(recipe.user, self.user)
        self.assertTrue(recipe.is_favorite)

    def test_update_and_delete(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('recipe_update', args=[self.recipe.pk]),
            {
                'title': 'Борщ с грибами',
                'category': self.category.pk,
                'cooking_time': 100,
                'description': 'Обновлённый рецепт.',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Борщ с грибами')

        response = self.client.post(reverse('recipe_delete', args=[self.recipe.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Recipe.objects.filter(pk=self.recipe.pk).exists())

    def test_favorite_toggle(self):
        self.client.force_login(self.user)
        url = reverse('recipe_favorite', args=[self.recipe.pk])
        self.client.post(url)
        self.recipe.refresh_from_db()
        self.assertTrue(self.recipe.is_favorite)
        self.client.post(url)
        self.recipe.refresh_from_db()
        self.assertFalse(self.recipe.is_favorite)

    def test_filters(self):
        Recipe.objects.create(
            title='Тирамису', description='Смешать.', cooking_time=40,
            category=self.other_category, user=self.user, is_favorite=True,
        )
        self.client.force_login(self.user)
        url = reverse('recipe_list')

        response = self.client.get(url, {'category': self.other_category.pk})
        self.assertEqual([r.title for r in response.context['recipes']], ['Тирамису'])

        response = self.client.get(url, {'favorite': '1'})
        self.assertEqual([r.title for r in response.context['recipes']], ['Тирамису'])
        self.assertEqual(response.context['total_count'], 1)

        response = self.client.get(url, {'max_time': '60'})
        self.assertEqual([r.title for r in response.context['recipes']], ['Тирамису'])

    def test_other_users_recipes_are_hidden(self):
        foreign = Recipe.objects.create(
            title='Чужой суп', description='Секрет.', cooking_time=10,
            category=self.category, user=self.other,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('recipe_list'))
        self.assertNotContains(response, 'Чужой суп')

        for name in ('recipe_update', 'recipe_delete'):
            response = self.client.get(reverse(name, args=[foreign.pk]))
            self.assertEqual(response.status_code, 404)

        response = self.client.post(reverse('recipe_favorite', args=[foreign.pk]))
        self.assertEqual(response.status_code, 404)
        foreign.refresh_from_db()
        self.assertFalse(foreign.is_favorite)
