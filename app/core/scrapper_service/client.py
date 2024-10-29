from datetime import datetime
from decimal import Decimal
import decimal
from typing import Any, Dict, Optional, Tuple, Union
from unittest import result
from hexbytes import HexBytes
import requests
from web3 import Web3

from app.core.binance_spot_api.client import BinanceSpotApiClient
from app.core.etherscan_http_client.client import EtherscanHttpclient
from app.core.etherscan_http_client.model import EtherscanBlockNumberResponse, EtherscanProxyModuleResult, EtherscanTransaction, EtherscanTransactionWithUsdtFee
from app.core.scrapper_service.model import ClosedPriceResult, TokenDetail, TransactionFeeCalcResult, TransactionSwapExecutionPrice
from app.core.log.logger import Logger
from app.storage.token_pair_pools_repositories.client import TokenPairPoolsRepository
from app.storage.models import TokenPairPool
from app.storage.transactions_to_from_pools_repositories.client import TransactionToFromPoolRepository
from app.storage.models import TransactionToFromPool
from app.core.scrapper_service.abis import uniswap_v3_swap_abi
from app.core.config import app_config


class ScrapperService:
    def __init__(self, 
                 binance_spot_client: BinanceSpotApiClient, 
                 etherscan_client: EtherscanHttpclient, 
                 token_pair_pool_repo: TokenPairPoolsRepository, 
                 transaction_pool_repo: TransactionToFromPoolRepository,
                 web3py: Web3
                 ) -> None:
        self.__binance_spot_client = binance_spot_client
        self.__etherscan_client = etherscan_client
        self.__token_pair_pool_repo = token_pair_pool_repo
        self.__transaction_pool_repo = transaction_pool_repo
        self.__web3py = web3py
        self.__logger = Logger(name=self.__class__.__name__) 

    def get_token_txs_by_start_block(self, address: str, start_block: int) -> list[EtherscanTransaction]:
        result = self.__etherscan_client.get_token_txs_by_start_block(address, start_block)
        return result.result
    
    def get_latest_token_txs(self, address: str) -> list[EtherscanTransaction]:
        result = self.__etherscan_client.get_latest_token_txs(address)
        return result.result
    
    def get_closed_price_by_timestamp(self, symbol: str, endTime: str) -> ClosedPriceResult:
        kline_list = self.__binance_spot_client.get_closed_price_by_timestamp(symbol, endTime)

        if len(kline_list) == 0:
            log_message = "Closed price extraction failed, kline_list is empty"
            self.__logger.exception(log_message)
            return ClosedPriceResult()

        return self.get_closed_price_from_klines(kline_list[0])
    
    def scrapping_job(self, address: str, start_block: int, pool_id: int) -> bool:
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

            if len(transaction_to_be_insert) == app_config.scrapping_job_max_count_per_interval:
                break

        self.__transaction_pool_repo.insert_transaction_to_from_pool_data(transaction_to_be_insert)
        return True
    
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
        '''
        Placeholder, not in use
        '''
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
    
    def get_historical_transaction_data(
            self,
            address: str,
            start_time: int,
            end_time: int,
    ) -> list[EtherscanTransactionWithUsdtFee]:
        historical_start_block = self.__etherscan_client.get_closest_block_number_by_start_timestamp(start_time)
        historical_end_block = self.__etherscan_client.get_closest_block_number_by_end_timestamp(end_time)

        if historical_start_block.status != "1" or historical_end_block.status != "1":
            return []


        result = self.__etherscan_client.get_token_txs_by_start_and_end_block(
            address=address,
            start_block=int(historical_start_block.result),
            end_block=int(historical_end_block.result)
        )

        historical_tx = result.result
        processed_transactions = set()

        result_list: list[EtherscanTransactionWithUsdtFee] = []
        for tx in historical_tx:
            if tx.hash in processed_transactions:
                continue

            processed_transactions.add(tx.hash)

            transaction_fee = self.calculate_transaction_fee_in_usdt(tx)

            transformed_tx = EtherscanTransactionWithUsdtFee(
                **tx.model_dump(),
                usdt_fee=self.convert_str_decimal_to_two_decimal_point(transaction_fee.transaction_fee)
            )

            result_list.append(transformed_tx)
        
        return result_list
    
    def get_transaction_data_with_time_range(
            self,
            address: str,
            start_time: int,
            end_time: int,
    ) -> list[EtherscanTransactionWithUsdtFee]:

        historical_tx = self.get_historical_transaction_data(address, start_time, end_time)
        return historical_tx


    def get_transaction_fee_with_tx_hash(self, tx_hash: str) -> Tuple[str, str]:
        tx_db = self.__transaction_pool_repo.read_transaction_data_by_tx_hash([tx_hash])
        pool_name = ""
        if len(tx_db) == 0:
            return "0.00", pool_name
        
        pool_name_list = self.__token_pair_pool_repo.read_token_pool_pair_data_by_id([tx_db[0].pool_id])

        if len(pool_name_list) > 0:
            pool_name = pool_name_list[0].pool_name
        
        return self.convert_str_decimal_to_two_decimal_point(tx_db[0].transaction_fee_usdt), pool_name

    def get_decode_uniswap_v3_executed_price(self, tx_hash: str, contract_address: str) -> list[TransactionSwapExecutionPrice]:


        event_signature = Web3.keccak(
            text="Swap(address,address,int256,int256,uint160,uint128,int24)"
        ).hex()

        result : list[TransactionSwapExecutionPrice] = []

        receipt = self.__web3py.eth.get_transaction_receipt(tx_hash)
        for log in receipt.logs:
            if log["address"].lower() == contract_address.lower() and log["topics"][0].hex() == event_signature:  # Replace with actual Uniswap contract address
                try:
                    contract = self.__web3py.eth.contract(abi=uniswap_v3_swap_abi)
                    swap_events = contract.events.Swap()
                    # swap_events = self.__web3py.eth.contract(abi=uniswap_v3_swap_abi).events.Swap()
                    event_data = swap_events.process_log(log)
                    amount0 = event_data['args']['amount0']
                    amount1 = event_data['args']['amount1']
                    sqrtPriceX96 = event_data['args']['sqrtPriceX96']

                    (token_received, token_sent) = self.get_token_details(amount0, amount1)

                    decimal0 = token_received.token_decimal if token_received.is_zero else token_sent.token_decimal
                    decimal1 = token_received.token_decimal if token_sent.is_zero else token_sent.token_decimal

                    execution_price = self.calculate_price_from_sqrt_price_x96(sqrtPriceX96, decimal0, decimal1)
                    if (execution_price < 1):
                        execution_price = 1 / execution_price

                    result.append(TransactionSwapExecutionPrice(
                        transaction_hash=tx_hash,
                        execution_price=self.convert_str_decimal_to_two_decimal_point(str(execution_price)),
                        amount0=str(amount0),
                        amount1=str(amount1),
                        sender=event_data['args']['sender'],
                        recipient=event_data['args']['recipient'],
                    ))

                except Exception as e:
                    self.__logger.error(f"Error decoding log: {e}")
        return result
    

    def get_token_details(self, amount0: int, amount1: int) -> Tuple[TokenDetail, TokenDetail]:
        token_received = TokenDetail(
            token_symbol="",
            is_received=True,
            is_zero= False,
            token_decimal=0,
            token_amount=0
        )
        token_sent = TokenDetail(
            token_symbol="",
            is_received=False,
            is_zero= False,
            token_decimal=0,
            token_amount=0
        )

        if amount0 > 0:
            token_received.token_amount = amount0
            token_sent.token_amount = amount1
            token_received.is_zero = True
        else:
            token_received.token_amount = amount1
            token_sent.token_amount = amount0
            token_sent.is_zero = True

        if len(str(token_received.token_amount)) > len(str(token_sent.token_amount)):
            token_received.token_decimal = 18
            token_sent.token_decimal = 6
            token_received.token_symbol = "WETH"
            token_sent.token_symbol = "USDC"
        else:
            token_received.token_decimal = 6
            token_sent.token_decimal = 18
            token_received.token_symbol = "USDC"
            token_sent.token_symbol = "WETH"
            
        return token_received, token_sent

    def calculate_price_from_sqrt_price_x96(self, sqrt_price_x96: int, decimals0: int, decimals1: int) -> float:
        """Calculate actual price from sqrtPriceX96."""
        price = (sqrt_price_x96 ** 2) * (10 ** (decimals0 - decimals1)) / (2 ** 192)
        return price
    
    def convert_str_decimal_to_two_decimal_point(self, value: str) -> str:
        return "{:.2f}".format(float(value))
   
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
    
    def get_closed_price_from_klines(self, kline_data: list[Union[str, int]]) -> ClosedPriceResult:
        result = ClosedPriceResult()
        if len(kline_data) < 5:
            log_message = "Closed price extraction failed, kline_data must have at least 5 elements to extract close price"
            self.__logger.exception(log_message)
            return result
        
        result.success = not result.success
        result.closed_price = kline_data[4]

        return result

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