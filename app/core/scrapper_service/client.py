from decimal import Decimal
from typing import Union
from unittest import result
import requests

from app.core.binance_spot_api.client import BinanceSpotApiClient
from app.core.etherscan_http_client.client import EtherscanHttpclient
from app.core.etherscan_http_client.model import EtherscanTransaction
from app.core.scrapper_service.model import ClosedPriceResult, TransactionFeeCalcResult
from app.core.log.logger import Logger
from app.storage.token_pair_pools_repositories.client import TokenPairPoolsRepository
from app.storage.models import TokenPairPool
from app.storage.transactions_to_from_pools_repositories.client import TransactionToFromPoolRepository
from app.storage.models import TransactionToFromPool


class ScrapperService:
    def __init__(self, binance_spot_client: BinanceSpotApiClient, etherscan_client: EtherscanHttpclient, token_pair_pool_repo: TokenPairPoolsRepository, transaction_pool_repo: TransactionToFromPoolRepository) -> None:
        self.__binance_spot_client = binance_spot_client
        self.__etherscan_client = etherscan_client
        self.__token_pair_pool_repo = token_pair_pool_repo
        self.__transaction_pool_repo = transaction_pool_repo
        self.__logger = Logger(name=self.__class__.__name__) 

    def get_closed_price_by_timestamp(self, symbol: str, endTime: str) -> ClosedPriceResult:
        kline_list = self.__binance_spot_client.get_closed_price_by_timestamp(symbol, endTime)

        if len(kline_list) == 0:
            log_message = "Closed price extraction failed, kline_list is empty"
            self.__logger.exception(log_message)
            return ClosedPriceResult()

        return self.get_closed_price_from_klines(kline_list[0])

    def get_closed_price_from_klines(self, kline_data: list[Union[str, int]]) -> ClosedPriceResult:
        result = ClosedPriceResult()
        if len(kline_data) < 5:
            log_message = "Closed price extraction failed, kline_data must have at least 5 elements to extract close price"
            self.__logger.exception(log_message)
            return result
        
        result.success = not result.success
        result.closed_price = kline_data[4]

        return result
    
    def get_token_txs_by_start_block(self, address: str, start_block: int) -> list[EtherscanTransaction]:
        result = self.__etherscan_client.get_token_txs_by_start_block(address, start_block)
        return result.result
    
    def get_latest_token_txs(self, address: str) -> list[EtherscanTransaction]:
        result = self.__etherscan_client.get_latest_token_txs(address)
        return result.result

    def calculate_transaction_fee_in_eth(self, transaction: EtherscanTransaction) -> Decimal:
        """Calculate the transaction fee in ETH."""
        gas_used = Decimal(transaction.gasUsed)
        gas_price_in_wei = Decimal(transaction.gasPrice)
        # Convert gas price from wei to ETH
        gas_price_in_eth = gas_price_in_wei / Decimal(10**18)
        # Calculate transaction fee in ETH
        return gas_used * gas_price_in_eth
    

    def convert_timestamp_to_milliseconds(self, timestamp: str) -> str:
        return str(int(timestamp) * 1000)

    def calculate_transaction_fee_in_usdt(self, transaction: EtherscanTransaction) -> TransactionFeeCalcResult:
        """Calculate the transaction fee in USDT."""
        transaction_fee_in_eth = self.calculate_transaction_fee_in_eth(transaction)
        closed_price = self.get_closed_price_by_timestamp("ethusdt", self.convert_timestamp_to_milliseconds(transaction.timeStamp))

        if not closed_price.success:
            return TransactionFeeCalcResult()
        
        transaction_fee_in_usdt = transaction_fee_in_eth * Decimal(closed_price.closed_price)

        return TransactionFeeCalcResult(
            success=True,
            transaction_fee=str(transaction_fee_in_usdt)
        )
    
    def scrapping_job(self, address: str, start_block: int, pool_id: int) -> list[TransactionFeeCalcResult]:
        """transaction will ignore first block and duplicate block."""
        
        token_txs = self.get_token_txs_by_start_block(address, start_block)
        transaction_to_be_insert: list[TransactionToFromPool] = []
        processed_transactions = set()
        for tx in token_txs:
            if tx.blockNumber == str(start_block):
                continue 

            if tx.hash in processed_transactions:
                continue
            processed_transactions.add(tx.hash)
            transaction_fee = self.calculate_transaction_fee_in_usdt(tx)
            transformed_tx = self.convert_etherTx_to_transaction_repo(
                tx=tx,
                pool_id=pool_id,
                usdt_fee=transaction_fee.transaction_fee
            )
            transaction_to_be_insert.append(transformed_tx)

        self.__transaction_pool_repo.insert_transaction_to_from_pool_data(transaction_to_be_insert)
        return result
    
    
    def scrape_first_block(self, address: str, token_pool_pair_id: int) -> None:
        token_txs = self.get_latest_token_txs(address)
        if len(token_txs) == 0:
            return
        
        first_block_tx = token_txs[0]
        # get_latest = self.__transaction_pool_repo.get_latest_transaction_data_by_to_from_address_with_id(
        #     address=address,
        #     pool_id=token_pool_pair_id
        # )

        transaction_fee = self.calculate_transaction_fee_in_usdt(first_block_tx)    

        transform_first_block_tx = self.convert_etherTx_to_transaction_repo(
            tx=first_block_tx,
            pool_id=token_pool_pair_id,
            usdt_fee=transaction_fee.transaction_fee
        )

        self.__transaction_pool_repo.insert_first_transaction_to_from_pool_data([transform_first_block_tx])

    def insert_new_latest_transaction_pool(self, address: str, token_pool_pair_id: int) -> bool:
        try:
            token_txs = self.get_latest_token_txs(address)
            if len(token_txs) == 0:
                return False
            
            first_block_tx = token_txs[0]

            transaction_fee = self.calculate_transaction_fee_in_usdt(first_block_tx)    

            transform_first_block_tx = self.convert_etherTx_to_transaction_repo(
                tx=first_block_tx,
                pool_id=token_pool_pair_id,
                usdt_fee=transaction_fee.transaction_fee
            )

            self.__transaction_pool_repo.insert_first_transaction_to_from_pool_data([transform_first_block_tx])

            return True

        except Exception as e:
            description = "Insert new latest transaction pool failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            return False


 
    # def scrape_job(self, address: str) -> None:
    #     poolData = self.get_token_pool_pair_by_address(address)

    #     if len(poolData) == 0:
    #         raise Exception("Pool not found")
        
    #     pool_id = poolData[0].pool_id

    #     existing_list = self.__transaction_pool_repo.read_transaction_data_by_to_from_address(
    #         address=address,
    #         pool_id=pool_id
    #     )

    #     if len(existing_list) == 0:
    #         return self.insert_new_latest_transaction_pool(address, pool_id)
        
    #     else



    #     return

    def read_latest_transaction_pool(self, address: str, token_pool_pair_id: int) -> TransactionToFromPool | None:
        latest = self.__transaction_pool_repo.get_latest_transaction_data_by_to_from_address_with_id(
            address=address,
            pool_id=token_pool_pair_id
        )
        return latest

    def get_all_token_pool_pair(self) -> list[TokenPairPool]:
        all_token_pool_pair = self.__token_pair_pool_repo.read_all_token_pool_pairs()

        if len(all_token_pool_pair) == 0:
            return []
        
        return all_token_pool_pair
    
    def get_token_pool_pair_by_address(self, address: str) -> list[TokenPairPool]:
        token_pool_pair = self.__token_pair_pool_repo.read_token_pool_pair_by_address(address)

        if len(token_pool_pair) == 0:
            return []
        
        return token_pool_pair

    def get_token_pool_pair_by_pool_name(self, pool_name: str) -> list[TokenPairPool]:
        token_pool_pair = self.__token_pair_pool_repo.get_token_pool_pair_by_pool_name(pool_name)

        if len(token_pool_pair) == 0:
            return []
        
        return token_pool_pair

    def register_new_token_pool(self, pool_name:str, contract_address: str) -> None:
        token_pair_pool_data = TokenPairPool(
            pool_name=pool_name,
            contract_address=contract_address,
        )        
        self.__token_pair_pool_repo.insert_token_pair_pool_data([token_pair_pool_data]) 
    


    def convert_etherTx_to_transaction_repo(self, tx: EtherscanTransaction, pool_id: int, usdt_fee: str) -> TransactionToFromPool:
        return TransactionToFromPool(
            block_number=int(tx.blockNumber),
            ts_timestamp=int(tx.timeStamp),
            tx_hash=tx.hash,
            from_address=tx.from_,
            to_address=tx.to,
            contract_address=tx.contractAddress,
            token_value=tx.value,
            token_name=tx.tokenName,
            token_symbol=tx.tokenSymbol,
            token_decimal=tx.tokenDecimal,
            transaction_index=tx.transactionIndex,
            gas_limit=tx.gas,
            gas_price=tx.gasPrice,
            gas_used=tx.gasUsed,
            cumulative_gas_used=tx.cumulativeGasUsed,
            confirmations=tx.confirmations,
            transaction_fee_usdt=usdt_fee,
            pool_id=pool_id,
        )