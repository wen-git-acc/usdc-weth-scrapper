from fastapi import APIRouter

from app.routes.scrapper_route.controller import scrapper_route
from app.routes.health_check import health_check_router

router = APIRouter()
router.include_router(router=health_check_router, tags=["Health Check"])
router.include_router(router=scrapper_route, tags=["Usdc/WETH Scrapper Route"])