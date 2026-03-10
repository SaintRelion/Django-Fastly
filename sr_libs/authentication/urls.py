from django.urls import path
from .views import (
    ChangePasswordView,
    CheckDeviceView,
    CustomTokenObtainPairView,
    MeView,
    RegisterView,
    ResetPasswordView,
    SendResetPasswordLinkView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "send-reset-link/", SendResetPasswordLinkView.as_view(), name="send_reset_link"
    ),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("check/device/", CheckDeviceView.as_view(), name="check_device"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
