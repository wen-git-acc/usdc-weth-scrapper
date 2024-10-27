from sqlalchemy.orm import Session
from app.core.binance_spot_api.client import BinanceSpotApiClient
from app.core.etherscan_http_client.client import EtherscanHttpclient
from app.core.fund_allocator.client import FundAllocatorClient
from app.core.helper.client import HelperClient
from app.core.scrapper_service.client import ScrapperService
from app.storage.connection import get_session
from binance.spot import Spot
from app.core.config import app_config
from app.storage.token_pair_pools_repositories.client import TokenPairPoolsRepository
from app.storage.transactions_to_from_pools_repositories.client import TransactionToFromPoolRepository
from app.utils.http_client.client import ether_scan_client



# Singleton
helper_client = HelperClient()

# Scoped
def get_db_session() -> Session:
    return get_session()

def get_fund_allocator_client() -> FundAllocatorClient:
    return FundAllocatorClient(helper_client=helper_client)

def get_token_pair_pools_repo() -> TokenPairPoolsRepository:
    return TokenPairPoolsRepository(db_session=get_db_session)

def get_transaction_pool_repo() -> TransactionToFromPoolRepository:
    return TransactionToFromPoolRepository(db_session=get_db_session)

def get_binance_spot_client() -> BinanceSpotApiClient:
    # Initialize with api key and secret if required
    return BinanceSpotApiClient(
        # spot_client=Spot(timeout=1),
        spot_client=Spot(base_url=app_config.binance_spot_base_url, timeout=5),
    )

def get_etherscan_httpclient() -> EtherscanHttpclient:
    return EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key=app_config.etherscan_api_key,
    )

def get_scrapper_service() -> ScrapperService:
    return ScrapperService(
        binance_spot_client=get_binance_spot_client(),
        etherscan_client=get_etherscan_httpclient(),
        token_pair_pool_repo=get_token_pair_pools_repo(),
        transaction_pool_repo=get_transaction_pool_repo(),
    )
