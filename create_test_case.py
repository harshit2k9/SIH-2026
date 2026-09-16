#!/usr/bin/env python3
"""
Script to create a test case in the database for document upload testing.
Run this after ensuring the database is initialized.
"""
import uuid
import asyncpg
import asyncio
import os

# Database connection settings (matching your config)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sddms_user:sddms_secure_password_2025@localhost:5432/sddms_db")

async def create_test_case():
    print(f"Connecting to database: {DATABASE_URL}")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # First, check if departments exist
        dept_result = await conn.fetchrow("SELECT id FROM departments LIMIT 1")
        if not dept_result:
            print("❌ No departments found. Please run database initialization scripts first.")
            await conn.close()
            return
        
        dept_id = dept_result['id']
        print(f"Using department ID: {dept_id}")
        
        # Check if users exist
        user_result = await conn.fetchrow("SELECT id FROM users LIMIT 1")
        if not user_result:
            print("❌ No users found. Please run database initialization scripts first.")
            await conn.close()
            return
        
        user_id = user_result['id']
        print(f"Using user ID: {user_id}")
        
        # Create a test case
        case_uuid = uuid.uuid4()
        case_number = f"CASE-TEST-{uuid.uuid4().hex[:8].upper()}"
        
        await conn.execute("""
            INSERT INTO cases (id, case_number, title, description, classification_level, status, 
                              primary_department_id, lead_investigator_id, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, case_uuid, case_number, "Test Case for Document Upload", 
            "This is a test case created for testing document upload functionality.",
            3, "OPEN", dept_id, user_id, user_id)
        
        print(f"\n✅ Test case created successfully!")
        print(f"   Case UUID: {case_uuid}")
        print(f"   Case Number: {case_number}")
        print(f"\nUse this UUID in the Case ID field when uploading documents:")
        print(f"   {case_uuid}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_test_case())
