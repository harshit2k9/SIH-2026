"""
One-time script to create the Master Admin user.
Run this ONLY once during initial deployment.

Usage:
    docker compose exec -it dms_backend python scripts/create_master_admin.py
"""
import os
import sys
import bcrypt
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.mfa import generate_mfa_secret
from config import settings
from database import SessionLocal, engine
from models import Admin, Base

# Ensure tables exist
Base.metadata.create_all(bind=engine)

MASTER_EMAIL = "admin@police.gov"
MASTER_PASSWORD = "Admin@12345"  # Change this immediately after first login!

def create_master_admin():
    db = SessionLocal()
    try:
        # 1. Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.email == MASTER_EMAIL).first()
        
        if existing_admin:
            print(f"⚠️  Master admin '{MASTER_EMAIL}' already exists.")
            print("   If you lost the password/MFA secret, you must manually reset them in the DB.")
            return

        # 2. Generate Password Hash
        password_hash = bcrypt.hashpw(
            MASTER_PASSWORD.encode("utf-8"), 
            bcrypt.gensalt()
        ).decode("utf-8")

        # 3. Generate MFA Secret
        mfa_secret = generate_mfa_secret()

        # 4. Create Admin
        new_admin = Admin(
            email=MASTER_EMAIL,
            password_hash=password_hash,
            is_active=True
        )
        
        # Note: Since your Admin model doesn't have mfa_secret column yet, 
        # we assume you might need to add it or store it elsewhere.
        # For now, we just create the admin. You may need to update models.Admin 
        # to include mfa_secret if your login flow requires it for admins.
        
        db.add(new_admin)
        db.commit()
        
        print("\n" + "="*60)
        print("✅ MASTER ADMIN CREATED SUCCESSFULLY")
        print("="*60)
        print(f"📧 Email:    {MASTER_EMAIL}")
        print(f"🔑 Password: {MASTER_PASSWORD}")
        print(f"📱 MFA Secret: {mfa_secret}")
        print("\n⚠️  IMPORTANT:")
        print("   1. Copy the MFA Secret above.")
        print("   2. Open Google Authenticator / Authy.")
        print("   3. Add a new account using 'Manual Entry' and paste the secret.")
        print("   4. Use the generated 6-digit code to login at /login.")
        print("   5. CHANGE THE PASSWORD immediately after logging in!")
        print("="*60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating master admin: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    create_master_admin()