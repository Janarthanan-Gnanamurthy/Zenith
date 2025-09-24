from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .firebase_admin import verify_firebase_token
from typing import Dict, Any, Optional
import os

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)  # Don't auto-raise error for missing tokens

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from Firebase token.
    Falls back to development mode if no credentials provided and DISABLE_AUTH is set.
    """
    # Check if authentication is disabled for development
    if os.getenv("DISABLE_AUTH", "false").lower() == "true":
        if not credentials:
            # Return a development user
            return {
                "uid": "dev_user_123",
                "email": "dev@example.com",
                "email_verified": True,
                "name": "Development User",
                "picture": None,
                "firebase_claims": {}
            }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the token with Firebase
    token = credentials.credentials
    decoded_token = verify_firebase_token(token)
    
    # Return the user claims from the token
    return {
        "uid": decoded_token.get("uid"),
        "email": decoded_token.get("email"),
        "email_verified": decoded_token.get("email_verified", False),
        "name": decoded_token.get("name"),
        "picture": decoded_token.get("picture"),
        "firebase_claims": decoded_token.get("firebase", {})
    }