from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserUpdateAPIView, UserListAPIView, EmailConfirmAPIView, \
    RequestPasswordReset, ResetPassword

app_name=UsersConfig.name

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),

    path("registration/", UserCreateAPIView.as_view(), name="user_create"),

    path('email-confirm/<str:token>/', EmailConfirmAPIView.as_view(), name='email-confirm'),
    path("request-reset/", RequestPasswordReset.as_view(), name="request-reset"),
    path("reset-password/<str:token>/", ResetPassword.as_view(), name="reset-password"),

    path("update/<int:pk>/", UserUpdateAPIView.as_view(), name="user_update"),
    path("", UserListAPIView.as_view(), name="user_list"),
]