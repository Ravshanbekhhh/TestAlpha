"""
Simple script to create an admin user
"""
import asyncio
from app.database import AsyncSessionLocal
from app.services.auth_service import AuthService


async def create_admin():
    async with AsyncSessionLocal() as db:
        try:
            admin = await AuthService.create_admin_user(db, "admin", "admin123")
            await db.commit()
            print(f"✓ Admin user created: {admin.username}")
            print(f"  Username: admin")
            print(f"  Password: admin123")
        except Exception as e:
            print(f"✗ Error: {e}")
            print("  Admin might already exist - try logging in!")


if __name__ == "__main__":
    asyncio.run(create_admin())
