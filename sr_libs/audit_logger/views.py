from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import AuditLog
from .serializers import AuditLogSerializer
from .permissions import IsAuditViewer


class AuditLogListView(generics.ListAPIView):
    """
    List all audit logs with filters, search, and ordering.
    """

    queryset = AuditLog.objects.all().order_by("-created_at")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditViewer]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        "action",
        "category",
        "source",
        "user",
    ]

    search_fields = [
        "category",
        "object_id",
    ]

    ordering_fields = [
        "created_at",
        "action",
    ]


class AuditLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single audit log by ID.
    """

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditViewer]
