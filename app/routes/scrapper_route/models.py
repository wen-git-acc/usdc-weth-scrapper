

from datetime import datetime
from pydantic import BaseModel

from app.core.etherscan_http_client.model import EtherscanTransactionWithUsdtFee
from app.core.scrapper_service.model import TransactionSwapExecutionPrice



class TransactionPoolModelRequest(BaseModel):
    pool_name: str = ""
    pool_address: str = ""


class TokenPairPoolSchema(BaseModel):
    pool_id: int
    pool_name: str
    contract_address: str

    class Config:
        model_config = {'from_attributes': True}


class TokenPoolPairResponse(BaseModel):
    success: bool = False
    regitered_pool: list[TokenPairPoolSchema] = []


class GeneralResponse(BaseModel):
    message: str = ""

class TimeRangeRequest(BaseModel):
    pool_name: str
    start_time: datetime
    end_time: datetime

class TimeRangeResponse(BaseModel):
    pool_name: str = ""
    start_time: str = ""
    end_time: str = ""
    success: bool = False
    transactions: list[EtherscanTransactionWithUsdtFee] = []

class TransactionFeeWithHashResponse(BaseModel):
    message: str = ""
    tx_hash: str = ""
    pool_name: str = ""
    fee: str = ""

class UniswapUsdcWethExecutionPriceResponse(BaseModel):
    success: bool = False
    result: list[TransactionSwapExecutionPrice] = []