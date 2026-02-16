"""
Quick script to check sessions in database
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.session import TestSession
from datetime import datetime


async def check_sessions():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(TestSession).order_by(TestSession.started_at.desc()).limit(5))
        sessions = result.scalars().all()
        
        print(f"Found {len(sessions)} recent sessions:\n")
        
        for s in sessions:
            now = datetime.utcnow()
            print(f"Session Token: {s.session_token}")
            print(f"  Started: {s.started_at}")
            print(f"  Expires: {s.expires_at}")
            print(f"  Current time: {now}")
            print(f"  Time until expiry: {(s.expires_at - now).total_seconds()/60:.1f} minutes")
            print(f"  Is expired: {s.is_expired}")
            print(f"  Is submitted: {s.is_submitted}")
            print(f"  Is valid (property): {s.is_valid}")
            print()


if __name__ == "__main__":
    asyncio.run(check_sessions())
