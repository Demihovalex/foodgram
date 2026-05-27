import json
import os
import sys

import django

from recipes.models import Ingredient

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()

file_path = "/app/fixtures/ingredients.json"

with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    Ingredient.objects.update_or_create(
        name=item["name"],
        defaults={"measurement_unit": item["measurement_unit"]},
    )

print(f"Загружено {len(data)} ингредиентов.")
