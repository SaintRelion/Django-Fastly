from django.conf import settings

# defaults
DEFAULTS = {
    "RP_ID": "default-rp-id",
    "RP_NAME": "default-rp-name",
    "ORIGIN": "http://localhost",
}

# override with project settings if they exist
for k, v in DEFAULTS.items():
    setattr(settings, k, getattr(settings, k, v))
