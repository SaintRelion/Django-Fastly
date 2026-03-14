from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class SRDALConfig:
    DEFAULT_PAGINATION_CLASS: str = "rest_framework.pagination.PageNumberPagination"
    PAGE_SIZE: int = 30

    DEFAULT_FILTER_BACKENDS: List[str] = field(
        default_factory=lambda: [
            "django_filters.rest_framework.DjangoFilterBackend",
            "rest_framework.filters.SearchFilter",
            "rest_framework.filters.OrderingFilter",
        ]
    )
