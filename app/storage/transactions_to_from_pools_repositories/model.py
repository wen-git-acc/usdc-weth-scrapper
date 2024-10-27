from sqlalchemy import Column, Integer, BigInteger, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransactionToFromPool(Base):
    __tablename__ = 'transactions_to_from_pools'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    block_number = Column(String, nullable=False)
    ts_timestamp = Column(String, nullable=False)
    tx_hash = Column(String, unique=True, nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    contract_address = Column(String, nullable=False)
    token_value = Column(String, nullable=False)
    token_name = Column(String)
    token_symbol = Column(String)
    token_decimal = Column(String)
    transaction_index = Column(String, nullable=False)
    gas_limit = Column(String, nullable=False)
    gas_price = Column(String, nullable=False)
    gas_used = Column(String, nullable=False)
    cumulative_gas_used = Column(String)
    confirmations = Column(String)
    transaction_fee_usdt = Column(String)
    pool_id = Column(Integer, ForeignKey('token_pair_pools.pool_id'), nullable=True)

    # Relationship to token pair pool
    # pool = relationship("TokenPairPool", back_populates="transactions")

    def __repr__(self):
        return (f"<TransactionToFromPool(transaction_id={self.transaction_id}, "
                f"block_number={self.block_number}, ts_timestamp={self.ts_timestamp}, "
                f"tx_hash={self.tx_hash}, from_address={self.from_address}, "
                f"to_address={self.to_address}, token_value={self.token_value}, "
                f"transaction_fee_usdt={self.transaction_fee_usdt})>")
