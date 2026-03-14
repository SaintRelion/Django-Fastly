from django.urls import path
from .views import (
    ChangePasswordView,
    TrustedDeviceView,
    CustomTokenObtainPairView,
    MeView,
    RegisterView,
    ResetPasswordView,
    SendResetPasswordLinkView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("trust/device/", TrustedDeviceView.as_view(), name="trust_device"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "send-reset-link/", SendResetPasswordLinkView.as_view(), name="send_reset_link"
    ),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
]
