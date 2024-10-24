from app.core.log.logger import Logger

from fastapi import Depends
from fastapi.responses import JSONResponse

from app.core.dependencies import get_fund_allocator_client
from app.core.fund_allocator.client import FundAllocatorClient
from app.routes.deposit_route.models import DepositPlanRequestModel, DepositPlanResponseModel
from app.routes.utils import get_exception_action_response


logger = Logger(name="deposit_plan_route_controller")

def plan_deposit_handler(
        request: DepositPlanRequestModel,
        fund_allocator: FundAllocatorClient = Depends(get_fund_allocator_client),
) -> DepositPlanResponseModel:
    response = DepositPlanResponseModel()

    try:
        # Check if deposit plan or deposit detail is empty
        if len(request.deposit_details) == 0 or len(request.deposit_plans) == 0:
            raise ValueError("Deposit plan or deposit detail is empty.")
        
        # Maximum plan is two, one-time and monthly
        if len(request.deposit_plans) > 2:
            raise ValueError("Deposit plan is more than 2.")
        
        result = fund_allocator.distribute_funds(deposit_plans=request.deposit_plans, deposit_details=request.deposit_details)
        response.result = result

        return response

    except Exception as e:
        response.message = str(e)
        return get_exception_action_response(
            e=e, logger=logger, name=plan_deposit_handler.__name__, response=response
        )
