import os
import csv
import random
import requests
from django.core.exceptions import ValidationError
from Addresses.models import Zipcode, Coordinate, Address

ADDRESS_URL = "https://raw.githubusercontent.com/EthanRBrown/rrad/master/addresses-us-all.min.json"


def add_zips():
    cwd = os.getcwd()
    if os.name == "nt":
        path = f"{cwd}\\config\\management\\zips\\zipcodes.csv"
    else:
        path = f"{cwd}/config/management/zips/zipcodes.csv"
    # print(path)
    with open(path) as readfile:
        reader = csv.reader(readfile, delimiter=",")
        for row in reader:
            ziptry = Zipcode.objects.filter(code=row[0]).first()
            if ziptry:
                continue
            coord = Coordinate.objects.create(lat=float(row[1]), lng=float(row[2]))
            Zipcode.objects.get_or_create(code=row[0], centroid=coord)


def generate_address_groups(maxnum=40):
    addresses = Address.objects.filter(demo=True)
    count = addresses.count()
    count = count if count < maxnum else maxnum
    addresses = random.sample(list(addresses), count)
    exclude_pks = []
    return_groups = []
    for address in addresses:
        if address.pk in exclude_pks:
            continue
        number = random.randint(2, 4)

        closest = address.find_closest_others()
        adds = []
        for _ in range(0, number):
            for close in closest:
                if close.pk in exclude_pks:
                    continue
                adds.append(close)
                exclude_pks.append(close.pk)
                break
        adds.append(address)
        exclude_pks.append(address.pk)
        return_groups.append(adds)
    print(return_groups)
    return return_groups


def create_addresses():
    if Zipcode.objects.all().count() < 33144:
        add_zips()
    addresses_response = requests.get(ADDRESS_URL).json()
    addresses = addresses_response.get("addresses", [])
    addresses = list(addresses)
    for address in addresses:
        address_1 = address.get("address1")
        address_2 = address.get("address2")
        city = address.get("city")
        state = address.get("state")
        postal_code = address.get("postalCode")
        try:
            return Address.objects.get_or_create_address(
                address_line_1=address_1,
                address_line_2=address_2,
                city=city,
                state=state,
                postal_code=postal_code,
                demo=True,
            )
        except (ValidationError, IndexError):
            print("bad addres")
            return None
