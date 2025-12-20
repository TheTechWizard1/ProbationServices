# api/management/commands/cleanup.py
from django.core.management.base import BaseCommand
from api.models import Product, Order, OrderItem

class Command(BaseCommand):
    help = 'Deletes all data from Product, Order, and OrderItem models'

    def handle(self, *args, **options):
        self.stdout.write("Deleting old data...")
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted old data.'))
