"""
Addresses.models
    - Coordinate
    - Zipcode
    - Address

"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
import googlemaps


class Coordinate(models.Model):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    point = models.PointField(null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.lat and self.lng:
            self.point = Point(self.lng, self.lat)
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
            )

    class Meta:
        unique_together = ('lat', 'lng')

    def __str__(self):
        return str(self.lat) + ' ' + str(self.lng)


class CentroidManager(models.Manager):
    def get_centroid(self, code):
        coords = self.filter(code=code).first()
        if not coords:
            return None
        return coords.centroid.point


class Zipcode(models.Model):
    code = models.CharField(max_length=5, unique=True)
    centroid = models.ForeignKey(Coordinate, on_delete=models.CASCADE)

    objects = CentroidManager()

    def __str__(self):
        return self.code


class AddressManager(models.Manager):

    def get_or_create_address(self, **kwargs):

        def get_value(value: str, alt_response=None):
            for component in address_components:
                types = component.get('types')
                if not types:
                    continue
                if value in types:
                    return component['short_name']
                continue
            return alt_response

        gmap_id = kwargs.get('gmaps_id')
        street = kwargs.get('address_line_1')
        street_2 = kwargs.get('address_line_2')
        city = kwargs.get('city')
        state = kwargs.get('state')
        postal_code = kwargs.get('postal_code')
        response = None
        add_obj = self.model.objects.filter(gmaps_id=gmap_id).first() if gmap_id else None
        if add_obj:
            return add_obj
        gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
        if gmap_id:
            response = gmaps.reverse_geocode(self.gmaps_id)[0]
        else:
            address_string = f'{street} {street_2}, {city}, {state}, {postal_code}'
            response = gmaps.geocode(address_string)[0]

        gmap_id = response.get('place_id')
        add_obj = self.model.objects.filter(gmaps_id=gmap_id).first()
        if add_obj:
            return add_obj
        address_components = response.get('address_components')
        zipcode = get_value('postal_code', 0)
        postal_code = Zipcode.objects.filter(code=zipcode).first()
        if not postal_code:
            raise ValidationError('Invalid address')
        add_obj: Address = self.model()
        add_obj.gmaps_id = gmap_id
        add_obj.postal_code = postal_code
        lat = response['geometry']['location']['lat']
        lng = response['geometry']['location']['lng']
        coordinate = Coordinate.objects.filter(lat=lat, lng=lng).first()
        if not coordinate:
            coordinate = Coordinate.objects.create(lat=lat, lng=lng)
        add_obj.coordinates = coordinate
        street_number = get_value('street_number')
        route = get_value('route')
        add_obj.address_line_1 = f'{street_number} {route}'
        add_obj.state = get_value('administrative_area_level_1')
        add_obj.city = get_value('locality')
        add_obj.save()
        return add_obj


class Address(models.Model):
    address_line_1 = models.CharField(max_length=120)
    address_line_2 = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    gmaps_id = models.CharField(max_length=200, unique=True)
    address_string = models.CharField(max_length=1000, null=True, blank=True)
    lat = models.DecimalField(decimal_places=7, max_digits=13, null=True, blank=True)
    lng = models.DecimalField(decimal_places=7, max_digits=13, null=True, blank=True)
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

    demo = models.BooleanField(default=False)

    objects = AddressManager()

    def __str__(self):
        if self.address_string:
            return self.address_string
        return self.get_address_string()

    def get_short_name(self):
        if self.address_line_1:
            split = self.address_line_1.split(' ')
            if len(split) > 1:
                street_name = split[1]
        if self.city:
            return self.city


    def get_address_string(self):
        al1 = self.address_line_1
        al2 = self.address_line_2
        city = self.city
        state = self.state
        return f'{al1} {al2}, {city}, {state}, {self.postal_code}'

    def city_state(self):
        return f'{self.city}, {self.state}'

    def save(self, *args, **kwargs):
        self.lat = self.coordinates.lat
        self.lng = self.coordinates.lng
        self.address_string = self.get_address_string()
        super(Address, self).save(*args, **kwargs)
