from django.conf import settings


def check_local():
    if settings.ENVIRONMENT != 'local':
        raise Exception('this operation can only be run on local machine')

def exclude_production():
    if settings.ENVIRONMENT == 'production':
        raise Exception('cannot run this command in production')
