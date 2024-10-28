
import re
import token
from typing import Dict
from unittest.mock import MagicMock
import binance
from binance.spot import Spot
from hexbytes import HexBytes
from httpx import get
from openai import base_url
from pydantic import BaseModel
from sqlalchemy import Transaction
from app.core import etherscan_http_client
from app.core.binance_spot_api.client import BinanceSpotApiClient
from app.core.etherscan_http_client.client import EtherscanHttpclient
from app.core.etherscan_http_client.model import EtherscanBlockNumberResponse, EtherscanTransaction, EtherscanTxResponse
from app.core.scrapper_service.client import ScrapperService
from app.storage.models import TokenPairPool, TransactionToFromPool
from app.storage.token_pair_pools_repositories.client import TokenPairPoolsRepository
from app.storage.transactions_to_from_pools_repositories.client import TransactionToFromPoolRepository
from app.utils.http_client.client import ether_scan_client
from web3 import Web3
from web3.types import TxReceipt
from app.core.scrapper_service.abis import uniswap_v3_swap_abi



def test_scrapper_service_get_latest_token_txs_return_correct_value() -> None:
    etherscan_http_client = EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key="",
    )

    etherscan_http_client.get_latest_token_txs = MagicMock(return_value=
        EtherscanTxResponse(
            status= "1",
            message="OK",
            result=[
                EtherscanTransaction(
                    blockNumber="12345678"
                )
            ]
        )
    )
    
    client =  ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=etherscan_http_client,
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )
    
    result = client.get_latest_token_txs("0x12345678")
    assert len(result) == 1

    tx = result[0]
    assert tx.blockNumber == "12345678"
    
def test_scrapper_service_get_token_txs_by_start_block_correct_value() -> None:
    etherscan_http_client = EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key="",
    )

    etherscan_http_client.get_token_txs_by_start_block = MagicMock(return_value=
        EtherscanTxResponse(
            status="1",
            message="OK",
            result=[
                EtherscanTransaction(
                    blockNumber="12345678"
                ),
                EtherscanTransaction(
                    blockNumber="12345679"
                )
            ]
        )
    )

    client = ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=etherscan_http_client,
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )

    result = client.get_token_txs_by_start_block("0x12345678", "12345678")
    assert len(result) == 2

    tx1 = result[0]
    tx2 = result[1]

    assert tx1.blockNumber == "12345678"
    assert tx2.blockNumber == "12345679"

def test_get_closed_price_by_timestamp_correct_value() -> None:
    binance_spot_client = BinanceSpotApiClient(
        spot_client=Spot(base_url=base_url, timeout=5),
    )

    binance_spot_client.get_closed_price_by_timestamp = MagicMock(return_value=[
        [
            123456789,  # Open time
            "0.0010",   # Open
            "0.0020",   # High
            "0.0005",   # Low
            "0.0015",   # Close
            "1000",     # Volume
            123456799,  # Close time
            "1.5",      # Quote asset volume
            100,        # Number of trades
            "500",      # Taker buy base asset volume
            "0.75",     # Taker buy quote asset volume
            "0"         # Ignore
        ]
    ])

    client = ScrapperService(
        binance_spot_client=binance_spot_client,
        etherscan_client=MagicMock(),
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )

    result = client.get_closed_price_by_timestamp("BTCUSDT", 123456789)
    assert result.closed_price == "0.0015"


def get_client_with_fully_mocked_properties() -> ScrapperService:
    return ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=MagicMock(),
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )


def test_get_token_details_with_correct_value():
    client = get_client_with_fully_mocked_properties()

    (token_received, token_sent) = client.get_token_details(12345,-123)
    assert token_received.token_amount == 12345
    assert token_received.token_symbol == "WETH"
    assert token_received.token_decimal == 18


    assert token_sent.token_amount == -123
    assert token_sent.token_symbol == "USDC"
    assert token_sent.token_decimal == 6

    (token_received, token_sent) = client.get_token_details(-12345,123)
    assert token_sent.token_amount == -12345
    assert token_sent.token_symbol == "WETH"
    assert token_sent.token_decimal == 18

    assert token_received.token_amount == 123
    assert token_received.token_symbol == "USDC"
    assert token_received.token_decimal == 6

    (token_received, token_sent) = client.get_token_details(-123,12345)
    assert token_sent.token_amount == -123
    assert token_sent.token_symbol == "USDC"
    assert token_sent.token_decimal == 6

    assert token_received.token_amount == 12345
    assert token_received.token_symbol == "WETH"
    assert token_received.token_decimal == 18

    (token_received, token_sent) = client.get_token_details(123,-12345)
    assert token_received.token_amount == 123
    assert token_received.token_symbol == "USDC"
    assert token_received.token_decimal == 6

    assert token_sent.token_amount == -12345
    assert token_sent.token_symbol == "WETH"
    assert token_sent.token_decimal == 18

