import datetime
from django.db import models

class PlanManager(models.Manager):

    def get_or_create_default(self):
        plan = self.model.objects.get_or_create(
            name='default',
            duration=datetime.timedelta(days=365),
            rate=0.00,
            billing_recurrence=datetime.timedelta(days=30)
            )[0]
        return plan


class Plan(models.Model):
    name = models.CharField(max_length=60, unique=True)
    duration = models.DurationField()
    billing_recurrence = models.DurationField()
    rate = models.DecimalField(max_digits=7, decimal_places=2)
    location_threshold = models.IntegerField(default=2)

    objects = PlanManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class ConsumerPlan(Plan):
    pass


class SupplierPlan(Plan):
    employee_limit = models.IntegerField(default=1)


# class ProPlan(Plan):
#     employee_limit = models.IntegerField(default=1)

