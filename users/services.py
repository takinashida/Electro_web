import secrets
from datetime import timedelta
from django.utils import timezone
from users.models import EmailConfirmationToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator

def create_email_confirmation(user):
    token = secrets.token_hex(32)

    EmailConfirmationToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=24)
    )

    user.is_active = False
    user.save(update_fields=['is_active'])

    return token



password_reset_token = PasswordResetTokenGenerator()