def test_calculate_price_from_sqrt_price_x96_with_correct_input () -> None:
    client = get_client_with_fully_mocked_properties()
    expected_result = 1.5930919111324522e-20
    result = client.calculate_price_from_sqrt_price_x96(10000000000000,18,6)
    assert result == expected_result

def test_convert_str_decimal_to_two_decimal_with_correct_input () -> None:
    client = get_client_with_fully_mocked_properties()
    expected_result = "0.00"
    result = client.convert_str_decimal_to_two_decimal_point("0.000000")
    assert result == expected_result

def test_convert_etherTx_to_transaction_repo_with_correct_value() -> None:
    client = get_client_with_fully_mocked_properties()
    tx = EtherscanTransaction(
        blockNumber = "12345",
        timeStamp = "123",
        hash = "123",
        nonce = "123",
        blockHash = "123",
        from_ = "a",
        contractAddress = "b",
        to = "c",
        value = "123",
        tokenName = "123",
        tokenSymbol = "123",
        tokenDecimal = "123",
        transactionIndex = "123",
        gas = "123",
        gasPrice = "123",
        gasUsed = "123",
        cumulativeGasUsed = "123",
        input = "123",
        confirmations = "123"
    )

    pool_id = 1
    usdt_fee = "0.001"

    result = client.convert_etherTx_to_transaction_repo(tx, pool_id, usdt_fee)

    assert result.block_number == int(tx.blockNumber)
    assert result.ts_timestamp == int(tx.timeStamp)
    assert result.tx_hash == tx.hash
    assert result.from_address == tx.from_
    assert result.to_address == tx.to
    assert result.contract_address == tx.contractAddress
    assert result.token_value == tx.value
    assert result.token_name == tx.tokenName
    assert result.token_symbol == tx.tokenSymbol
    assert result.token_decimal == tx.tokenDecimal
    assert result.transaction_index == tx.transactionIndex
    assert result.gas_limit == tx.gas
    assert result.gas_price == tx.gasPrice
    assert result.gas_used == tx.gasUsed
    assert result.cumulative_gas_used == tx.cumulativeGasUsed
    assert result.confirmations == tx.confirmations
    assert result.transaction_fee_usdt == usdt_fee
    assert result.pool_id == pool_id

def test_get_closed_price_from_klines_with_correct_value() -> None:
    client = get_client_with_fully_mocked_properties()

    klines = [
            123456789,  # Open time
            "0.0010",   # Open
            "0.0020",   # High
            "0.0005",   # Low
            "0.0015",   # Close
            "1000",     # Volume
            123456799,  # Close time
            "1.5",      # Quote asset volume
            100,        # Number of trades
            "500",      # Taker buy base asset volume
            "0.75",     # Taker buy quote asset volume
            "0"         # Ignore
        ]
    

    result = client.get_closed_price_from_klines(klines)
    assert result.closed_price == "0.0015"
    assert result.success

    klines = []

    result = client.get_closed_price_from_klines(klines)
    assert result.closed_price == ""
    assert not result.success

def test_calcualte_transaction_fee_in_eth() -> None:
    client = get_client_with_fully_mocked_properties()
    tx = EtherscanTransaction(
        blockNumber = "12345",
        timeStamp = "123",
        hash = "123",
        nonce = "123",
        blockHash = "123",
        from_ = "a",
        contractAddress = "b",
        to = "c",
        value = "123",
        tokenName = "123",
        tokenSymbol = "123",
        tokenDecimal = "123",
        transactionIndex = "123",
        gas = "123",
        gasPrice = "123",
        gasUsed = "123",
        cumulativeGasUsed = "123",
        input = "123",
        confirmations = "123"
    )
    result = client.calculate_transaction_fee_in_eth(tx)
    assert str(result) == '1.5129E-14'

