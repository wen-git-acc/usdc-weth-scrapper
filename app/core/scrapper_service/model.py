from pydantic import BaseModel


class ClosedPriceResult(BaseModel):
    success: bool = False
    closed_price: str = ""

class TransactionFeeCalcResult(BaseModel):
    success: bool = False
    transaction_fee: str = ""