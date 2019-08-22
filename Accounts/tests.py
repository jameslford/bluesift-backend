# Accounts.tests.py

from django.test import TestCase

from .models import User

class AccountModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_supplier(email='jim@gmail.com', first_name='jim', password='blahblah')
        User.objects.create_user(email='claireford@gmail.com', password='blahblah')


    def test_if_supplier(self):
        jim = User.objects.get(id=1)
        self.assertTrue(jim.is_supplier)

    def test_if_add_lastname(self):
        jim = User.objects.get(id=1)
        jim.last_name = 'Ford'
        self.assertEqual(jim.last_name, 'Ford')

    def test_other_user(self):
        claire = User.objects.get(email='claireford@gmail.com')
        self.assertEqual(claire.get_first_name(), 'claireford@gmail.com')