def test_convert_timestamp_to_milliseconds_with_correct_value() -> None:
    client = get_client_with_fully_mocked_properties()
    timestamp = 123456789
    result = client.convert_timestamp_to_milliseconds(str(timestamp))
    assert result == str(123456789000)

def test_calculate_transaction_fee_in_usdt() -> None:

    binance_spot_client = BinanceSpotApiClient(
        spot_client=Spot(base_url=base_url, timeout=5),
    )

    binance_spot_client.get_closed_price_by_timestamp = MagicMock(return_value=[
        [
            123456789,  # Open time
            "0.0010",   # Open
            "0.0020",   # High
            "0.0005",   # Low
            "0.0015",   # Close
            "1000",     # Volume
            123456799,  # Close time
            "1.5",      # Quote asset volume
            100,        # Number of trades
            "500",      # Taker buy base asset volume
            "0.75",     # Taker buy quote asset volume
            "0"         # Ignore
        ]
    ])

    client = ScrapperService(
        binance_spot_client=binance_spot_client,
        etherscan_client=MagicMock(),
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )
    tx = EtherscanTransaction(
        blockNumber = "12345",
        timeStamp = "123",
        hash = "123",
        nonce = "123",
        blockHash = "123",
        from_ = "a",
        contractAddress = "b",
        to = "c",
        value = "123",
        tokenName = "123",
        tokenSymbol = "123",
        tokenDecimal = "123",
        transactionIndex = "123",
        gas = "123",
        gasPrice = "123",
        gasUsed = "123",
        cumulativeGasUsed = "123",
        input = "123",
        confirmations = "123"
    )
    result = client.calculate_transaction_fee_in_usdt(tx)
    assert result.transaction_fee == '2.26935E-17'


def test_scrapping_job_return_true() -> None:
    ethercan_http_client = EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key="",
    )

    binance_spot_client = BinanceSpotApiClient(
        spot_client=Spot(base_url=base_url, timeout=5),
    )

    transaction_pool_repo = TransactionToFromPoolRepository(
        db_session=MagicMock(),
    )

    ethercan_http_client.get_token_txs_by_start_block = MagicMock(
        return_value= EtherscanTxResponse(
            status="1",
            message="OK",
            result=[
                EtherscanTransaction(
                    blockNumber = "12345",
                    timeStamp = "123",
                    hash = "123",
                    nonce = "123",
                    blockHash = "123",
                    from_ = "a",
                    contractAddress = "b",
                    to = "c",
                    value = "123",
                    tokenName = "123",
                    tokenSymbol = "123",
                    tokenDecimal = "123",
                    transactionIndex = "123",
                    gas = "123",
                    gasPrice = "123",
                    gasUsed = "123",
                    cumulativeGasUsed = "123",
                    input = "123",
                    confirmations = "123"
                ),
                EtherscanTransaction(
                    blockNumber = "123456",
                    timeStamp = "123",
                    hash = "123",
                    nonce = "123",
                    blockHash = "123",
                    from_ = "a",
                    contractAddress = "b",
                    to = "c",
                    value = "123",
                    tokenName = "123",
                    tokenSymbol = "123",
                    tokenDecimal = "123",
                    transactionIndex = "123",
                    gas = "123",
                    gasPrice = "123",
                    gasUsed = "123",
                    cumulativeGasUsed = "123",
                    input = "123",
                    confirmations = "123"
                )
            ]
        )
    )

    binance_spot_client.get_closed_price_by_timestamp = MagicMock(return_value=[
        [
            123456789,  # Open time
            "0.0010",   # Open
            "0.0020",   # High
            "0.0005",   # Low
            "0.0015",   # Close
            "1000",     # Volume
            123456799,  # Close time
            "1.5",      # Quote asset volume
            100,        # Number of trades
            "500",      # Taker buy base asset volume
            "0.75",     # Taker buy quote asset volume
            "0"         # Ignore
        ]
    ])

    transaction_pool_repo.insert_transaction_to_from_pool_data = MagicMock()

    client = ScrapperService(
        binance_spot_client=binance_spot_client,
        etherscan_client=ethercan_http_client,
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=transaction_pool_repo,
        web3py=MagicMock(),
    )

    result = client.scrapping_job(
        pool_id=1,
        start_block=12345,
        address="0x12345678"
    )

    assert result

