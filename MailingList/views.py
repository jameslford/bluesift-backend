from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import MailingList, EmailAddress
from rest_framework import status



@api_view(['POST'])
def add_to_mailinglist(request):
    data = request.data
    list_name = data.get('list_name')
    email_address = data.get('email')
    mailing_list = MailingList.objects.filter(name=list_name).first()
    email = EmailAddress.objects.get_or_create(email_address=email_address)
    mailing_list.email_addresses.add(email)
    return Response(status=status.HTTP_201_CREATED)
