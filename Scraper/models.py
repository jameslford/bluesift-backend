from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class ScraperGroup(models.Model):
    limit = models.Q(
        app_label='SpecializedProducts',
        model='a'
        ) | models.Q(
        app_label='SpecializedProducts',
        model='b'
        ) | models.Q(
        app_label='SpecializedProducts',
        model='c'
        )
    manufacturer = models.CharField(max_length=60)
    category = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to=limit
    )