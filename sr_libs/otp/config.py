from dataclasses import dataclass


@dataclass
class SROTPConfig:
    OTP_EXPIRY_SECONDS = 300
    OTP_MAX_ATTEMPTS = 3
    OTP_ONE_TIME_USE = True
