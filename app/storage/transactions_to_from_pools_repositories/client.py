from typing import Callable

from sqlalchemy import and_, case
from sqlalchemy.orm import Session

from app.core.log.logger import Logger
from app.storage.transactions_to_from_pools_repositories.model import TransactionToFromPool

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
                for embedding in data:
                    session.add(embedding)
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
