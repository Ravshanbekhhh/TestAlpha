"""
Check test status in database
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.test import Test
from app.models.admin import AdminUser  # Import for relationship


async def check_tests():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(Test).order_by(Test.created_at.desc()).limit(5))
        tests = result.scalars().all()
        
        print(f"Found {len(tests)} tests in database:\n")
        
        for t in tests:
            print(f"Test Code: {t.test_code}")
            print(f"  Title: {t.title}")
            print(f"  Is Active: {t.is_active}")
            print(f"  Created: {t.created_at}")
            print()


if __name__ == "__main__":
    asyncio.run(check_tests())
