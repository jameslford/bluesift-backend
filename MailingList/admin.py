from django.contrib import admin
from .models import MailingList, EmailAddress

admin.site.register(MailingList)
admin.site.register(EmailAddress)