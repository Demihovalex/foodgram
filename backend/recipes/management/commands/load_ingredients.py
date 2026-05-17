import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from JSON file'

    def handle(self, *args, **options):
        # Путь к файлу относительно папки backend (поднимаемся на уровень выше)
        file_path = '../data/ingredients.json'

        with open(file_path, 'r', encoding='utf-8') as file:
            ingredients = json.load(file)
            for item in ingredients:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS(
            f'Загружено {len(ingredients)} ингредиентов'))
