import sqlite3
from pathlib import Path

from database import Base, engine


BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = BASE_DIR / "sih26.db"


# ============================================================
# CREATE NEW TABLES
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# CONNECT SQLITE
# ============================================================

connection = sqlite3.connect(
    DATABASE_FILE
)

cursor = connection.cursor()


# ============================================================
# EXISTING USER COLUMNS
# ============================================================

cursor.execute(
    "PRAGMA table_info(users)"
)

existing_columns = {
    row[1]
    for row in cursor.fetchall()
}


# ============================================================
# NEW COLUMNS
# ============================================================

new_columns = {

    "face_similarity_score":
        "REAL",

    "face_match_threshold":
        "REAL",

    "flag_reason":
        "TEXT",

    "admin_review_status":
        "TEXT DEFAULT 'NOT_REQUIRED'",

}


# ============================================================
# ADD MISSING COLUMNS
# ============================================================

for column_name, column_type in new_columns.items():

    if column_name not in existing_columns:

        print(
            f"Adding column: {column_name}"
        )

        cursor.execute(
            f"""
            ALTER TABLE users
            ADD COLUMN {column_name} {column_type}
            """
        )

    else:

        print(
            f"Already exists: {column_name}"
        )


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
    )
    """
)


# ============================================================
# COMMIT
# ============================================================

connection.commit()

connection.close()


print()
print("Database migration complete.")