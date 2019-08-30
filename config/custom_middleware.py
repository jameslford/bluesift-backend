from django.conf import settings
from django.http import JsonResponse


class StagingMiddleware(object):
    """
    Keeps random users from being able to look at staging data
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.ENVIRONMENT != 'staging':
            return self.get_response(request)
        if request.user.is_authenticated:
            if request.user.admin or request.user.demo:
                return self.get_response(request)
        return JsonResponse({'message': 'We\'re sorry, this area is for admin only'})
