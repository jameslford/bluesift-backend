
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from config.celery import app



@app.task
def send_verification_email(site_domain, user_pk):
    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=user_pk)
        message = render_to_string('acc_activate_email.html', {
            'user': user,
            'domain': site_domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': user.auth_token
        })

        email_obj = EmailMessage(
            subject="Activate your Buildbook account",
            body=message,
            from_email='jford@bluesift.com',
            to=[user.email]
            )
        email_obj.send()
        return f'{user.email} email sent'
    except user_model.DoesNotExist:
        return f'{user.email} email failed'
