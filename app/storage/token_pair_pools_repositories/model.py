from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TokenPairPool(Base):
    __tablename__ = 'token_pair_pools'
    
    pool_id = Column(Integer, primary_key=True, autoincrement=True)
    pool_name = Column(String(255), unique=True, nullable=False)
    contract_address = Column(String(42), unique=True, nullable=False)

    # Relationship to transactions
    transactions = relationship("TransactionToFromPool", back_populates="pool")