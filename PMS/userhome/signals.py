from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import  Notification
from django.core.mail import send_mail
from django.conf import settings
@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        users= User.objects.all()
        for user in users:
            send_mail(
                'Notification',
                instance.message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=True
            )
                
        