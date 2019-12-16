import boto3
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    bucket_name = settings.AWS_STATIC_BUCKET_NAME
    custom_domain = bucket_name + '.s3.amazonaws.com'


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    bucket_name = settings.AWS_MEDIA_BUCKET_NAME
    custom_domain = bucket_name + '.s3.amazonaws.com'

    @classmethod
    def base_path(cls):
        url_p = cls.url_protocol
        return f'https://{cls.custom_domain}/{cls.location}/'
