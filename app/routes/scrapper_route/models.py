

from pydantic import BaseModel


class TransactionPoolModelRequest(BaseModel):
    pool_name: str = ""
    pool_address: str = ""