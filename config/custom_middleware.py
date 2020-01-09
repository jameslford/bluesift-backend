
import json
from ipware import get_client_ip
from django.conf import settings
from django.http import JsonResponse, HttpRequest
# from rest_framework.request import Request
from rest_framework.authtoken.models import Token
from .tasks import harvest_request

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False

class StagingMiddleware:
    """
    Keeps random users from being able to look at staging data
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('request_received')
        if settings.ENVIRONMENT != 'staging':
            return self.get_response(request)
        safe_urls = ['accounts/login', 'landing', 'admin', 'get-demo']
        if any(safe in request.path for safe in safe_urls):
            return self.get_response(request)
        header_token = request.META.get('HTTP_AUTHORIZATION', None)
        if header_token is not None:
            try:
                token = header_token.replace('Token', '').strip()
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist:
                pass
        if request.user.is_authenticated:
            if request.user.admin or request.user.demo:
                return self.get_response(request)
        return JsonResponse({'message': 'We\'re sorry, this area is for admin only'})


class LastSeenMiddleware:
    """
    sends a request to celery to mark user as seen
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        print('request_received')
        headers = {k: v for k, v in request.META.items() if is_jsonable(v)}
        ip_address = get_client_ip(request)[0]
        path = request.get_full_path()
        harvest_request.delay(headers, path, ip_address)
        return self.get_response(request)


        # if 'accounts/login' in request.path:
        # if 'landing' in request.path:
        #     return self.get_response(request)
        # if 'admin' in request.path:
        #     return self.get_response(request)
        # if 'get-demo' in request.path:
        #     return self.get_response(request)