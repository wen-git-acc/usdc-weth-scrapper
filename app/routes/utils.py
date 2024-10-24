from pydantic import BaseModel

from app.core.log.logger import Logger
from app.routes.deposit_route.models import DepositPlanResponseModel


class BaseResponse(BaseModel):
    message: str = "Success"
    error: bool = False
    details: str = ""


def get_exception_action_response(
    e: Exception,
    logger: Logger,
    name: str,
    response: DepositPlanResponseModel,
) -> DepositPlanResponseModel:

    logger.info(" ".join([f"{name} Error:", str(e)]))

    response.details = e.args[0] if len(e.args) != 0 else str(e)
    response.error = True

    return response

