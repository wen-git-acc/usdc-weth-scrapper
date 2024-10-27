

from pydantic import BaseModel


class BinanceSpotKlineRequestConfig(BaseModel):
    """
    Binance Spot Kline Request Config
    see: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
    start_time and end_time are in milliseconds
    """
    symbol: str = ""
    start_time: str = ""
    end_time: str = ""
    limit: int = 1
    interval: str = "1m"
