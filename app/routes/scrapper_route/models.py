

from pydantic import BaseModel



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