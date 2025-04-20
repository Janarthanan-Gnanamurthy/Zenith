from fastapi import APIRouter, Depends, HTTPException
from auth.dependencies import get_current_user
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter()

# User profile model
class UserProfile(BaseModel):
    display_name: str = None
    bio: str = None
    preferences: Dict[str, Any] = {}

# In a real app, you would use a database
# This is just a mock for demonstration
user_profiles = {}

@router.post("/profile", response_model=Dict[str, Any])
async def create_or_update_profile(
    profile: UserProfile = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create or update user profile.
    """
    uid = current_user["uid"]
    
    # If profile data is not provided, use existing or create default
    if not profile:
        profile_data = user_profiles.get(uid, UserProfile())
    else:
        profile_data = profile
    
    # Store profile
    user_profiles[uid] = profile_data
    
    return {
        "uid": uid,
        "email": current_user["email"],
        "profile": profile_data.dict(),
        "message": "Profile updated successfully"
    }

@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user profile.
    """
    uid = current_user["uid"]
    
    # Get profile or return default
    profile_data = user_profiles.get(uid, UserProfile())
    
    return {
        "uid": uid,
        "email": current_user["email"],
        "profile": profile_data.dict()
    }