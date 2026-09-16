import getpass

import bcrypt

from database import (
    Base,
    engine,
    SessionLocal,
)

from models import Admin


# ============================================================
# ENSURE TABLE EXISTS
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# DATABASE
# ============================================================

db = SessionLocal()


try:

    print()
    print("SIH26 Administrator Setup")
    print("-------------------------")
    print()

    email = input(
        "Admin email: "
    ).strip().lower()


    password = getpass.getpass(
        "Admin password: "
    )


    confirm_password = getpass.getpass(
        "Confirm password: "
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not email:

        raise ValueError(
            "Email cannot be empty."
        )


    if password != confirm_password:

        raise ValueError(
            "Passwords do not match."
        )


    if len(password) < 10:

        raise ValueError(
            "Admin password must contain at least 10 characters."
        )


    password_bytes = password.encode(
        "utf-8"
    )


    if len(password_bytes) > 72:

        raise ValueError(
            "Password is too long."
        )


    # ========================================================
    # CHECK EXISTING
    # ========================================================

    existing = (
        db.query(Admin)
        .filter(
            Admin.email == email
        )
        .first()
    )


    if existing:

        raise ValueError(
            "An administrator with this email already exists."
        )


    # ========================================================
    # HASH PASSWORD
    # ========================================================

    password_hash = bcrypt.hashpw(

        password_bytes,

        bcrypt.gensalt()

    ).decode(
        "utf-8"
    )


    # ========================================================
    # CREATE ADMIN
    # ========================================================

    admin = Admin(

        email=email,

        password_hash=password_hash,

        is_active=True,

    )


    db.add(
        admin
    )

    db.commit()


    print()
    print("Administrator created successfully.")
    print()


except Exception as error:

    db.rollback()

    print()
    print(
        "ERROR:",
        error
    )
    print()


finally:

    db.close()