from sqlalchemy.orm import Session
from app.core.fund_allocator.client import FundAllocatorClient
from app.core.helper.client import HelperClient
from app.storage.connection import get_session

# Singleton
helper_client = HelperClient()

# Scoped
def get_db_session() -> Session:
    return get_session()

def get_fund_allocator_client() -> FundAllocatorClient:
    return FundAllocatorClient(helper_client=helper_client)