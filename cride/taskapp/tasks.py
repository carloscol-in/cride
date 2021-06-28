"""Async Celery tasks"""

# Django
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Celery
from celery.decorators import task, periodic_task

# Utilities
import time
import jwt
from datetime import timedelta

# Models
from cride.rides.models import Ride

User = get_user_model()


def gen_verification_token(user):
    """Generate JWT to verify user's account."""
    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    # `.decode()` is neccessary for PyJWT version < 2.0.0
    # for versions >=2.0.0 the token won't be represented as bytes
    return token.decode()

@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user_pk):
    """Send account verification link to user's email."""
    for i in range(30):
        time.sleep(1)
        print('Sleeping ', i+1)
    user = User.objects.get(pk=user_pk)
    verification_token = gen_verification_token(user)
    subject = f'Welcome @{user.username}! - Account Verification Code'
    from_email = 'Comparte Ride <noreply@comparteride.com>'
    content = render_to_string(
        'emails/users/account_verification.html',
        {
            'token': verification_token,
            'user': user,
        }
    )
    msg = EmailMultiAlternatives(
        subject,
        content,
        from_email,
        [user.email]
    )
    msg.attach_alternative(
        content,
        'text/html'
    )
    msg.send()

@periodic_task(name='disable_finished_rides', run_every=timedelta(seconds=30))
def disable_finished_rides():
    """Disable all finished rides."""
    now = timezone.now()
    offset = now - timedelta(seconds=60)

    # update rides that have already finished
    rides = Ride.objects.filter(arrival_date__lte=offset, is_active=True)
    rides.update(is_active=False)