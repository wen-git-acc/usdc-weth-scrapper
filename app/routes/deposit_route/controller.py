from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.core.log.logger import Logger
from app.routes.deposit_route.handler import plan_deposit_handler
from app.routes.deposit_route.models import DepositPlanResponseModel
from app.routes.deposit_route.response_config import open_api_config

deposit_plan_route = APIRouter()
logger = Logger(name="deposit_plan_route_controller")


async def log_request(request: Request) -> None:
    body_info = await request.body()
    logger.info(message={"body": body_info, "headers": request.headers})


@deposit_plan_route.post(
    "/plan/deposit",
    response_model=DepositPlanResponseModel,
    responses=open_api_config,
)
async def plan_deposit(
    request: Request,
    result: DepositPlanResponseModel = Depends(plan_deposit_handler),
) -> JSONResponse:
    await log_request(request)

    if result.error:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": result.message, "details": result.details},
        )
    return JSONResponse(content=result.model_dump())

