from typing import Dict, Optional, Union

from app.core.binance_spot_api.model import BinanceSpotKlineRequestConfig
from app.core.log.logger import Logger
from binance.spot import Spot

class BinanceSpotApiClient:
    """
    Binance Spot API Client
    """

    def __init__(
        self,
        spot_client: Spot,

    ) -> None:
        self.__spot_client = spot_client
        self.__logger = Logger(name=self.__class__.__name__)


    def get_default_klines_by_time_stamp_params(self) -> BinanceSpotKlineRequestConfig:
        return BinanceSpotKlineRequestConfig(
            interval="1m",
            limit=1,
        )

    def get_closed_price_by_timestamp(
        self,
        symbol: str,
        endTime: str,
    ) -> Dict:
        """
        Get klines by symbol

        Example Response:
        [
            [
                1591258320000,      	// Open time
                "9640.7",       	 	// Open
                "9642.4",       	 	// High
                "9640.6",       	 	// Low
                "9642.0",      	 	 	// Close (or latest price)
                "206", 			 		// Volume
                1591258379999,       	// Close time
                "2.13660389",    		// Base asset volume
                48,             		// Number of trades
                "119",    				// Taker buy volume
                "1.23424865",      		// Taker buy base asset volume
                "0" 					// Ignore.
            ]
        ]
        """

        try:
            if not isinstance(endTime, str) or len(str(endTime)) != 13:
                raise ValueError("endTime must be a 13-digit millisecond timestamp")
            
            defaultKlinesTimeStampParams = self.get_default_klines_by_time_stamp_params()

            result: list[list[Union[str, int]]] = self.__spot_client.klines(
                symbol=symbol.upper(),
                interval=defaultKlinesTimeStampParams.interval,
                limit=defaultKlinesTimeStampParams.limit,
                endTime=endTime,
            )
            return result
        except Exception as e:
            description = "Get klines by symbol failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            return []
        
    def get_klines_by_symbol(
        self,
        symbol: str,
        interval: str,
        limit: Optional[int] = None,
        startTime: Optional[int] = None,
        endTime: Optional[int] = None,
    ) -> Dict:
        """
        Get klines by symbol

        Example Response:
        [
            [
                1591258320000,      	// Open time
                "9640.7",       	 	// Open
                "9642.4",       	 	// High
                "9640.6",       	 	// Low
                "9642.0",      	 	 	// Close (or latest price)
                "206", 			 		// Volume
                1591258379999,       	// Close time
                "2.13660389",    		// Base asset volume
                48,             		// Number of trades
                "119",    				// Taker buy volume
                "1.23424865",      		// Taker buy base asset volume
                "0" 					// Ignore.
            ]
        ]
        """

        try:
            return self.__spot_client.klines(
                symbol=symbol.upper(),
                interval=interval,
                limit=limit,
                startTime=startTime,
                endTime=endTime,
            )
        except Exception as e:
            description = "Get klines by symbol failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Get klines by symbol failed"
            raise Exception(error_message) from e
