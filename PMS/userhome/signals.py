from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import  Mail, Notification, NotificationUser
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import m2m_changed
import json
@receiver(post_save, sender=Mail)
def send_mail(sender, instance, created, **kwargs):
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
                
@receiver(m2m_changed, sender=Notification.users.through)
def send_notification(sender, instance, action, **kwargs):
    """
    Trigger WebSocket notification when users are added to a Notification.
    """
    if action == "post_add":  # Ensure we trigger only after users are added
        channel_layer = get_channel_layer()

        print("Users:", instance.users.all())  # Debugging

        for user in instance.users.all():
            print(f"Sending notification to {user.username}")  # Debugging
            NotificationUser.objects.create(user=user, notification=instance)
            # Send WebSocket message to each user's group
            async_to_sync(channel_layer.group_send)(
                f"notification_{user.id}",  # Group for each user
                {
                    'type': 'send_notification',
                    'message': instance.message,
                     "id": instance.id
                }
            )
