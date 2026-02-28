from django.urls import path
from .views import CheckDeviceView, CustomTokenObtainPairView, MeView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("check/device/", CheckDeviceView.as_view(), name="check_device"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
