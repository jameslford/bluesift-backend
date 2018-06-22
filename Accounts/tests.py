# Accounts.tests.py

from django.test import TestCase

from .models import User

class AccountModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_supplier(email='jim@gmail.com', first_name='jim', password='blahblah')

    def test_if_supplier(self):
        jim = User.objects.get(id=1)
        self.assertTrue(jim.is_supplier)


