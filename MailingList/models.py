from django.db import models
from django.conf import settings

# Create your models here.
class MailingList(models.Model):
    name = models.CharField(max_length=60)


class Recipient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    email = models.EmailField()
    name = models.CharField(max_length=60)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.user:
            self.name = self.user.get_full_name()
            self.email = self.user.email
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
