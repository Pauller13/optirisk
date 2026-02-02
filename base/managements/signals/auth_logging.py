import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth import get_user_model

logger = logging.getLogger('auth_logger')

UserModel = get_user_model()
@receiver(user_logged_in)
def log_user_login(sender,credentials, request, user, **kwargs):
    email = credentials.get('email', 'Unknown')
    user = UserModel.objects.filter(email=email).first()
    logger.info(f"[LOGIN] User '{user.last_name} {user.first_name}' logged in from IP {get_client_ip(request)} at {now()}.")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('email', 'Unknown')
    logger.warning(f"[FAILED LOGIN] Failed login attempt for username '{username}' from IP {get_client_ip(request)} at {now()}.")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"[LOGOUT] User '{user.username}' logged out from IP {get_client_ip(request)} at {now()}.")


def get_client_ip(request):
    """Helper to get the real IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
