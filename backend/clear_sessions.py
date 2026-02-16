"""
Script to clear test sessions for testing purposes
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.session import TestSession


async def clear_sessions():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, delete
        
        # Option 1: Clear all sessions
        print("Clearing all test sessions...")
        result = await db.execute(delete(TestSession))
        await db.commit()
        print(f"Cleared {result.rowcount} sessions")


if __name__ == "__main__":
    asyncio.run(clear_sessions())
