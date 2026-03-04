# Twilio SMS configuration
TWILIO_ACCOUNT_SID = None  # Your Twilio Account SID
TWILIO_AUTH_TOKEN = None  # Your Twilio Auth Token
TWILIO_PHONE_NUMBER = None  # Your Twilio phone number (sender)

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Live
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

EVENTSTREAM_CHANNELMANAGER_CLASS = (
    "delivery_channels.managers.channelmanager.MyChannelManager"
)

EVENTSTREAM_REDIS = {"host": "localhost", "port": 6379, "db": 0}
