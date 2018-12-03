import decimal
import csv
import requests
import os
import random
import glob

from io import BytesIO
from django.conf import settings
from django.core import files
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand
from Products.models import Manufacturer, Category, Look, Material, Build, Product, Finish, Image


class Command(BaseCommand):

    def handle(self):
        data = os.getcwd() + '/config/management/zips/zipcodes.csv'
