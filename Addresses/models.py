from django.conf import settings
# from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import googlemaps
from .choices import states

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


class CentroidManager(models.Manager):
    def get_centroid(self, code):
        coords = self.filter(code=code).first().centroid.point
        if coords:
            return coords
        else:
            return

class Zipcode(models.Model):
    code = models.CharField(max_length=5, unique=True)
    centroid = models.ForeignKey(Coordinate, on_delete=models.CASCADE)

    objects = CentroidManager()

    def __str__(self):
        return self.code

class Address(models.Model):
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120)
    country = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        default='United States of America'
        )
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=11)
    coordinates = models.ForeignKey(Coordinate, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.address_line_2:
            return '%s, %s, %s, %s, %s' % (self.address_line_1, self.address_line_2, self.city, self.state, self.postal_code)
        return '%s, %s, %s, %s' % (self.address_line_1, self.city, self.state, self.postal_code)

    def address_string(self):
        al1 = self.address_line_1
        al2 = self.address_line_2
        city = self.city
        state = self.state
        return f'{al1}, {city}, {state}, {self.postal_code}'

    def get_latlng(self):
        key = settings.GMAPS_API_KEY
        gmaps = googlemaps.Client(key=key)
        add = self.address_string()
        location = gmaps.geocode(add)[0]['geometry']['location']
        lat = location['lat']
        lng = location['lng']
        return [lat, lng]


    def save(self, *args, **kwargs):
        if not self.coordinates:
            lat_long = self.get_latlng()
            if lat_long:
                coordinate = Coordinate.objects.create(lat=lat_long[0], lng=lat_long[1])
                self.coordinates = coordinate
                super(Address, self).save(*args, **kwargs)
