from atexit import register
from re import A
from time import sleep
from tracemalloc import start
from typing import Dict
from xml.dom.domreg import registered
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from httpx import get

from app.core.dependencies import get_binance_spot_client, get_etherscan_httpclient, get_scrapper_service
from app.core.config import app_config
from app.core.log.logger import Logger
from app.core.scrapper_service.model import TransactionSwapExecutionPrice
from app.routes.deposit_route.handler import plan_deposit_handler
from app.routes.deposit_route.models import DepositPlanResponseModel
from app.routes.deposit_route.response_config import open_api_config
import asyncio
from binance.spot import Spot

from app.routes.scrapper_route.models import GeneralResponse, TimeRangeRequest, TimeRangeResponse, TokenPairPoolSchema, TokenPoolPairResponse, TransactionFeeWithHashResponse, TransactionPoolModelRequest, UniswapUsdcWethExecutionPriceResponse
from app.storage.models import TransactionToFromPool
from datetime import datetime, timezone
from pydantic import BaseModel

scrapper_route = APIRouter()
running_tasks: Dict[str,asyncio.Event] = {}
logger = Logger(name="scrapper_route_controller")



async def log_request(request: Request) -> None:
    body_info = await request.body()
    logger.info(message={"body": body_info, "headers": request.headers})


@scrapper_route.get("/transaction/pool/existing",
                     response_model=TokenPoolPairResponse)
async def get_existing_transaction_pools(request: Request):
    await log_request(request)
    response = TokenPoolPairResponse()
    scrapper_client = get_scrapper_service()
    result = scrapper_client.get_all_token_pool_pair()
    registered_pool = []
    for pool in result:
        registered_pool.append(TokenPairPoolSchema.model_validate(pool.__dict__))
    response.regitered_pool = registered_pool
    response.success = True
    return JSONResponse(content=response.model_dump())


@scrapper_route.post("/transaction/pool/register",
                     response_model=GeneralResponse)
async def register_transaction(request: Request, pool_register_request: TransactionPoolModelRequest):
    try: 
        await log_request(request)
        scrapper_client = get_scrapper_service()

        if '/' in pool_register_request.pool_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pool name should not contain '/'"
            )
        
        scrapper_client.register_new_token_pool(
            pool_name=pool_register_request.pool_name.lower(),
            contract_address=pool_register_request.pool_address.lower(),
        )

        return JSONResponse(content={"message": "success"})
    except Exception as e:
        return JSONResponse(content={"message": f"No duplicate pool name and addrss allowed. {e!s}"}, status_code=500)
    




# @scrapper_route.get("/etherscan/tokentx/{pool_address}/latest")
# async def use_etherscan_client(_: Request, pool_address: str) -> JSONResponse:
#     # scrape_transactions_V2("uniswap/usdc/weth", asyncio.Event())
#     client = get_etherscan_httpclient()
#     response = client.get_latest_token_txs(pool_address)
#     scrapper_client = get_scrapper_service()
#     poolData = scrapper_client.get_token_pool_pair_by_address(pool_address)

#     if len(poolData) == 0:
#         return JSONResponse(content={"message": "pool not found"})
    
#     poolId = poolData[0].pool_id


#     latest = scrapper_client.read_latest_transaction_pool(pool_address, poolId)

#     # scrapper_client.scrape_first_block(
#     #     address=pool_address, 
#     #     token_pool_pair_id=poolId
#     #     )

#     # scrapper_client.scrape_job(address=pool_address)
#     return JSONResponse(content=response.model_dump())   
    


# @scrapper_route.get("/etherscan/tokentx/{pool_address}/{start_block}")
# async def use_etherscan_client(_: Request, pool_address: str, start_block: int) -> JSONResponse:
#     client = get_etherscan_httpclient()
#     response = client.get_token_txs_by_start_block(address=pool_address, start_block=start_block)

#     scrapper_client = get_scrapper_service()
#     scrapper_client.scrapping_job(address=pool_address, start_block=start_block)
#     # scrapper_client.scrape_first_block(address=pool_address)
#     return JSONResponse(content=response.model_dump())   
    


# @scrapper_route.get("/binance/spot/{symbol}/{timestamp}")
# async def use_binance_spot(symbol: str, timestamp: int) -> JSONResponse:
#     scrapper_client = get_scrapper_service()
#     result = scrapper_client.get_closed_price_by_timestamp(symbol=symbol, endTime=timestamp)
#     # print(client.get_klines_by_symbol(
#     #     symbol="ETHUSDT",
#     #     interval="1m",
#     #     limit=1,
#     #     endTime=1729824923000,
#     # ))
#     return JSONResponse(content=result.model_dump())

        

