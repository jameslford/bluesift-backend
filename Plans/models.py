# Plans.models.py

from django.db import models


class Plan(models.Model):
    CHOICES = (
        (0,'Free'),
        (1,'Premium'),
        (2,'Enterprise')
    )

    selection = models.SmallIntegerField(choices=CHOICES)