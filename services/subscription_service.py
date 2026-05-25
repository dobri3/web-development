from domain.models import Subscription
from django.shortcuts import get_object_or_404
from django.utils import timezone


def get_user_subscription(user):

    return Subscription.objects.filter(
        user=user,
        is_active=True,
        expires_at__gt=timezone.now()
    ).first()


def create_subscription(user, expires_at):

    return Subscription.objects.create(
        user=user,
        expires_at=expires_at,
        is_active=True
    )


def deactivate_subscription(subscription_id):

    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id
    )

    subscription.is_active = False
    subscription.save()

    return subscription