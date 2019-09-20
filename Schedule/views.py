from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from UserProductCollections.models import BaseProject


@api_view(['GET'])
def schedule(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    assignments = project.product_assignments.all()
    
