from django.conf import settings
from django.http import JsonResponse
from config.tasks import mark_user_seen


class StagingMiddleware:
    """
    Keeps random users from being able to look at staging data
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'accounts/login' in request.path:
            return self.get_response(request)
        if 'admin' in request.path:
            return self.get_response(request)
        if settings.ENVIRONMENT != 'staging':
            return self.get_response(request)
        if request.user.is_authenticated:
            if request.user.admin or request.user.demo:
                return self.get_response(request)
        return JsonResponse({'message': 'We\'re sorry, this area is for admin only'})


# class ProductionMiddleware(object):
#     """
#     Keeps random users from being able to look at staging data
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         if 'accounts/login' in request.path:
#             return self.get_response(request)
#         if settings.ENVIRONMENT != 'production':
#             return self.get_response(request)
#         if request.user.is_authenticated:
#             if request.user:
#                 return self.get_response(request)
#         return JsonResponse({'message': 'We\'re sorry, this area is for admin only'})


class LastSeenMiddleware:
    """
    sends a request to celery to mark user as seen
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            mark_user_seen.delay(request.user.pk)
        return self.get_response(request)
