from typing import Dict, Optional
from urllib import response

from app.core.etherscan_http_client.model import EtherscanParams, EtherscanTxResponse
from app.core.log.logger import Logger
from binance.spot import Spot

from app.utils.http_client.base_class import HttpClient
from app.core.config import app_config

class EtherscanHttpclient:
    """
    Etherscan http client
    """

    def __init__(
        self,
        http_client: HttpClient,
        api_key: str,

    ) -> None:
        self.__http_client = http_client
        self.__logger = Logger(name=self.__class__.__name__)
        self.__api_key = api_key


    def get_default_latest_tokentx_etherscan_params(self) -> EtherscanParams:
        """
        Get default latest token transactions etherscan params
        """
        return EtherscanParams(
            module="account",
            action="tokentx",
            page=1,
            offset=2,
            sort="desc")
    
    def get_default_start_block_tokentx_etherscan_params(self) -> EtherscanParams:
        """
        Get default latest token transactions etherscan params
        """
        return EtherscanParams(
            module="account",
            action="tokentx",
            page=1,
            offset=100,
            sort="asc"
            )
    
    def get_latest_token_txs(
        self,
        address: str,
    ) -> EtherscanTxResponse:
        """
        Get latest token transactions
        """
        try:
            queryParams = self.get_default_latest_tokentx_etherscan_params()
            queryParams.address = address
            queryParams.apikey = self.__api_key

            with self.__http_client.get_session() as session:
                response_json = self.__http_client.get(session, params=queryParams.model_dump())
                return EtherscanTxResponse(**response_json)

        except Exception as e:
            description = "Get latest token transactions failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Get latest token transactions failed"
            raise Exception(error_message) from e

    def get_token_txs_by_start_block(
        self,
        address: str,
        start_block: int,
    ) -> EtherscanTxResponse:
        """
        Get token transactions by start block
        """
        try:
            queryParams = self.get_default_start_block_tokentx_etherscan_params()
            queryParams.address = address
            queryParams.startblock = start_block
            queryParams.apikey = self.__api_key

            with self.__http_client.get_session() as session:
                response_json = self.__http_client.get(session, params=queryParams.model_dump())
                return EtherscanTxResponse(**response_json)

        except Exception as e:
            description = "Get token transactions by start block failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Get token transactions by start block failed"
            raise Exception(error_message) from e
