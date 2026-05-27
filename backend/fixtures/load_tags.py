import json
import os
import sys

import django

from recipes.models import Tag

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")
django.setup()

file_path = "/app/fixtures/tags.json"

with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

count = 0
for item in data:
    obj, created = Tag.objects.update_or_create(
        slug=item["fields"]["slug"],
        defaults={"name": item["fields"]["name"]}
    )
    if created:
        count += 1
print(f"Загружено {count} тегов.")
