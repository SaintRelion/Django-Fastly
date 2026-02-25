from django.urls import path
from .views import SendOTP, VerifyOTP

urlpatterns = [
    path("send/", SendOTP.as_view(), name="send-otp"),
    path("verify/", VerifyOTP.as_view(), name="verify-otp"),
]
