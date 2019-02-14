# Plans.models.py

from django.db import models


class CustomerPlan(models.Model):
    name = models.CharField(max_length=60, unique=True)
    duration = models.DurationField()
    billing_recurrence = models.DurationField()
    rate = models.DecimalField(max_digits=7, decimal_places=2)
    project_threshold = models.IntegerField(default=2)

    def __str__(self):
        return self.name


class SupplierPlan(models.Model):
    name = models.CharField(max_length=60, unique=True)
    duration = models.DurationField()
    billing_recurrence = models.DurationField()
    rate = models.DecimalField(max_digits=7, decimal_places=2)
    location_threshold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
