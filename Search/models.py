from django.db import models


class SearchIndex(models.Model):
    name = models.CharField(max_length=60, unique=True)
    return_url = models.CharField(max_length=200)
    hash_value = models.CharField(max_length=2000)
