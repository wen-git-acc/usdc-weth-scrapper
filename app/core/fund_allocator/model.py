from decimal import Decimal
from pydantic import BaseModel

class DepositPlanDetail(BaseModel):
    portfolio_names: list[str] = []
    individual_amount: list[Decimal] = [] 
    total_amount: Decimal = Decimal('0.00')
