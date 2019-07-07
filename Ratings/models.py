from django.db import models
from django.conf import settings
from model_utils import Choices
from UserProductCollections.models import RetailerLocation
from Products.models import Product


class GenericRating(models.Model):
    RATING = Choices(1, 2, 3, 4, 5)
    rating = models.IntegerField(choices=RATING)
    review = models.TextField(max_length=1000, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        )

    class Meta:
        abstract = True


class ProductRating(GenericRating):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ratings"
        )

    class Meta:
        unique_together = ('user', 'product')


class LocationRating(GenericRating):
    location = models.ForeignKey(
        RetailerLocation,
        on_delete=models.CASCADE,
        related_name="ratings"
        )

    class Meta:
        unique_together = ('user', 'location')
