"""Создание стартовых категорий: python manage.py seed_categories."""

from django.core.management.base import BaseCommand

from recipes.models import Category

CATEGORY_NAMES = ['Супы', 'Вторые блюда', 'Десерты', 'Напитки']


class Command(BaseCommand):
    help = 'Создаёт справочник категорий (дубли не создаются)'

    def handle(self, *args, **options):
        created = 0
        for name in CATEGORY_NAMES:
            _, was_created = Category.objects.get_or_create(name=name)
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Категории готовы. Новых: {created}. Всего: {Category.objects.count()}'
        ))
