from pydantic import BaseModel, Field
from typing import Optional

class EtherscanParams(BaseModel):
    module: Optional[str] = None
    action: Optional[str] = None
    address: Optional[str] = None
    page: Optional[int] = None
    offset: Optional[int] = None
    sort: Optional[str] = None
    apikey: Optional[str] = None
    startblock: Optional[int] = None

class EtherscanTransaction(BaseModel):
    blockNumber: str = ""
    timeStamp: str = ""
    hash: str = ""
    nonce: str = ""
    blockHash: str = ""
    from_: str = Field("", alias="from")
    contractAddress: str = ""
    to: str = ""
    value: str = ""
    tokenName: str = ""
    tokenSymbol: str = ""
    tokenDecimal: str = ""
    transactionIndex: str = ""
    gas: str = ""
    gasPrice: str = ""
    gasUsed: str = ""
    cumulativeGasUsed: str = ""
    input: str = ""
    confirmations: str = ""

class EtherscanTxResponse(BaseModel):
    status: str
    message: str
    result: list[EtherscanTransaction]