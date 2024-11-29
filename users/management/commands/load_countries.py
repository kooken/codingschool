import json
from django.core.management.base import BaseCommand
from users.models import Country


class Command(BaseCommand):
    help = 'Load countries from a JSON file into the database'

    def handle(self, *args, **kwargs):
        with open('countries.json', 'r') as f:
            countries_data = json.load(f)

        for country in countries_data:
            Country.objects.create(name=country['name'], code=country['code'])

        self.stdout.write(self.style.SUCCESS('Successfully loaded countries into the database'))
