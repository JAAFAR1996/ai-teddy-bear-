import asyncio
import time
from typing import List

import aiohttp


class ConcurrentUserTest:
    """Test concurrent user scenarios"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[dict] = []

    async def simulate_user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a complete user session"""
        start_time = time.time()

        try:
            # Login
            async with session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"email": f"user{user_id}@test.com", "password": "test-password"},
            ) as response:
                if response.status != 200:
                    return {"user_id": user_id, "status": "login_failed"}

                token = (await response.json())["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

            # Start conversation
            async with session.post(
                f"{self.base_url}/api/v1/conversations/start",
                json={"child_id": f"child-{user_id}", "initial_message": "Hello"},
                headers=headers,
            ) as response:
                if response.status != 200:
                    return {"user_id": user_id, "status": "conversation_failed"}

            # Send messages
            for i in range(3):
                async with session.post(
                    f"{self.base_url}/api/v1/conversations/active/messages",
                    json={"text": f"Message {i+1}"},
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        return {"user_id": user_id, "status": "message_failed"}

                await asyncio.sleep(0.5)  # Simulate thinking time

            end_time = time.time()
            return {"user_id": user_id, "status": "success", "duration": end_time - start_time}

        except Exception as e:
            return {"user_id": user_id, "status": "error", "error": str(e)}

    async def run_concurrent_test(self, num_users: int = 50):
        """Run concurrent user test"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.simulate_user_session(session, i) for i in range(num_users)]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
            failed = len(results) - successful

            if successful > 0:
                avg_duration = (
                    sum(r["duration"] for r in results if isinstance(r, dict) and "duration" in r) / successful
                )
            else:
                avg_duration = 0

            print(f"Concurrent Users: {num_users}")
            print(f"Successful: {successful}")
            print(f"Failed: {failed}")
            print(f"Success Rate: {successful/num_users*100:.1f}%")
            print(f"Average Duration: {avg_duration:.2f}s")

            return results


if __name__ == "__main__":
    test = ConcurrentUserTest()
    asyncio.run(test.run_concurrent_test(50))
