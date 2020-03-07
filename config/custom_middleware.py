
import json
from ipware import get_client_ip
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from rest_framework.authtoken.models import Token
from .tasks import verify_token

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
        if request.method == 'OPTIONS':
            return self.get_response(request)
        to_skip = [settings.ADMIN_URL, 'favicon']
        if any(skip in request.path for skip in to_skip):
            return self.get_response(request)
        headers = {k: v for k, v in request.META.items() if is_jsonable(v)}
        ip_address = get_client_ip(request)[0]
        request.record_dict = {
            'location': headers.get('HTTP_LOCATION'),
            'ip_address': ip_address
            }
        header_token = headers.get('HTTP_AUTHORIZATION', None)
        if header_token:
            verify_token.delay(header_token, request.path, ip_address)
            return self.get_response(request)
        if not request.session or not request.session.session_key:
            request.session.create()
        # request.record_dict.update({'session_id': request.session.session_key})
        return self.get_response(request)

            # print('have token ', header_token)
            # harvest_user.delay(header_token, path, params, headers, ip_address)
                # print('key created ', request.session.session_key)
                # harvest_anonymous.delay(request.session.session_key, path, params, headers, ip_address)
            # print(request.session.session_key)
        # session_id = headers.get('HTTP_SESSIONID')
        # print(session_id)
        # if not session_id:
        # if request.method != 'GET':
        #     return self.get_response(request)
        # print(request.user)
        # path = request.get_full_path()

        # for k, v in headers.items():
        #     print(k, '---', v)

        # harvest_request.delay(headers, path, ip_address)
