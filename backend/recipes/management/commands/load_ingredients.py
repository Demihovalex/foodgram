import json
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients from ingredients.json'

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), '../../../data/ingredients.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            obj, created = Ingredient.objects.get_or_create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
            if created:
                count += 1
        self.stdout.write(f'Загружено {count} ингредиентов')
