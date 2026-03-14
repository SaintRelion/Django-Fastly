from dataclasses import dataclass
from typing import List


@dataclass
class SRAuditLoggerConfig:
    ALLOWED_GROUPS: List[str] = ["admin", "staff"]
