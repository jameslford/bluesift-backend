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

    def handle(self, *args, **options):
        path = os.getcwd() + '\\config\\management\\zips\\zipcodes.csv'
        # print(path)
        zip_dic = {}
        with open(path) as readfile:
            reader = csv.reader(readfile, delimiter=",")
            for row in reader:
                zip_dic[row[0]] = [row[1], row[2]]
        print(zip_dic['30319'])
