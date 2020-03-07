from config.celery import app
from django.core.mail import EmailMessage




@app.task
def send_danger_log_message(pk):
    from .models import DangerLog
    dlog = DangerLog.objects.get(pk=pk)
    message = f'{dlog.message} ----- dlog number {pk}'
    email_obj = EmailMessage(
        subject="Danger",
        body=message,
        from_email='jford@bluesift.com',
        to='jford@bluesift.com',
        )
    email_obj.send()
    return f'dlog {pk} email sent'

