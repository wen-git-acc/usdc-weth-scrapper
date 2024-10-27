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
    endblock: Optional[int] = None

class EtherscanParamsBlockModule(BaseModel):
    module: Optional[str] = "block"
    action: Optional[str] = "getblocknobytime"
    timestamp: Optional[int] = None
    closest: Optional[str] = "before"
    apikey: Optional[str] = None

class EtherscanParamsProxyModule(BaseModel):
    module: Optional[str] = "proxy"
    action: Optional[str] = "eth_getTransactionReceipt"
    apikey: Optional[str] = None
    txhash: Optional[str] = None

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

class EtherscanTransactionWithUsdtFee(EtherscanTransaction):
    usdt_fee: str = ""

class EtherscanTxResponse(BaseModel):
    status: str
    message: str
    result: list[EtherscanTransaction]

class EtherscanBlockNumberResponse(BaseModel):
    status: str
    message: str
    result: str

class EtherscanLog(BaseModel):
    address: str
    topics: list[str]
    data: str
    blockNumber: str
    transactionHash: str
    transactionIndex: str
    blockHash: str
    logIndex: str
    removed: bool

class EtherscanProxyModuleResult(BaseModel):
    blockHash: str
    blockNumber: str
    contractAddress: Optional[str]
    cumulativeGasUsed: str
    effectiveGasPrice: str
    from_: str = Field(..., alias="from")
    gasUsed: str
    logs: list[EtherscanLog]
    logsBloom: str
    status: str
    to: str
    transactionHash: str
    transactionIndex: str
    type: str

class EtherscanProxyModuleResponse(BaseModel):
    jsonrpc: str = ""
    id: int = ""
    result: EtherscanProxyModuleResult = None
