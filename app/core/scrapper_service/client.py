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
from app.storage.token_pair_pools_repositories.model import TokenPairPool
from app.storage.transactions_to_from_pools_repositories.client import TransactionToFromPoolRepository
from app.storage.transactions_to_from_pools_repositories.model import TransactionToFromPool


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
    
    def scrapping_job(self, address: str, start_block: int) -> list[TransactionFeeCalcResult]:
        """transaction will ignore first block and duplicate block."""
        
        token_txs = self.get_token_txs_by_start_block(address, start_block)
        result = []
        processed_transactions = set()
        for tx in token_txs:
            if tx.blockNumber == str(start_block):
                continue 

            if tx.hash in processed_transactions:
                continue
            processed_transactions.add(tx.hash)
            transaction_fee = self.calculate_transaction_fee_in_usdt(tx)
            result.append(transaction_fee)

        return result
    
    def scrape_first_block(self, address: str) -> None:
        token_txs = self.get_latest_token_txs(address)
        if len(token_txs) == 0:
            return
        
        first_block_tx = token_txs[0]

        transaction_fee = self.calculate_transaction_fee_in_usdt(first_block_tx)    
        transaction_repo = self.convert_etherTx_to_transaction_repo(first_block_tx, transaction_fee.transaction_fee)

        self.__transaction_pool_repo.insert_transaction_to_from_pool_data([transaction_repo])
        # first_block = token_txs[0].blockNumber
        # self.scrapping_job(address, first_block)


    def register_new_token_pool(self, pool_name:str, contract_address: str) -> None:
        token_pair_pool_data = TokenPairPool(
            pool_name=pool_name,
            contract_address=contract_address,
        )        
        self.__token_pair_pool_repo.insert_token_pair_pool_data([token_pair_pool_data]) 
    


    def convert_etherTx_to_transaction_repo(self, tx: EtherscanTransaction, usdt_fee: str) -> TransactionToFromPool:
        return TransactionToFromPool(
            block_number=tx.blockNumber,
            ts_timestamp=tx.timeStamp,
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
        )