from django.conf import settings
from django.db import models
import googlemaps
from .choices import states


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
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        if self.address_line_2:
            return '%s, %s, %s, %s, %s' % (self.address_line_1, self.address_line_2, self.city, self.state, self.postal_code)
        else:
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
        if not self.lat:
            lat_long = self.get_latlng()
            if lat_long:
                self.lat = lat_long[0]
                self.lng = lat_long[1]
                super(Address, self).save(*args, **kwargs)
