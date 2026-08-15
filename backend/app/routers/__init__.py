from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .predict import router as predict_router
from .recommend import router as recommend_router
from .monitor import router as monitor_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(predict_router)
router.include_router(recommend_router)
router.include_router(monitor_router)
