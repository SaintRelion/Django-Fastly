from dataclasses import dataclass


@dataclass
class SROTPConfig:
    OTP_EXPIRY_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 3
    OTP_ONE_TIME_USE: bool = True
