from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from Addresses.models import Coordinate
from .tasks import send_danger_log_message



# Create your odels here.
class DangerLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='dangerLogs'
        )
    headers = JSONField(null=True)
    message = models.CharField(max_length=400)
    ip_address = models.CharField(max_length=200, null=True)
    session_id = models.CharField(max_length=120, null=True)
    base_path = models.CharField(max_length=200, null=True)
    path_params = models.CharField(max_length=300, null=True)
    location = models.ForeignKey(
        Coordinate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        send_danger_log_message.delay(self.pk)
        return
