# Products.tests.py

from django.test import TestCase

from .models import Manufacturer, Product

class ProductModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        daltile = Manufacturer.objects.create()
        daltile.name = 'Daltile'
        GT = Product.objects.create()
        GT.name = 'Grey Tile'
        GT.manufacturer = daltile
        
        
    def test_if_created(self):
        product = Product.objects.get(id=1)
        productManu = Product.manufacturer.name
        self.assertEqual(product.name, 'Grey Tile')
        self.assertEqual(productManu,'Daltile')
        