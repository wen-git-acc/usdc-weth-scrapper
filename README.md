# usdc-weth-scrapper

usdc-weth-scrapper is a long-polling job that scrape usdc/weth transaction data into db. Support data retrieval via fast api

## Case Scenario Assumption



## Test Set Up:

-Two Options-
1. Use PyTest.
2. Call the endpoint through swagger ui (http://localhost:8088/docs) or curl

```
curl -X 'POST' \
  'http://localhost:8088/plan/deposit' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "deposit_plans": [
    {
      "portfolio_details": [
        {
          "portfolio_name": "portfolio1",
          "amount": "10.56"
        },
        {
          "portfolio_name": "portfolio2",
          "amount": "550"
        }
      ],
      "plan_name": "one-time"
    },
    {
      "portfolio_details": [
        {
          "portfolio_name": "portfolio1",
          "amount": "10.20"
        },
        {
          "portfolio_name": "portfolio2",
          "amount": "100.50"
        },
        {
          "portfolio_name": "portfolio3",
          "amount": "100.50"
        }
      ],
      "plan_name": "monthly"
    }
  ],
  "deposit_details": [
    {
      "amount": "580",
      "reference_code": "asda"
    },
    {
      "amount": "100",
      "reference_code": "asda"
    }
  ]
}'
```

## Prerequisites

- Python 3.x
- Poetry
- venv

## Quick Start

```sh
# Setup tools needed and pre-commit hooks
$ make setup

# Create your own venv folder in workspace
$ python3 -m venv .venv

# Entering the Python virtual environment mode
$ poetry shell

# Install Python dependencies
$ poetry install

# Create a gitignored secret.ini, and fill in the required secrets for development
$ cp configs/secret.ini.example configs/secret.ini

# Run the application with hot reload/ or use debugger mode with launch.json setup below
$ make dev


## Useful commands

```sh
# Setup pre-commit hooks for linting and formatting checks
$ make pre-commit

# Run linting, formatting checks and auto-fixes
$ make format

# Run all unit tests with coverage report
$ make test

# Checkout all available commands
$ make help
```

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
    ├── .pre-commit-config.yaml   - Configuration file for pre-commit git hooks
    └── Makefile                  - Makefile for common commands

## Debugging


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
          "env": {}
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

# Run migrations
$ ./scripts/db.sh --up
```


## Docker setup
Remember to pass in your system user for dbhost and password else sqlalchemypkg container will use root user default to connect to db
If not running in container, switch host back to local host.