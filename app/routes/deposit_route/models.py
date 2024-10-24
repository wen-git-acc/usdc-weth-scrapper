from app.core.config import app_config
from pydantic import BaseModel
from typing import Literal

class BaseResponse(BaseModel):
    message: str = "Success"
    error: bool = False
    details: str = "" 

class MoneyBaseModel(BaseModel):
    amount: float = 0.00

class DepositDetail(MoneyBaseModel):
    reference_code: str = ""

class PortfolioDetails(MoneyBaseModel):
    portfolio_name: str = ""

class DepositPlan(BaseModel):
    portfolio_details: list[PortfolioDetails] = []
    plan_name: Literal["one-time", "monthly"] = ""


class DepositPlanRequestModel(BaseModel):
    deposit_plans: list[DepositPlan] = [DepositPlan(plan_name=app_config.one_time_plan_name), DepositPlan(plan_name=app_config.monthly_plan_name)]
    deposit_details: list[DepositDetail] = []


class DistributedFundResult(BaseModel):
    portfolio_distribution: list[PortfolioDetails] = []
    total_amount: float= 0.00
    reference_code: str= ""


class DepositPlanResponseModel (BaseResponse):
    result : DistributedFundResult = DistributedFundResult()

