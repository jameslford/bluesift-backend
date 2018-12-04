import csv
import os
from django.conf import settings

def lookup(zipcode):
    path = settings.ZIP_PATH
    zip_dic = {}
    with open(path) as readfile:
        reader = csv.reader(readfile, delimiter=",")
        for row in reader:
            zip_dic[row[0]] = [row[1], row[2]]
    return zip_dic[f'{zipcode}']