def test_insert_new_latest_transaction_pool_return_bool() -> None:
    
    ethercan_http_client = EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key="",
    )

    binance_spot_client = BinanceSpotApiClient(
        spot_client=Spot(base_url=base_url, timeout=5),
    )

    transaction_pool_repo = TransactionToFromPoolRepository(
        db_session=MagicMock(),
    )

    ethercan_http_client.get_latest_token_txs = MagicMock(
        return_value= EtherscanTxResponse(
            status="1",
            message="OK",
            result=[
                EtherscanTransaction(
                    blockNumber = "12345",
                    timeStamp = "123",
                    hash = "123",
                    nonce = "123",
                    blockHash = "123",
                    from_ = "a",
                    contractAddress = "b",
                    to = "c",
                    value = "123",
                    tokenName = "123",
                    tokenSymbol = "123",
                    tokenDecimal = "123",
                    transactionIndex = "123",
                    gas = "123",
                    gasPrice = "123",
                    gasUsed = "123",
                    cumulativeGasUsed = "123",
                    input = "123",
                    confirmations = "123"
                ),
            ]
        )
    )

    binance_spot_client.get_closed_price_by_timestamp = MagicMock(return_value=[
        [
            123456789,  # Open time
            "0.0010",   # Open
            "0.0020",   # High
            "0.0005",   # Low
            "0.0015",   # Close
            "1000",     # Volume
            123456799,  # Close time
            "1.5",      # Quote asset volume
            100,        # Number of trades
            "500",      # Taker buy base asset volume
            "0.75",     # Taker buy quote asset volume
            "0"         # Ignore
        ]
    ])

    transaction_pool_repo.insert_transaction_to_from_pool_data = MagicMock()

    client = ScrapperService(
        binance_spot_client=binance_spot_client,
        etherscan_client=ethercan_http_client,
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=transaction_pool_repo,
        web3py=MagicMock(),
    )

    result = client.insert_new_latest_transaction_pool(
        token_pool_pair_id=1,
        address="0x12345678"
    )

    assert result

def test_read_latest_transaction_pool_data() -> None:

    transaction_pool_repo = TransactionToFromPoolRepository(
        db_session=MagicMock(),
    )
    transaction_pool_repo.get_latest_transaction_data_by_to_from_address_with_id = MagicMock(
        return_value=TransactionToFromPool(
            transaction_id=1,
            block_number=12345678,
            ts_timestamp=1234567890,
            tx_hash="0x1234567890abcdef",
            from_address="0xabcdef1234567890",
            to_address="0x1234567890abcdef",
            contract_address="0xabcdef1234567890",
            token_value="1000",
            token_name="TokenName",
            token_symbol="TN",
            token_decimal="18",
             transaction_index="1",
            gas_limit="21000",
            gas_price="1000000000",
            gas_used="21000",
            cumulative_gas_used="21000",
            confirmations="10",
            transaction_fee_usdt="0.01",
            pool_id=1
        )
    )
    client = ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=MagicMock(),
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=transaction_pool_repo,
        web3py=MagicMock()
    )   

    # client.__transaction_pool_repo = transaction_pool_repo

    result = client.read_latest_transaction_pool(
        address="0x12345678",
        token_pool_pair_id=1
    )

    assert result.transaction_id == 1

def get_mock_transaction_from_repo() -> TransactionToFromPool:
    return TransactionToFromPool(
            transaction_id=1,
            block_number=12345678,
            ts_timestamp=1234567890,
            tx_hash="0x1234567890abcdef",
            from_address="0xabcdef1234567890",
            to_address="0x1234567890abcdef",
            contract_address="0xabcdef1234567890",
            token_value="1000",
            token_name="TokenName",
            token_symbol="TN",
            token_decimal="18",
            transaction_index="1",
            gas_limit="21000",
            gas_price="1000000000",
            gas_used="21000",
            cumulative_gas_used="21000",
            confirmations="10",
            transaction_fee_usdt="0.01",
            pool_id=1
        )

def get_mock_token_pair_list_from_repo() -> list[TokenPairPool]:
    return [
        TokenPairPool(
            pool_id=1,
            pool_name="pool_name",
            contract_address="0x12345678",
        )
    ]

