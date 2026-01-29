from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from celery.utils.log import get_task_logger
from celery import shared_task

logger = get_task_logger(__name__)



@shared_task
def send_confirmation_email(email, url):
    print("Конфирм отправлен")
    send_mail(
        subject='Подтверждение почты',
        message=f'Подтвердите почту по ссылке:\n{url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )

@shared_task
def send_password_reset_email(email, token):
    print("Ресет отправлен")
    subject = "Восстановление пароля"
    message = f"Привет! Чтобы сбросить пароль, перейди по ссылке: http://localhost:8000/users/reset-password/{token}/"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )