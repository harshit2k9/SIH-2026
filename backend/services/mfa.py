import base64
from io import BytesIO

import pyotp
import qrcode


ISSUER_NAME = "SIH26 SecureDocs"


# ============================================================
# GENERATE SECRET
# ============================================================

def generate_mfa_secret():

    return pyotp.random_base32()


# ============================================================
# CREATE GOOGLE AUTHENTICATOR URI
# ============================================================

def create_provisioning_uri(
    secret: str,
    email: str
):

    totp = pyotp.TOTP(
        secret
    )

    return totp.provisioning_uri(
        name=email,
        issuer_name=ISSUER_NAME
    )


# ============================================================
# CREATE QR CODE
# ============================================================

def create_qr_code_base64(
    provisioning_uri: str
):

    qr = qrcode.QRCode(
        version=1,
        box_size=8,
        border=4
    )

    qr.add_data(
        provisioning_uri
    )

    qr.make(
        fit=True
    )

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )


    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )


    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode(
        "utf-8"
    )


    return encoded


# ============================================================
# VERIFY 6 DIGIT CODE
# ============================================================

def verify_totp(
    secret: str,
    code: str
):

    if not secret:
        return False


    code = code.strip()


    if (
        not code.isdigit()
        or len(code) != 6
    ):

        return False


    totp = pyotp.TOTP(
        secret
    )


    return totp.verify(
        code,
        valid_window=1
    )