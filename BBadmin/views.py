from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import get_user_model

from Accounts.serializers import UserSerializer


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def dashboard(request):
    user_model = get_user_model()
    users = user_model.objects.all()
    serialized_user = UserSerializer(users, many=True)
    return Response({'users': serialized_user.data})

@api_view(['POST'])
@permission_classes((IsAdminUser,))
def admin_check(request):
    return Response({'authorized': True})

@api_view(['POST', 'DELETE'])
@permission_classes((IsAdminUser,))
def user_details(request, pk=None):
    user_model = get_user_model()

    if request.method == 'DELETE':
        user = user_model.objects.get(id=pk)
        deleted_user = user.delete()
        return Response({'deleted': deleted_user}, status=status.HTTP_202_ACCEPTED) 

