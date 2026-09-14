import psycopg2
from config import settings
from database import Base, engine

# Create tables defined in models if they don't exist
Base.metadata.create_all(bind=engine)

# ============================================================
# CONNECT POSTGRESQL
# ============================================================

connection = psycopg2.connect(settings.DATABASE_URL)
cursor = connection.cursor()

# ============================================================
# EXISTING USER COLUMNS
# ============================================================

cursor.execute(
    """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'users';
    """
)

existing_columns = {row[0] for row in cursor.fetchall()}

# ============================================================
# NEW COLUMNS
# ============================================================

new_columns = {
    "face_similarity_score": "DOUBLE PRECISION",
    "face_match_threshold": "DOUBLE PRECISION",
    "flag_reason": "VARCHAR",
    "admin_review_status": "VARCHAR DEFAULT 'NOT_REQUIRED'",
}

# ============================================================
# ADD MISSING COLUMNS
# ============================================================

for column_name, column_type in new_columns.items():
    if column_name not in existing_columns:
        print(f"Adding column: {column_name}")
        cursor.execute(
            f"""
            ALTER TABLE users
            ADD COLUMN {column_name} {column_type};
            """
        )
    else:
        print(f"Already exists: {column_name}")

# ============================================================
# EXISTING FLAGGED USERS
# ============================================================

cursor.execute(
    """
    UPDATE users
    SET admin_review_status = 'PENDING'
    WHERE registration_status = 'FLAGGED'
    AND (
        admin_review_status IS NULL
        OR admin_review_status = 'NOT_REQUIRED'
    );
    """
)

# ============================================================
# COMMIT & CLOSE
# ============================================================

connection.commit()
cursor.close()
connection.close()

print()
print("PostgreSQL database migration complete.")