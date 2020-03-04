from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from Scraper.models import ScraperGroup
from config.models import ConfigTree


# class CommandGroup:

#     def __init__(self, title, link_append, groups, base_val=None):
#         self.title = title
#         self.link_append = link_append
#         self.groups = groups
#         self.base_val = base_val

#         def serialize(self):

#             return {
#                 'title': self.title,
#                 'link_append': self.link_append,
#                 'groups': self.groups,
#                 'base_val': self.base_val
#             }

# def create_command(name, link, **kwargs):
#     ret_dict = {
#         'name': name,

#     }


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def dashboard(request: Request):
    scrapers = ScraperGroup.objects.all().values()

    # scrape_buttons = []
    # scrape_buttons.append({'name': 'all', 'link': 'scrape'})
    # for scraper in scrapers:
#         re_dict = {}






@api_view(['GET'])
@permission_classes((IsAdminUser,))
def scrape(request, group='all'):
    pass


# @api_view(['GET'])
# @permission_classes((IsAdminUser,))
# def scrape(request, pk=None):
#     pass


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def refresh_tree(request):
    ConfigTree.refresh()

