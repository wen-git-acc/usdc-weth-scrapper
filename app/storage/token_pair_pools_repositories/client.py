from sqlalchemy.exc import IntegrityError
from typing import Callable

from httpx import get
from sqlalchemy import and_, case
from sqlalchemy.orm import Session

from app.core.log.logger import Logger
from app.storage.models import TokenPairPool



class TokenPairPoolsRepository:
    def __init__(self, db_session: Callable[..., Session]) -> None:
        self.__db_session = db_session
        self.__logger = Logger(name=self.__class__.__name__)

    def insert_token_pair_pool_data(self, data: list[TokenPairPool]) -> None:
        """
        Method to insert bulk data into table/schema, input is a list.
        """
        # Need to prevent duplicate to be insert

        token_pair_pool_data_to_insert = []

        for token_pair_pool in data:
            get_token_pair_pool_data = self.read_token_pool_pair_by_address(token_pair_pool.contract_address)
            if len(get_token_pair_pool_data) > 0:
                continue
            token_pair_pool_data_to_insert.append(token_pair_pool)

        try:
            if len(token_pair_pool_data_to_insert) == 0:
                return

            with self.__db_session() as session:
                for token_pool in token_pair_pool_data_to_insert:
                    session.add(token_pool)
                session.commit()
        except IntegrityError as e:
            description = "Unique pair constraint violated, already inserted"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            return
        except Exception as e:
            description = "Insert token pair pool data failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Insert token pair pool data failed"
            raise Exception(error_message) from e

    def read_token_pool_pair_by_address(
        self, address: str
    ) -> list[TokenPairPool] | None:
        """
        Method to read TokenPairPool based on address.
        """
        try:
            with self.__db_session() as session:
                return (
                    session.query(TokenPairPool)
                    .filter(TokenPairPool.contract_address == address)
                    .all()
                )
        except Exception as e:
            description = "Read token pair pool data by address failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read token pair pool data by address failed"
            raise Exception(error_message) from e
        
    def get_token_pool_pair_by_pool_name(
        self, pool_name: str
    ) -> list[TokenPairPool] | None:
        """
        Method to read TokenPairPool based on pool_name.
        """
        try:
            with self.__db_session() as session:
                return (
                    session.query(TokenPairPool)
                    .filter(TokenPairPool.pool_name == pool_name)
                    .all()
                )
        except Exception as e:
            description = "Read token pair pool data by pool_name failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read token pair pool data by pool_name failed"
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

    def read_all_token_pool_pairs (
        self
    ) -> list[TokenPairPool] | None:
        """
        Method to read all TokenPairPool.
        """
        try:
            with self.__db_session() as session:
                return (
                    session.query(TokenPairPool)
                    .all()
                )
        except Exception as e:
            description = "Read all token pair pool data failed"
            log_message = f"Description: {description} |Error: {e!s}"
            self.__logger.exception(log_message)
            error_message = "Read all token pair pool data failed"
            raise Exception(error_message) from e
    