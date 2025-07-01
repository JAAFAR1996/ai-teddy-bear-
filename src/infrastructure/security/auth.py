import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class AuthService:
    """JWT-based authentication with refresh tokens"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()

    def create_access_token(
        self, subject: str, expires_delta: timedelta = timedelta(minutes=15)
    ) -> str:
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, subject: str) -> str:
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32),  # Unique token ID
        }
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ) -> Dict[str, Any]:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