def get_transaction_and_token_repo_client_mock() -> ScrapperService:

    transaction_pool_repo = TransactionToFromPoolRepository(
        db_session=MagicMock(),
    )

    transaction_pool_repo.get_latest_transaction_data_by_to_from_address_with_id = MagicMock(
        return_value = get_mock_transaction_from_repo()
    )

    token_pair_pool_repo = TokenPairPoolsRepository(
        db_session=MagicMock(),
    )

    token_pair_pool_repo.read_all_token_pool_pairs = MagicMock(
        return_value = get_mock_token_pair_list_from_repo()
    )

    token_pair_pool_repo.read_token_pool_pair_by_address = MagicMock(
        return_value = get_mock_token_pair_list_from_repo()
    )

    token_pair_pool_repo.get_token_pool_pair_by_pool_name = MagicMock(
        return_value = get_mock_token_pair_list_from_repo()
    )

    token_pair_pool_repo.insert_token_pair_pool_data = MagicMock()

    client = ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=MagicMock(),
        token_pair_pool_repo=token_pair_pool_repo,
        transaction_pool_repo=transaction_pool_repo,
        web3py=MagicMock()
    )

    return client

def test_read_latest_transaction_pool_data_with_correct_value() -> None:
    client = get_transaction_and_token_repo_client_mock()

    result = client.read_latest_transaction_pool(
        address="0x12345678",
        token_pool_pair_id=1
    )

    expected = get_mock_transaction_from_repo()

    assert result.transaction_id == expected.transaction_id 

def test_get_all_token_pool_pairs_with_correct_value() -> None:
    client = get_transaction_and_token_repo_client_mock()

    result = client.get_all_token_pool_pair()

    expected = get_mock_token_pair_list_from_repo()

    assert result[0].contract_address == expected[0].contract_address

def test_get_all_token_pool_pair_by_address_with_correct_value() -> None:
    client = get_transaction_and_token_repo_client_mock()

    result = client.get_token_pool_pair_by_address("0x12345678")

    expected = get_mock_token_pair_list_from_repo()

    assert result[0].contract_address == expected[0].contract_address

def test_get_token_pool_pair_by_pool_name_with_correct_value() -> None:
    client = get_transaction_and_token_repo_client_mock()

    result = client.get_token_pool_pair_by_pool_name("pool_name")

    expected = get_mock_token_pair_list_from_repo()

    assert result[0].contract_address == expected[0].contract_address


def get_historical_transaction_data_scapper_mock() -> ScrapperService:
    etherscan_http_client = EtherscanHttpclient(
        http_client=ether_scan_client,
        api_key="",
    )

    etherscan_http_client.get_closest_block_number_by_end_timestamp = MagicMock(
        return_value = EtherscanBlockNumberResponse(
            status="1",
            message="OK",
            result="12345678",
        )
    )
    etherscan_http_client.get_closest_block_number_by_start_timestamp = MagicMock(
        return_value= EtherscanBlockNumberResponse(
            status="1",
            message="OK",
            result="12345677",
        )
    )

    etherscan_http_client.get_token_txs_by_start_and_end_block = MagicMock(
        return_value= EtherscanTxResponse(
            status="1",
            message="OK",
            result=[
                EtherscanTransaction(
                    blockNumber = "12345",
                    timeStamp = "123",
                    hash = "123",
                    nonce = "123",
                    blockHash = "123",
                    from_ = "a",
                    contractAddress = "b",
                    to = "c",
                    value = "123",
                    tokenName = "123",
                    tokenSymbol = "123",
                    tokenDecimal = "123",
                    transactionIndex = "123",
                    gas = "123",
                    gasPrice = "123",
                    gasUsed = "123",
                    cumulativeGasUsed = "123",
                    input = "123",
                    confirmations = "123"
                ),
            ]
        )
    )

    binance_spot_client = BinanceSpotApiClient(
        spot_client=Spot(base_url=base_url, timeout=5),
    )

    binance_spot_client.get_closed_price_by_timestamp = MagicMock(
        return_value=[
            [
                123456789,  # Open time
                "0.0010",   # Open
                "0.0020",   # High
                "0.0005",   # Low
                "0.0015",   # Close
                "1000",     # Volume
                123456799,  # Close time
                "1.5",      # Quote asset volume
                100,        # Number of trades
                "500",      # Taker buy base asset volume
                "0.75",     # Taker buy quote asset volume
                "0"         # Ignore
            ]
        ]
    )

    return ScrapperService(
        binance_spot_client=binance_spot_client,
        etherscan_client=etherscan_http_client,
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=MagicMock(),
    )

