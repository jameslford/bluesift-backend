from django.conf import settings
from django.core.files.storage import FileSystemStorage


class LocalStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return name


def get_local_storage():
    if settings.ENVIRONMENT == 'local':
        return LocalStorage(location='D:\\BSData\\product_images')
    from .custom_storage import MediaStorage
    return MediaStorage
