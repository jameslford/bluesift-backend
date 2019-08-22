from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from .models import MailingList, EmailAddress
from rest_framework import status


@api_view(['POST'])
def add_to_mailinglist(request):
    data = request.data
    list_name = data.get('list_name', None)
    email_address = data.get('email', None)
    if not email_address or not list_name:
        return Response('Email needed!', status=status.HTTP_400_BAD_REQUEST)
    valid = send_mail(
        subject="You're on the list",
        from_email='no_reply@BlueSift.com',
        message="Thanks for signing up! We can't wait to share what we've built for you!",
        recipient_list=[email_address]
    )
    if valid != 1:
        return Response('Unable to deliver email', status=status.HTTP_400_BAD_REQUEST)
    mailing_list = MailingList.objects.get_or_create(name=list_name)[0]
    email = EmailAddress.objects.get_or_create(email_address=email_address)[0]
    mailing_list.email_addresses.add(email)
    send_mail(
        subject='Signup',
        message=email_address + ' has signed up to be notified',
        from_email='no_reply@BlueSift.com',
        recipient_list=['jford@bluesift.com']
    )
    return Response(status=status.HTTP_201_CREATED)
