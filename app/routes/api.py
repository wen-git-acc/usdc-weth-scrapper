from fastapi import APIRouter

from app.routes.deposit_route.controller import deposit_plan_route
from app.routes.health_check import health_check_router

router = APIRouter()
router.include_router(router=health_check_router, tags=["Health Check"])
router.include_router(router=deposit_plan_route, tags=["Deposit Plan StashAway"])
