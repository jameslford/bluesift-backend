""" Profiles.serializers """
from Plans.serializers import PlanSerializer
from .models import ProEmployeeProfile, RetailerEmployeeProfile, ConsumerProfile

def serialize_profile(user=None, profile=None):
    if not profile:
        if not user:
            return None
        profile = user.get_profile()
    ret_dict = {
        'pk': profile.pk,
        'avatar': profile.avatar.url if profile.avatar else None,
        }
    all_collaborators = profile.collaborators.values_list('pk', flat=True)
    pro_collaborators = ProEmployeeProfile.objects.filter(pk__in=all_collaborators).values('pk', 'company__pk')
    ret_collaborators = RetailerEmployeeProfile.objects.filter(pk__in=all_collaborators).values('pk', 'company__pk')
    if not (user.is_pro or user.is_supplier):
        ret_dict['plan'] = PlanSerializer(profile.plan).data if profile.plan else None
        ret_dict['phone_number'] = profile.phone_number
        return ret_dict
    ret_dict['company_name'] = profile.company.name
    ret_dict['owner'] = profile.owner
    ret_dict['admin'] = profile.admin
    ret_dict['title'] = profile.title
    return ret_dict


        # if user.is_pro:
    #     ret_dict['links'] = ret_dict['links'] + ['projects', 'metrics', 'company_info']
    # elif user.is_supplier:
    #     ret_dict['locations_managed'] = profile.locations_managed()
    #     ret_dict['links'] = ret_dict['links'] + ['locations', 'metrics', 'company_info']
    # else:
    #     ret_dict['links'].append('projects')
