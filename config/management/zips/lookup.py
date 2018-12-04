import csv
import os

def lookup(zipcode):
    path = os.getcwd() + '\\config\\management\\zips\\zipcodes.csv'
    zip_dic = {}
    with open(path) as readfile:
        reader = csv.reader(readfile, delimiter=",")
        for row in reader:
            zip_dic[row[0]] = [row[1], row[2]]
    return zip_dic[f'{zipcode}']

