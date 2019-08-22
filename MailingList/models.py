from django.db import models


class EmailAddress(models.Model):
    email_address = models.EmailField()

    def __str__(self):
        return self.email_address


class MailingList(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email_addresses = models.ManyToManyField(EmailAddress, related_name='mailing_lists')

    def __str__(self):
        return self.name
