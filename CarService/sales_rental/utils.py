import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def generate_otp():
    """
    Generate a random six-digit OTP (One-Time Password).
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp_email(user, subject, purpose):
    """
    Send an OTP email to the user.
    """
    context = {
        'user': user,
        'otp': user.otp,
        'purpose': purpose
    }
    html_message = render_to_string('email/otp_email.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    msg = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
    msg.attach_alternative(html_message, "text/html")
    msg.send()
