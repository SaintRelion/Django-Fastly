from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class SRModelTriggerConfig:
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_ACCEPT_CONTENT: List[str] = field(default_factory=lambda: ["json"])
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
