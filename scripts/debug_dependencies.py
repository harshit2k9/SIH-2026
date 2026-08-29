"""
Debug helper: tests each external dependency (ClamAV, MinIO, PostgreSQL)
independently, with full tracebacks, so you can see exactly which one is
failing instead of a generic 500 error.

Run from the project root:
    uv run python scripts/debug_dependencies.py
     only for development/debugging, not for production use
        
"""
import asyncio  
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def test_clamav(test_file_path: str):
    print("\n--- Testing ClamAV ---")
    try:
        from app.services import antivirus
        test_file = Path(test_file_path)
        if not test_file.exists():
            print(f"SKIPPED: {test_file} not found.")
            return
        result = await antivirus.scan_file(str(test_file))
        print(f"SUCCESS: infected={result.infected}")
    except Exception:
        print("FAILED:")
        traceback.print_exc()


async def test_minio():
    print("\n--- Testing MinIO ---")
    try:
        from app.services import storage
        await storage.ensure_bucket()
        print("SUCCESS: bucket check/creation worked")
    except Exception:
        print("FAILED:")
        traceback.print_exc()


async def test_db():
    print("\n--- Testing PostgreSQL ---")
    try:
        from app.database import init_db_pool, get_pool, close_db_pool
        await init_db_pool()
        pool = get_pool()
        val = await pool.fetchval("SELECT 1")
        print(f"SUCCESS: query returned {val}")
        row = await pool.fetchrow("SELECT * FROM users WHERE id = 1")
        print(f"Seeded test user row: {row}")
        await close_db_pool()
    except Exception:
        print("FAILED:")
        traceback.print_exc()


async def test_magic(test_file_path: str):
    print("\n--- Testing python-magic (MIME detection) ---")
    try:
        from app.security.sanitize import detect_true_mime
        test_file = Path(test_file_path)
        if not test_file.exists():
            print(f"SKIPPED: {test_file} not found.")
            return
        mime = detect_true_mime(str(test_file))
        print(f"SUCCESS: detected mime={mime}")
    except Exception:
        print("FAILED:")
        traceback.print_exc()


async def main():
    test_file_path = sys.argv[1] if len(sys.argv) > 1 else str(
        Path(__file__).resolve().parent.parent / "1.pdf"
    )
    print(f"Using test file: {test_file_path}")
    await test_magic(test_file_path)
    await test_clamav(test_file_path)
    await test_minio()
    await test_db()
    print("\nDone. Whichever section says FAILED above is your real problem.")


if __name__ == "__main__":
    asyncio.run(main())