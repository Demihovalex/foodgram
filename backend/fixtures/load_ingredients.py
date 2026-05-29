import json
import os
import sys

import django

from recipes.models import Ingredient

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

django.setup()

file_path = '/app/fixtures/ingredients.json'

with open(file_path, encoding='utf-8') as f:
    data = json.load(f)

count = 0
for item in data:
    obj, created = Ingredient.objects.update_or_create(
        name=item['name'],
        defaults={'measurement_unit': item['measurement_unit']}
    )
    if created:
        count += 1

print(
    f'Загружено {count} ингредиентов '
    f'(всего в БД: {Ingredient.objects.count()})'
)
