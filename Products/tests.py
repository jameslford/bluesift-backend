# Products.tests.py

from django.test import TestCase

from .models import Manufacturer, Product

class ProductModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        daltile = Manufacturer.objects.create()
        daltile.name = 'Daltile'
        grey_tile = Product.objects.create()
        grey_tile.name = 'Grey Tile'
        grey_tile.manufacturer = daltile


    def test_if_created(self):
        product = Product.objects.get(id=1)
        product_manu = product.manufacturer.name
        self.assertEqual(product.name, 'Grey Tile')
        self.assertEqual(product_manu, 'Daltile')
        