async def scrape_transactions(transaction_pair: str, stop_event: asyncio.Event) -> None:
    """
    This is the main function executed by the backgroudn tasks.
    """
    scrapper_client = get_scrapper_service()
    poolData = scrapper_client.get_token_pool_pair_by_pool_name(transaction_pair)

    if len(poolData) == 0:
        print(f"Stopped scraping for {transaction_pair}, due to pool not found.")
        return

    
    pool_id = poolData[0].pool_id
    address = poolData[0].contract_address

    latest_tx = scrapper_client.read_latest_transaction_pool(
        address=address,
        token_pool_pair_id=pool_id
    )

    if latest_tx == None:
        is_success = scrapper_client.insert_new_latest_transaction_pool(address, pool_id)

        if not is_success:
            # Catch by controller
            del running_tasks[transaction_pair]
            print(f"Stopped scraping for {transaction_pair}, due to first tx is not found.")
        
    
    # Start block for etherscan
    # Enter job scraping while first insert is success.
    print(f"Scraping transactions for {transaction_pair}...")
    while not stop_event.is_set():
        latest_tx = scrapper_client.read_latest_transaction_pool(
            address=address,
            token_pool_pair_id=pool_id
        )
        if isinstance(latest_tx, TransactionToFromPool):
            print(f"Transaction Pair: {transaction_pair},Latest block: {latest_tx.block_number}")
            start_block = latest_tx.block_number
            scrapper_client.scrapping_job(address=address, start_block=start_block, pool_id=pool_id)
            await asyncio.sleep(10)  # Simulate scraping delay

    print(f"Stopped scraping for {transaction_pair}.")


@scrapper_route.post("/start-task/{transaction_pair}",
                     response_model=GeneralResponse)
async def start_task(transaction_pair: str, background_tasks: BackgroundTasks):
    if transaction_pair in running_tasks:
        return {"message": f"Task for {transaction_pair} is already running."}
    
    scrapper_client = get_scrapper_service()
    poolData = scrapper_client.get_token_pool_pair_by_pool_name(transaction_pair)

    if len(poolData) == 0:
        return JSONResponse(content={"message": "Pool not found"}, status_code=404)
    
    # Create an asyncio Event to control task stopping
    stop_event = asyncio.Event()
    running_tasks[transaction_pair] = stop_event
    background_tasks.add_task(scrape_transactions, transaction_pair, stop_event)
    return GeneralResponse(
        message=f"Started task for {transaction_pair}"
    )

@scrapper_route.post("/stop-task/{transaction_pair}",
                     response_model=GeneralResponse)
async def stop_task(transaction_pair: str):
    stop_event = running_tasks.get(transaction_pair)
    if not stop_event:
        raise HTTPException(status_code=404, detail="Task not found for this pair.")

    # Signal the task to stop
    stop_event.set()
    del running_tasks[transaction_pair]
    return GeneralResponse(
        message=f"Stopped task for {transaction_pair}"
    )



@scrapper_route.post("/transaction/pool/timerange",
                        response_model=GeneralResponse)
async def get_transactions_in_time_range(request: Request, time_range_request: TimeRangeRequest) -> JSONResponse:
    result = TimeRangeResponse(
        pool_name=time_range_request.pool_name,
        start_time=time_range_request.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        end_time=time_range_request.end_time.strftime('%Y-%m-%d %H:%M:%S'),
    )
    try:
        await log_request(request)

        start_time = time_range_request.start_time
        end_time = time_range_request.end_time

        # Convert start and end times to UTC timestamps
        start_time_ts = int(start_time.timestamp())
        end_time_ts = int(end_time.timestamp())

        scrapper_client = get_scrapper_service()

        poolData = scrapper_client.get_token_pool_pair_by_pool_name(time_range_request.pool_name)
        if len(poolData) == 0:
            raise HTTPException(status_code=404, detail="Pool not found")

        transaction_list = scrapper_client.get_transaction_data_with_time_range(
            address=poolData[0].contract_address,
            start_time=start_time_ts,
            end_time=end_time_ts
        )

        result.success = True
        result.transactions = transaction_list

        return JSONResponse(content=result.model_dump())

    except Exception as e:
        return JSONResponse(content=result.model_dump(), status_code=404)
    

@scrapper_route.get("/transaction/fees/{tx_hash}",
                    response_model=TransactionFeeWithHashResponse)
async def get_transaction_fee(request: Request, tx_hash: str) -> JSONResponse:
    result = TransactionFeeWithHashResponse()
    try:
        await log_request(request)
        scrapper_client = get_scrapper_service()
        (fee, pool_name) = scrapper_client.get_transaction_fee_with_tx_hash(tx_hash)
        result.tx_hash = tx_hash
        result.pool_name = pool_name
        result.fee = fee

        if (fee == "0.00"):
            result.message = "Transaction not found, you might querying tx that is not in the database. (not recorded)"
        return JSONResponse(content=result.model_dump())
    except Exception as e:
        result.message = f"Error: {e!s}"
        return JSONResponse(content=result.model_dump(), status_code=404)
    
@scrapper_route.get("/transaction/{tx_hash}/{pool_name}/executed-price",
                    response_model=UniswapUsdcWethExecutionPriceResponse)
async def get_uniswap_executed_price(request: Request, tx_hash: str, pool_name: str) -> JSONResponse:
    try:
        await log_request(request)
        scrapper_client = get_scrapper_service()
        pool_data = scrapper_client.get_token_pool_pair_by_pool_name(pool_name)
        if len(pool_data) == 0:
            return JSONResponse(content={"message": "Pool not found"}, status_code=404)
        pool_address = pool_data[0].contract_address
        result = scrapper_client.get_decode_uniswap_v3_executed_price(tx_hash, pool_address)
        response = UniswapUsdcWethExecutionPriceResponse(
            success=True,
            result=result
        )
        return JSONResponse(content=response.model_dump())
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {e!s}"}, status_code=404)