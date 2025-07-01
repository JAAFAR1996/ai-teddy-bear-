import asyncio
import random

from locust import HttpUser, between, task


class TeddyBearUser(HttpUser):
    """Load test user simulation"""

    wait_time = between(1, 3)

    def on_start(self):
        """Login and get token"""
        response = self.client.post(
            "/api/v1/auth/login", json={"email": "test@parent.com", "password": "test-password"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(3)
    def start_conversation(self):
        """Test starting conversations"""
        self.client.post(
            "/api/v1/conversations/start",
            json={
                "child_id": "test-child-1",
                "initial_message": random.choice(["مرحبا", "كيف حالك؟", "Hello", "Let's play"]),
            },
            headers=self.headers,
        )

    @task(5)
    def send_message(self):
        """Test sending messages"""
        self.client.post(
            "/api/v1/conversations/active/messages",
            json={"text": random.choice(["ما هذا؟", "احكي لي قصة", "What is this?", "Tell me a story"])},
            headers=self.headers,
        )

    @task(2)
    def get_conversation_history(self):
        """Test getting conversation history"""
        self.client.get("/api/v1/children/test-child-1/conversations", headers=self.headers)

    @task(1)
    def end_conversation(self):
        """Test ending conversations"""
        self.client.post("/api/v1/conversations/active/end", headers=self.headers)
