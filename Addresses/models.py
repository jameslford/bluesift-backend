from django.db import models
from .choices import states

class Address(models.Model):
    address_line_1      = models.CharField(max_length=120)
    address_line_2      = models.CharField(max_length=120, null=True, blank=True)
    city                = models.CharField(max_length=120)
    country             = models.CharField(max_length=120, default='United States of America')
    state               = models.CharField(max_length=120, choices=states)
    postal_code         = models.CharField(max_length=11)

    def __str__(self):
        if self.address_line_2:
            return '%s, %s, %s, %s, %s' % (self.address_line_1, self.address_line_2, self.city, self.state, self.postal_code)
        else:
            return '%s, %s, %s, %s' % (self.address_line_1, self.city, self.state, self.postal_code)
