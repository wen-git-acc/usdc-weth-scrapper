from typing import Callable

from sqlalchemy import and_, case, or_
from sqlalchemy.orm import Session

from app.core.log.logger import Logger
from app.storage.models import TransactionToFromPool

class TransactionToFromPoolRepository:
    def __init__(self, db_session: Callable[..., Session]) -> None:
        self.__db_session = db_session
        self.__logger = Logger(name=self.__class__.__name__)

    def insert_transaction_to_from_pool_data(self, data: list[TransactionToFromPool]) -> None:
        """
        Method to insert bulk data into table/schema, input is a list.
        """
        # Need to prevent duplicate too
        try:
            if len(data) == 0:
                return

            with self.__db_session() as session:
                for transaction in data:
                    session.add(transaction)
                session.commit()
        except Exception as e:
            description = "Insert transaction to from pool data failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Insert transaction to from pool data failed"
            raise Exception(error_message) from e
        
    def insert_first_transaction_to_from_pool_data(self, data: list[TransactionToFromPool]) -> None:
        """
        Method to insert bulk data into table/schema, input is a list.
        """
        # Need to prevent duplicate too
        existing_tx_hash = self.read_transaction_data_by_tx_hash([transaction.tx_hash for transaction in data])
        if len(existing_tx_hash) > 0:
            return

        try:
            if len(data) == 0:
                return

            with self.__db_session() as session:
                for transaction in data:
                    session.add(transaction)
                session.commit()
        except Exception as e:
            description = "Insert transaction to from pool data failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Insert transaction to from pool data failed"
            raise Exception(error_message) from e


    def read_token_pool_pair_data_by_id(
        self, ids: list[int]
    ) -> list[TransactionToFromPool] | None:
        """
        Method to bulk read TransactionToFromPool based on transaction_id.
        order condition to ensure the response from db is according to order in IN clause
        """
        try:
            if len(ids) == 0:
                return []

            with self.__db_session() as session:

                clause_statement_list = [TransactionToFromPool.transaction_id.in_(ids)]
                query_statement = session.query(TransactionToFromPool)

                order_conditions = case(
                    {value: index for index, value in enumerate(ids)},
                    value=TransactionToFromPool.transaction_id,
                )
                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .order_by(order_conditions)
                    .all()
                )

        except Exception as e:
            description = "Read transaction to from pool data by id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read transaction to from pool data by id failed"
            raise Exception(error_message) from e
        
    def read_transaction_data_by_tx_hash(
        self, tx_hashs: list[int]
    ) -> list[TransactionToFromPool] | None:
        """
        Method to bulk read TransactionToFromPool based on tx_hashs.
        order condition to ensure the response from db is according to order in IN clause
        """
        try:
            if len(tx_hashs) == 0:
                return []

            with self.__db_session() as session:

                clause_statement_list = [TransactionToFromPool.tx_hash.in_(tx_hashs)]
                query_statement = session.query(TransactionToFromPool)

                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .all()
                )

        except Exception as e:
            description = "Read transaction to from pool data by id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read transaction to from pool data by id failed"
            raise Exception(error_message) from e
        
    def read_transaction_data_by_to_from_address(
        self, 
        address: str,
        pool_id: str,
    ) -> list[TransactionToFromPool] | None:
        """
        Method to bulk read TransactionToFromPool based on to_address, from_address, and pool_id.
        """
        try:
            with self.__db_session() as session:

                clause_statement_list = [
                    or_(
                        TransactionToFromPool.to_address == address,
                        TransactionToFromPool.from_address == address
                    ),
                    TransactionToFromPool.pool_id == pool_id
                ]
                query_statement = session.query(TransactionToFromPool)

                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .all()
                )

        except Exception as e:
            description = "Read transaction to from pool data by address and pool_id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read transaction to from pool data by address and pool_id failed"
            raise Exception(error_message) from e
        
    def get_latest_transaction_data_by_to_from_address_with_id(
        self, 
        address: str,
        pool_id: str,
    ) -> TransactionToFromPool | None:
        """
        Method to get the latest TransactionToFromPool based on to_address, from_address, and pool_id,
        ordered by created date.
        """
        try:
            with self.__db_session() as session:

                clause_statement_list = [
                    or_(
                        TransactionToFromPool.to_address == address,
                        TransactionToFromPool.from_address == address
                    ),
                    TransactionToFromPool.pool_id == pool_id
                ]
                query_statement = session.query(TransactionToFromPool)

                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .order_by(TransactionToFromPool.ts_timestamp.desc())
                    .first()
                )

        except Exception as e:
            description = "Read latest transaction to from pool data by address and pool_id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read latest transaction to from pool data by address and pool_id failed"
            raise Exception(error_message) from e

    def get_earliest_transaction_data_by_id(
            self,
            pool_id: str,
    ) -> TransactionToFromPool | None:
        """
        Method to get the earliest TransactionToFromPool based on timestamp and pool_id,
        ordered by created date.
        """
        try:
            with self.__db_session() as session:

                clause_statement_list = [
                    TransactionToFromPool.pool_id == pool_id
                ]
                query_statement = session.query(TransactionToFromPool)

                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .order_by(TransactionToFromPool.ts_timestamp.asc())
                    .first()
                )

        except Exception as e:
            description = "Read earliest transaction to from pool data by timestamp and pool_id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read earliest transaction to from pool data by timestamp and pool_id failed"
            raise Exception(error_message) from e