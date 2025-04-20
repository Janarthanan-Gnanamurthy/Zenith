from fastapi import APIRouter
from .auth import router as auth_router
from .user import router as user_router
from .services import router as services_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(services_router, tags=["services"])