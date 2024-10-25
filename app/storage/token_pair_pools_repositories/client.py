from typing import Callable

from sqlalchemy import and_, case
from sqlalchemy.orm import Session

from app.core.log.logger import Logger
from app.storage.token_pair_pools_repositories.model import TokenPairPool



class TokenPairPoolsRepository:
    def __init__(self, db_session: Callable[..., Session]) -> None:
        self.__db_session = db_session
        self.__logger = Logger(name=self.__class__.__name__)

    def insert_token_pair_pool_data(self, data: list[TokenPairPool]) -> None:
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
            description = "Insert token pair pool data failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Insert token pair pool data failed"
            raise Exception(error_message) from e


    def read_token_pool_pair_data_by_id(
        self, ids: list[int]
    ) -> list[TokenPairPool] | None:
        """
        Method to bulk read TokenPairPool based on pool_id.
        order condition to ensure the response from db is according to order in IN clause
        """
        try:
            if len(ids) == 0:
                return []

            with self.__db_session() as session:

                clause_statement_list = [TokenPairPool.pool_id.in_(ids)]
                query_statement = session.query(TokenPairPool)

                order_conditions = case(
                    {value: index for index, value in enumerate(ids)},
                    value=TokenPairPool.pool_id,
                )
                return (
                    query_statement.filter(and_(*clause_statement_list))
                    .order_by(order_conditions)
                    .all()
                )

        except Exception as e:
            description = "Read token pair pool data by id failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read token pair pool data by id failed"
            raise Exception(error_message) from e
