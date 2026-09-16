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
# CREATE chain_of_custody_logs TABLE IF NOT EXISTS
# ============================================================

print("Checking for chain_of_custody_logs table...")

cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'chain_of_custody_logs'
    );
""")

table_exists = cursor.fetchone()[0]

if not table_exists:
    print("Creating chain_of_custody_logs table...")
    cursor.execute("""
        CREATE TABLE public.chain_of_custody_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            case_id UUID NOT NULL REFERENCES cases(id),
            document_id UUID REFERENCES documents(id),
            evidence_id UUID REFERENCES evidence_items(id),
            actor_id UUID NOT NULL REFERENCES users(id),
            actor_department_id UUID NOT NULL REFERENCES departments(id),
            action VARCHAR NOT NULL,
            ip_address VARCHAR,
            user_agent TEXT,
            previous_log_hash VARCHAR,
            current_log_hash VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_chain_of_custody_case_id ON public.chain_of_custody_logs(case_id);
        CREATE INDEX idx_chain_of_custody_created_at ON public.chain_of_custody_logs(created_at DESC);
        CREATE INDEX idx_chain_of_custody_actor_id ON public.chain_of_custody_logs(actor_id);
    """)
    connection.commit()
    print("✅ chain_of_custody_logs table created successfully!")
else:
    print("✅ chain_of_custody_logs table already exists.")

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