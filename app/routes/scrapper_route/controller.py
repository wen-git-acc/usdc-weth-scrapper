from time import sleep
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.log.logger import Logger
from app.routes.deposit_route.handler import plan_deposit_handler
from app.routes.deposit_route.models import DepositPlanResponseModel
from app.routes.deposit_route.response_config import open_api_config
import asyncio

scrapper_route = APIRouter()
running_tasks: Dict[str,asyncio.Event] = {}
logger = Logger(name="scrapper_route_controller")

async def log_request(request: Request) -> None:
    body_info = await request.body()
    logger.info(message={"body": body_info, "headers": request.headers})

@scrapper_route.post(
    "/plan/deposit",
    response_model=DepositPlanResponseModel,
    responses=open_api_config,
)
async def plan_deposit(
    request: Request,
    # result: DepositPlanResponseModel = Depends(plan_deposit_handler),
) -> JSONResponse:
    await log_request(request)

    # if result.error:
    #     return JSONResponse(
    #         staatus_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={"message": result.message, "details": result.details},
    #     )

    return JSONResponse(content={"message": "success"})





# Scrapper Job Function
async def scrape_transactions(transaction_pair: str, stop_event: asyncio.Event):
    while not stop_event.is_set():
        print(f"Scraping transactions for {transaction_pair}...")
        await asyncio.sleep(5)  # Simulate scraping delay
    print(f"Stopped scraping for {transaction_pair}.")


@scrapper_route.post("/start-task/{transaction_pair}")
async def start_task(transaction_pair: str, background_tasks: BackgroundTasks):
    if transaction_pair in running_tasks:
        return {"message": f"Task for {transaction_pair} is already running."}

    # Create an asyncio Event to control task stopping
    stop_event = asyncio.Event()
    running_tasks[transaction_pair] = stop_event
    background_tasks.add_task(scrape_transactions, transaction_pair, stop_event)
    return {"message": f"Started task for {transaction_pair}"}

@scrapper_route.post("/stop-task/{transaction_pair}")
async def stop_task(transaction_pair: str):
    stop_event = running_tasks.get(transaction_pair)
    if not stop_event:
        raise HTTPException(status_code=404, detail="Task not found for this pair.")

    # Signal the task to stop
    stop_event.set()
    del running_tasks[transaction_pair]
    return {"message": f"Stopped task for {transaction_pair}"}