from django.urls import path
from .views import *

urlpatterns = [
    path("check/", CheckDeviceRegistrationView.as_view()),
    path("register/begin/", BeginRegistration.as_view()),
    path("register/finish/", FinishRegistration.as_view()),
    path("login/begin/", BeginLogin.as_view()),
    path("login/finish/", FinishLogin.as_view()),
]
