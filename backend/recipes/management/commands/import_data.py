import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

PATH_TO_DATA = Path(BASE_DIR).resolve().joinpath("data") / "ingredients.csv"


class Command(BaseCommand):
    help = "Команда парсинга данных из .csv файла в БД."

    def handle(self, *args, **options):
        try:
            with open(PATH_TO_DATA, encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)

                for row in reader:
                    status, created = Ingredient.objects.update_or_create(
                        name=row[0], units=row[1]
                    )
            print("Парсинг успешно завершен.")

        except Exception as e:
            print(f"Парсинг завершился ошибкой: \n {e}")
