from sqlalchemy import Column, Integer, BigInteger, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TransactionToFromPool(Base):
    __tablename__ = 'transactions_to_from_pools'
    
    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    block_number = Column(BigInteger, nullable=False)
    ts_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    tx_hash = Column(String(66), unique=True, nullable=False)  # 66 characters for tx hashes with '0x' prefix
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    contract_address = Column(String(42), nullable=False)
    token_value = Column(Numeric(38, 0), nullable=False)  # 38 digits for high precision token values
    token_name = Column(String(50))
    token_symbol = Column(String(20))
    token_decimal = Column(Integer)  # Changed to Integer for better compatibility
    transaction_index = Column(Integer, nullable=False)
    gas_limit = Column(BigInteger, nullable=False)  # Original gas limit provided by the sender
    gas_price = Column(BigInteger, nullable=False)  # Gas price in wei
    gas_used = Column(BigInteger, nullable=False)  # Actual gas used
    cumulative_gas_used = Column(BigInteger)
    confirmations = Column(Integer)
    transaction_fee_usdt = Column(Numeric(38, 18))
    pool_id = Column(Integer, ForeignKey('token_pair_pools.pool_id'), nullable=True)

    # Relationship to token pair pool
    pool = relationship("TokenPairPool", back_populates="transactions")

    def __repr__(self):
        return (f"<TransactionToFromPool(transaction_id={self.transaction_id}, "
                f"block_number={self.block_number}, ts_timestamp={self.ts_timestamp}, "
                f"tx_hash={self.tx_hash}, from_address={self.from_address}, "
                f"to_address={self.to_address}, token_value={self.token_value}, "
                f"transaction_fee_usdt={self.transaction_fee_usdt})>")
