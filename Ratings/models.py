from django.db import models
from django.conf import settings
from model_utils import Choices
from Profiles.models import CompanyShippingLocation
from Products.models import Product


class GenericRating(models.Model):
    RATING = Choices(1, 2, 3, 4, 5)
    rating = models.IntegerField(choices=RATING)
    review = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        abstract = True


class ProductRating(GenericRating):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_ratings")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ratings"
        )

    class Meta:
        unique_together = ('user', 'product')


class LocationRating(GenericRating):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="location_ratings"
        )
    location = models.ForeignKey(
        CompanyShippingLocation,
        on_delete=models.CASCADE,
        related_name="ratings"
        )

    class Meta:
        unique_together = ('user', 'location')
