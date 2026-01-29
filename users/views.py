from django.shortcuts import render
from django.urls import reverse
from rest_framework import viewsets, generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from users.tasks import send_confirmation_email, send_password_reset_email
from users.models import User, EmailConfirmationToken
from users.permissions import IsOwner
from users.serializers import UserSerializer, PasswordResetRequestSerializer, PasswordResetSerializer
from users.services import create_email_confirmation, password_reset_token
from kombu.exceptions import OperationalError

# Create your views here.
class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token = create_email_confirmation(user)

        confirm_url = request.build_absolute_uri(
            reverse('users:email-confirm', args=[token])
        )

        try:
            send_confirmation_email.delay(user.email, confirm_url)
        except OperationalError as e:
            user.delete()
            print("Celery временно недоступен:", e)

        return Response(
            {'detail': 'Подтвердите почту'},
            status=status.HTTP_201_CREATED
        )



class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]



class EmailConfirmAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        token_obj = get_object_or_404(
            EmailConfirmationToken,
            token=token
        )

        if not token_obj.is_valid():
            return Response(
                {'detail': 'Ссылка устарела'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.is_active = True
        user.save(update_fields=['is_active'])

        token_obj.delete()

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

class UpdatePasswordAPIView(APIView):
    permission_classes = []

    def get(self, request, token):
        token_obj = get_object_or_404(
            EmailConfirmationToken,
            token=token
        )

        if not token_obj.is_valid():
            return Response(
                {'detail': 'Ссылка устарела'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = token_obj.user
        user.is_active = True
        user.save(update_fields=['is_active'])

        token_obj.delete()

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class RequestPasswordReset(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Если пользователь существует, письмо отправлено"}, status=status.HTTP_200_OK)

        token = password_reset_token.make_token(user)
        send_password_reset_email.delay(email, token)
        return Response({"detail": "Если пользователь существует, письмо отправлено"}, status=status.HTTP_200_OK)


class ResetPassword(APIView):
    def post(self, request, token):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Неверный email"}, status=status.HTTP_400_BAD_REQUEST)

        if not password_reset_token.check_token(user, token):
            return Response({"detail": "Неверный или истекший токен"}, status=status.HTTP_400_BAD_REQUEST)

        if user.check_password(password):
            return Response(
                {"detail": "Вы не можете поставить старый пароль."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.reset_token = None
        user.save()

        user.save()
        return Response({"detail": "Пароль успешно обновлен"}, status=status.HTTP_200_OK)