from .models import SupplierEmployeeProfile, BaseProfile


def employee_mini_serializer(profile: SupplierEmployeeProfile):
    return {
        'pk': profile.pk,
        'name': profile.user.get_ful_name(),
        'email': profile.user.email(),
        'avatar': profile.avatar,
        'title': profile.title
        }

def base_mini_serializer(profile: BaseProfile):
    return {
        'pk': profile.pk,
        'name': profile.user.get_full_name(),
        'email': profile.user.email(),
        'avatar': profile.avatar,
        }
