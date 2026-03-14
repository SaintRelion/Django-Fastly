import base64

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    RegistrationCredential,
    AuthenticatorAttestationResponse,
    AuthenticationCredential,
    AuthenticatorAssertionResponse,
)

from .models import DeviceCredential


def base64url_to_bytes(val: str) -> bytes:
    padding = "=" * (-len(val) % 4)
    return base64.urlsafe_b64decode(val + padding)


from django.conf import settings
from .config import SRFingerprintConfig

SR_FINGERPRINT_CONFIG = getattr(
    settings, "SR_FINGERPRINT_CONFIG", SRFingerprintConfig()
)

RP_ID = SR_FINGERPRINT_CONFIG.RP_ID
RP_NAME = SR_FINGERPRINT_CONFIG.RP_NAME
ORIGIN = SR_FINGERPRINT_CONFIG.ORIGIN


def create_registration_options(user):
    return generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=str(user.username).encode(),
        user_name=user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.REQUIRED
        ),
    )


def verify_registration(user, challenge_b64, data):
    return verify_registration_response(
        credential=RegistrationCredential(
            data["id"],
            base64url_to_bytes(data["rawId"]),
            AuthenticatorAttestationResponse(
                base64url_to_bytes(data["response"]["clientDataJSON"]),
                base64url_to_bytes(data["response"]["attestationObject"]),
            ),
        ),
        expected_challenge=base64url_to_bytes(challenge_b64),
        expected_rp_id=RP_ID,
        expected_origin=ORIGIN,
        require_user_verification=True,
    )


def create_authentication_options(credentials):
    return generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=credentials,
        user_verification=UserVerificationRequirement.REQUIRED,
    )


def verify_authentication(credential: DeviceCredential, challenge_b64, data):
    return verify_authentication_response(
        credential=AuthenticationCredential(
            data["id"],
            base64url_to_bytes(data["rawId"]),
            AuthenticatorAssertionResponse(
                base64url_to_bytes(data["response"]["clientDataJSON"]),
                base64url_to_bytes(data["response"]["authenticatorData"]),
                base64url_to_bytes(data["response"]["signature"]),
                (
                    base64url_to_bytes(data["response"]["userHandle"])
                    if data["response"]["userHandle"]
                    else None
                ),
            ),
        ),
        expected_challenge=base64url_to_bytes(challenge_b64),
        expected_rp_id=RP_ID,
        expected_origin=ORIGIN,
        require_user_verification=True,
        credential_public_key=credential.public_key,
        credential_current_sign_count=credential.sign_count,
    )
