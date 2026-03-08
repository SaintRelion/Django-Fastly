from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AuditLogListView, AuditLogDetailView

urlpatterns = [
    path("auditlogs/", AuditLogListView.as_view(), name="audit_logs"),
    path("auditlogs/<int:pk>/", AuditLogDetailView.as_view(), name="audit_log_detail"),
]