"""
Addresses.models
    - Coordinate
    - Zipcode
    - Address

"""
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import googlemaps


class Coordinate(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    point = models.PointField(null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.lat and self.lng:
            self.point = Point(self.lat, self.lng)
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
            )

    class Meta:
        unique_together = ('lat', 'lng')


class CentroidManager(models.Manager):
    def get_centroid(self, code):
        coords = self.filter(code=code).first().centroid.point
        if coords:
            return coords


class Zipcode(models.Model):
    code = models.CharField(max_length=5, unique=True)
    centroid = models.ForeignKey(Coordinate, on_delete=models.CASCADE)

    objects = CentroidManager()

    def __str__(self):
        return self.code


class Address(models.Model):
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    gmaps_id = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        default='United States of America'
        )
    state = models.CharField(max_length=120)
    postal_code = models.ForeignKey(
        Zipcode,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='address'
        )
    coordinates = models.ForeignKey(
        Coordinate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )

    def __str__(self):
        if self.address_line_2:
            return '%s, %s, %s, %s, %s' % (
                self.address_line_1,
                self.address_line_2,
                self.city,
                self.state,
                self.postal_code
                )
        return '%s, %s, %s, %s' % (self.address_line_1, self.city, self.state, self.postal_code)

    def assign_google_response(self):
        response = self.get_gmaps_address()
        address_components = response.get('address_components')

        def get_value(value: str, alt_response=None):
            for component in address_components:
                types = component.get('types')
                if not types:
                    continue
                if value in types:
                    return component['short_name']
                continue
            return alt_response

        if not response:
            return False
        zipcode = get_value('postal_code', 0)
        postal_code = Zipcode.objects.filter(code=zipcode).first()
        if not postal_code:
            return False
        self.postal_code = postal_code
        lat = response['geometry']['location']['lat']
        lng = response['geometry']['location']['lng']
        coordinate = Coordinate.objects.filter(lat=lat, lng=lng).first()
        if not coordinate:
            coordinate = Coordinate.objects.create(lat=lat, lng=lng)
        self.coordinates = coordinate
        street_number = get_value('street_number')
        route = get_value('route')
        self.address_line_1 = f'{street_number} {route}'
        self.state = get_value('administrative_area_level_1')
        self.city = get_value('locality')
        return True

    def get_gmaps_address(self):
        gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
        response = None
        if self.gmaps_id:
            response = gmaps.reverse_geocode(self.gmaps_id)
        else:
            response = gmaps.geocode(self.address_string())
        if response:
            return response[0]

    def address_string(self):
        al1 = self.address_line_1
        city = self.city
        state = self.state
        return f'{al1}, {city}, {state}, {self.postal_code}'

    def city_state(self):
        return f'{self.city}, {self.state}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        passed = self.assign_google_response()
        if not passed:
            return None
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
