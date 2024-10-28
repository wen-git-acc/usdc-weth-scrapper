from pydantic import BaseModel


class ClosedPriceResult(BaseModel):
    success: bool = False
    closed_price: str = ""

class TransactionFeeCalcResult(BaseModel):
    success: bool = False
    transaction_fee: str = ""

class TransactionSwapExecutionPrice(BaseModel):
    transaction_hash: str
    execution_price: str
    amount0: str
    amount1: str
    sender: str
    recipient: str

class TokenDetail(BaseModel):
    token_symbol: str
    is_received: bool
    is_zero: bool
    token_decimal: int
    token_amount: int