def test_get_historical_transaction_data_with_correct_value() -> None:
    client = get_historical_transaction_data_scapper_mock()

    result = client.get_historical_transaction_data(
        address="1",
        start_time=1234567890,
        end_time=1234567890,
    )

    assert result[0].blockNumber == "12345"
    assert result[0].usdt_fee == "0.00"
 

def test_get_transaction_data_with_time_range() -> None:
    client = get_historical_transaction_data_scapper_mock()

    result = client.get_transaction_data_with_time_range(
        address="1",
        start_time=1234567890,
        end_time=1234567890,
    )

    assert result[0].blockNumber == "12345"
    assert result[0].usdt_fee == "0.00"


def test_get_transaction_fee_with_tx_hash() -> None:
    transaction_pool_repo = TransactionToFromPoolRepository(
        db_session=MagicMock(),
    )

    transaction_pool_repo.read_transaction_data_by_tx_hash = MagicMock(
        return_value = [get_mock_transaction_from_repo()]
    )

    token_pair_pool_repo = TokenPairPoolsRepository(
        db_session=MagicMock(),
    )
    token_pair_pool_repo.read_token_pool_pair_data_by_id = MagicMock(
        return_value = get_mock_token_pair_list_from_repo()
    )

    client = ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=MagicMock(),
        token_pair_pool_repo=token_pair_pool_repo,
        transaction_pool_repo=transaction_pool_repo,
        web3py=MagicMock(),
    )

    (fee, pool_name) = client.get_transaction_fee_with_tx_hash("0x1234567890abcdef")

    assert fee == "0.01"
    assert pool_name == "pool_name"


class TxReceiptFromWeb3Mock(BaseModel):
    logs: list[Dict]


sender_receiver_address = "0xd4bC53434C5e12cb41381A556c3c47e1a86e80E3"
amount0 = -46760833659
amount1 = 18613894030387314688

class DecoderEventClassMock:
        def process_log(self, log: Dict) -> Dict:
            return {
                "args": {
                    "amount0": amount0,
                    "amount1": amount1,
                    "sqrtPriceX96": 1580398138016258038796895582689890,
                    "sender": sender_receiver_address,
                    "recipient": sender_receiver_address,
                }
            }

class MockEventsClass:
    def __init__(self):
        self.events = self

    def Swap(self):
        return DecoderEventClassMock()

def test_get_decode_uniswap_v3_executed_price() -> None:
    expected_execution_price = 2513.1947789287638
    contract_address = "123"
    tx_hash = "0x609e6a722c51b0242f7a3ffaba3f21b2a08cee6dd250702b70cae5f6f411c786"
    contract_address = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
    web3_client = Web3()
    web3_client.eth.get_transaction_receipt = MagicMock(
        return_value = TxReceiptFromWeb3Mock(
            logs=[{
                "address": contract_address,
                "topics": [
                    HexBytes('0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'),
                    HexBytes('0x000000000000000000000000d4bc53434c5e12cb41381a556c3c47e1a86e80e3'),
                    HexBytes('0x000000000000000000000000d4bc53434c5e12cb41381a556c3c47e1a86e80e3')
                ]
            }]
        )
    )

    web3_client.eth.contract = MagicMock(
        return_value = MockEventsClass()
    )

    client = ScrapperService(
        binance_spot_client=MagicMock(),
        etherscan_client=MagicMock(),
        token_pair_pool_repo=MagicMock(),
        transaction_pool_repo=MagicMock(),
        web3py=web3_client,
    )

    result_list = client.get_decode_uniswap_v3_executed_price(tx_hash=tx_hash, contract_address=contract_address)
    assert len(result_list) > 0
    result = result_list[0]
    assert result.transaction_hash == tx_hash
    assert result.execution_price == "{:.2f}".format(float(expected_execution_price))
    assert result.amount0 == str(amount0)
    assert result.amount1 == str(amount1)
    assert result.sender == sender_receiver_address
    assert result.recipient == sender_receiver_address



    