"""
Domain Entity - Pure Business Logic
No external dependencies allowed
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Child:
    """Child Domain Entity"""
    id: str
    name: str
    age: int
    created_at: datetime
    
    def __post_init__(self):
        """Domain validation"""
        if not 3 <= self.age <= 12:
            raise ValueError("Child age must be between 3 and 12")
            
    def is_age_appropriate_for_content(self, content_age_rating: int) -> bool:
        """Business rule: age appropriateness"""
        return self.age >= content_age_rating
