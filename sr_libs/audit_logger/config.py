from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class SRAuditLoggerConfig:
    ALLOWED_GROUPS: List[str] = field(default_factory=lambda: ["admin", "staff"])
