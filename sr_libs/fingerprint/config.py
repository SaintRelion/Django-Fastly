from dataclasses import dataclass


@dataclass(frozen=True)
class SRFingerprintConfig:
    RP_ID: str = "default-rp-id"
    RP_NAME: str = "default-rp-name"
    ORIGIN: str = "http://localhost"
