# Plans.models.py

from django.db import models

class Plan(models.Model):

    TIERS = (
        (0,'Free'),
        (1,'Premium'),
        (2,'Enterprise')
        )
    tier = models.IntegerField(choices=TIERS, default=0)

