from calendar import month
import logging
import os
from configparser import ConfigParser, ExtendedInterpolation
from functools import lru_cache
from pathlib import Path

import typer
from pydantic_settings import BaseSettings

from app.core.log.logger import Logger


class AppConfig(BaseSettings):
    environment: str = "dev"

# Database
    postgres_db_user: str = os.environ.get("POSTGRES_DB_USER", "")
    postgres_db_password: str = os.environ.get("POSTGRES_DB_PASSWORD", "")
    postgres_db_host: str = ""
    postgres_db_port: int = 0
    postgres_db_name: str = ""
    postgres_max_overflow: int = 0
    postgres_pool_size: int = 0
    postgres_pool_timeout: int = 0
    postgres_pool_recycle: int = 0

    # Logging: DEBUG, INFO, WARNING, ERROR, EXCEPTION
    log_level: str = ""

    #Binance Spot Base Url
    binance_spot_base_url: str = "https://testnet.binance.vision"

    #EtherScan Base Url
    etherscan_base_url: str = "https://api.etherscan.io/api"
    etherscan_api_key: str = os.environ.get("ETHERSCAN_API_KEY", "")
    
    #Validator Node Url Provider
    validator_node_url_provider: str = os.environ.get("VALIDATOR_NODE_URL", "")

    #Scrapping Job Config
    scrapping_job_interval_seconds: int = 10
    scrapping_job_max_count_per_interval: int = 20

@lru_cache
def get_config(
    environment: str = os.environ.get("ENVIRONMENT", "dev"),
    secret_init_path: str = os.environ.get("SECRET_INI_PATH", "configs/secret.ini"),
) -> AppConfig:
    # parser will be used to contain the main overall rendered config
    parser = ConfigParser(interpolation=ExtendedInterpolation())

    config_paths = parser.read(
        [Path("configs/" + environment + ".ini")],
        encoding="utf-8",
    )

    # at this stage we haven't get the env var setup, so we cant use the global logger
    logger = Logger("config", logging.INFO)
    logger.info("Reading config from paths: %s", config_paths)

    output_dict = {}

    sections = parser.sections()
    for section in sections:
        output_dict.update(dict(parser.items(section)))

    return AppConfig(**output_dict)


# initialize the app config
app_config = get_config()

log_level = (
    getattr(logging, app_config.log_level)
    if hasattr(logging, app_config.log_level)
    else logging.INFO
)
logger = Logger("app", log_level)


def main(key: str) -> None:
    """Print config value of specified key."""
    typer.echo(app_config.dict().get(key))


if __name__ == "__main__":
    typer.run(main)
