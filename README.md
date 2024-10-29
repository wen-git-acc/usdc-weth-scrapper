# usdc-weth-scrapper

usdc-weth-scrapper is a backservice to interact with etherscan and receive transaction details of a wallet address. It has capibility like:
- Endpoint to start long-polling job that scrape transaction data into db, also, calculate the transactoin fee (USDT). 
- Endpoint to stop the polling job.
- Endpoint to register address with transaction you want to scrape. 
- Endpoint to check all registered address.
- Endpoint to receive transaction fee from recorded transaction based on transaction hx. 
- Endpoint to receive historical transaction detail with transaction fee based on timerange and wallet address given (registered address pool name)
- Endpoint to receive execution price based on transaction hx for USDC/WETH Pool UniswapV3. But first you need to register this address with the registered endpoint

## Overview

For more information refer to [api endpoints](#api-endpoints) and [how to start?](#how-to-start)

I'm excited to share that I've developed a robust REST API designed for transaction scraping, focusing on the Uniswap ecosystem. This API includes several key features:

### Start and Stop Scraping Jobs:
You can easily manage your scraping tasks with endpoints to start and stop jobs for transaction scraping. This ensures you have full control over the data retrieval process.

### Retrieve Transaction Fees:
There's an endpoint specifically for retrieving transaction fees based on transaction hashes, allowing you to access vital information quickly.

### Get Transactions by Time Range:
The API provides functionality to query transactions within a specified time range, facilitating historical data analysis.

### Executed Price Retrieval:
You can fetch executed prices for transactions, enhancing your understanding of transaction dynamics.

### Reliability and Scalability
My system has been thoroughly tested for reliability, ensuring consistent performance even under varying loads. Moreover, the scraping capabilities are not limited to just the USDC/WETH pool; with sufficient CPU and worker resources, you can scrape additional token pools as needed. You can also register new pool pairs using the dedicated registration endpoint.

### Bonus Features
In addition to the primary requirements, I've designed the API to be extensible and scalable. The architecture allows for real-time data recording alongside historical batch processing, ensuring comprehensive coverage of Uniswap transactions.

### Testing and Documentation
The API is accompanied by a comprehensive test suite, adhering to software engineering best practices, which guarantees the quality of the code. Additionally, I've included detailed documentation in the README file, making it easy to build, test, and run the application.

## Test Set Up:

Thorough test suite is created for main class that hold all the logic for this scrapping task `./tests`.

To run test cases: <br><br>

For testing, you may use vscode default test extension or run command below at root directory ```.```

```sh
pytest
```

## Prerequisites

- Python 3.x
- Poetry
- venv

Run the command below to install neccessary dependencies.

```sh

# Create your own venv folder in workspace
$ python3 -m venv .venv

# Entering the Python virtual environment mode
$ poetry shell

# Install Python dependencies
$ poetry install

# Run the application with hot reload/ or use debugger mode with launch.json setup below
$ make dev

```

## API Endpoints

### 1. Get Existing Transaction Pools
**GET** `/transaction/pool/existing`  
**Response Model:** `TokenPoolPairResponse`  
**Description:** Retrieves all existing token pools.

---

### 2. Register Transaction Pool
**POST** `/transaction/pool/register`  
**Request Body:** `TransactionPoolModelRequest`  
**Response Model:** `GeneralResponse`  
**Description:** Registers a new token pool. The pool name must not contain '/'.

---

### 3. Start Scraping Task
**POST** `/start-task/{transaction_pair}`  
**Response Model:** `GeneralResponse`  
**Description:** Starts a background task to scrape transactions for a specified transaction pair. Returns a message if the task is already running.

---

### 4. Stop Scraping Task
**POST** `/stop-task/{transaction_pair}`  
**Response Model:** `GeneralResponse`  
**Description:** Stops the background scraping task for the specified transaction pair.

---

### 5. Get Transactions in Time Range
**POST** `/transaction/pool/timerange`  
**Request Body:** `TimeRangeRequest`  
**Response Model:** `GeneralResponse`  
**Description:** Retrieves transactions for a specified pool within a given time range.

---

### 6. Get Transaction Fee by Hash
**GET** `/transaction/fees/{tx_hash}`  
**Response Model:** `TransactionFeeWithHashResponse`  
**Description:** Retrieves the transaction fee for a specified transaction hash.

---

### 7. Get Uniswap Executed Price
**GET** `/transaction/{tx_hash}/{pool_name}/executed-price`  
**Response Model:** `UniswapUsdcWethExecutionPriceResponse`  
**Description:** Retrieves the executed price for a transaction in the Uniswap v3 USDC/WETH pool.

---

## Quick Start

The backend instance is dockerize into ```./docker-compose.yml```, hence, run `docker-compose up` at the root folder `./`. This project include the use of psotgresql, hence make sure set everything up according to instruction, hereafter.

### Step 1 (Environment Variable Setup):

Navigate to `./docker-compose.yml` and fill up environment variable value, which are api keys that need to connect with Etherscan, web3py (alchemy or infura) and postgresql username or password. 

Note: If you did not set up db username after installation, the db user name will be your system user name.

You will see following environment to be filled:

- ETHERSCAN_API_KEY - api key to connect to etherscan client
- VALIDATOR_NODE_URL - alchemy or infura node url
- POSTGRES_DB_PASSWORD - local db password, leave empty if passwordless
- POSTGRES_DB_USER - local db username, most likely system user if you did not explicitly set previously. 


### Step 2 (DB Setup): 

Postgresql is use in this project, make sure it is no user and password by default.
If your db has password please correct the command in `db.py` as needed.
Username is not needed as sqlalchemy package will you default system user. Caveat, you still need to fill up `POSTGRES_DB_USER` for dockerize service.
Run postgresql db migration according to [Data base migration guide](#database-migrations). In short, run the sh command and the root folder `./`

### Step 3 (Run the service).

build and run your docker image using: <br>

```sh
docker-compose up
```

#### Althernative (not running with docker) 

Refer to below or using debugger mode by importing [launch.json](#with-vscode)

Note: If runnong locally instead of docker, you must pass in your db host with localhost instead of host.docker.internal

### Step 4:

Start playing! Once start,  call the endpoint through swagger ui [api documentation](#api-documentation) or curl. <br>

## How to start?

### Registration
User have to register the contract address, e.g. (Uniswap V3 USDC/WETH), with name using the register endpoint.

- pool name: usdc_weth
- contract address: 0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640

There are two important endpoint:
- [get registered pool](#1-get-existing-transaction-pools)
- [register transaction pool](#2-register-transaction-pool)

Note: The registered **Pool Name** is needed for most of the endpoint.

### Start and Stop Job
In brief, two endpoints is provided to start and end job, the job will run continuously to scrape the pool transaction detail now and future (not historical), calculate the transaction fee (usdt) and record into databse:

- [Start Job](#3-start-scraping-task)
- [Stop Job](#4-stop-scraping-task)

Note: Remember pool name registered previously will be needed.

### Retrieve historical Data based on Time Range
In brief, one endpoint is provided to retrieve transaciton data with calculated usdt transaction fee when time range is given, in the format of ISO 8601. 

- [Transaction by time range](#5-get-transactions-in-time-range)

### Retrieve transaction fee with transaction hash.
One endpoint is provided for user to retrieve RECORDED usdt transaction fee by passing transaction hash. Historical transaction fee is not supported

- [Recorded transaction fee](#6-get-transaction-fee-by-hash)

### Retrieve executed price
Currently, there is one endpoint to retrieve executed price of Uniswap V3 USDC/WETH transactions. Registered pool name and transaction hash must be provide in this endpoint. Currently only support 1 pool, hence, you must always pass in the pool name of this contract address (0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640).

- [Get Executed Price for Uniswap V3 USDC/WETH](#7-get-uniswap-executed-price)


## API Documentation

> Swagger <http://localhost:8088/docs>
> Redoc <http://localhost:8088/redoc>




## Project structure

    ├── app                       - Application source code
    │   ├── core                  - Application configuration, startup events, logging.
    │   ├── routes                - API endpoints and request handlers.
    │   ├── storage               - Storage handlers including connection and table models   
    │   ├── server.py             - FastAPI application creation and configuration.
    ├── configs                   - Configuration files for the application.
    ├── scripts                   - Scripts used for various purposes.
    ├── tests                     - Testing files for unit test and test cases - pytest
    │   └── unit_tests            - Unit tests - pytest
    ├── Dockerfile                - Dockerfile for building the image
    ├── docker-compose.yml        - Docker compose to spin up container
    └── Makefile                  - Makefile for common commands


### With VSCode

1. Install the Python extension for VSCode.
   <https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy>

2. Add the following configuration to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug App",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.server:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8088",
                "--reload"
            ],
            "env": {
                "ETHERSCAN_API_KEY": "",
                "VALIDATOR_NODE_URL": "",
                "POSTGRES_DB_PASSWORD": "",
                "POSTGRES_DB_USER":"",
            }
        }
    ]
  }
```
3. Add the following testing configuration to `settings.json` user/workspace/default

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["--no-cov"],
}
```

### Database migrations

The setup is identical to Grab-kit's database migrations. You can run the following commands to create and run migrations.

```shell
# One time setup
$ ./scripts/db.sh --create

# Run migrations to create table
$ ./scripts/db.sh --up

# Run migrations to reverse implementation
$ ./scripts/db.sh --down
```
