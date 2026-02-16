"""
API client for communicating with backend.
"""
import aiohttp
from typing import Optional, Dict, List, Any
from config import settings


class APIClient:
    """
    Client for backend API requests.
    """
    
    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def register_user(self, telegram_id: int, full_name: str, surname: str, region: str) -> Dict:
        """
        Register a new user.
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/users/register"
        
        data = {
            "telegram_id": telegram_id,
            "full_name": full_name,
            "surname": surname,
            "region": region
        }
        
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """
        Get user by Telegram ID.
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/users/telegram/{telegram_id}"
        
        async with session.get(url) as response:
            if response.status == 404:
                return None
            response.raise_for_status()
            return await response.json()
    
    async def get_test_by_code(self, test_code: str) -> Optional[Dict]:
        """
        Get test by code.
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/tests/code/{test_code}"
        
        async with session.get(url) as response:
            if response.status == 404:
                return None
            response.raise_for_status()
            return await response.json()
    
    async def create_session(self, user_id: str, test_id: str) -> Optional[Dict]:
        """
        Create a new test session.
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/sessions/start"
        
        data = {
            "user_id": user_id,
            "test_id": test_id
        }
        
        async with session.post(url, json=data) as response:
            if response.status == 400:
                return None
            response.raise_for_status()
            return await response.json()
    
    async def get_user_results(self, user_id: str) -> List[Dict]:
        """
        Get all results for a user.
        """
        session = await self._get_session()
        url = f"{self.base_url}/api/v1/results/user/{user_id}"
        
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


# Global API client instance
api_client = APIClient()
