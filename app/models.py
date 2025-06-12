from sqlalchemy import Column,Integer,String ,Float,DateTime ,ForeignKey
from sqlalchemy.orm import declarative_base
Base=declarative_base()
class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,index=True)
    hashed_password=Column(String,nullable=False,unique=True)
    full_name=Column(String)

class Wallet(Base):
    __tablename__='wallets'
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey('users.id'),index=True)
    balance=Column(Float,default=0.0)

class Transaction(Base):
    __tablename__='transactions'
    id=Column(Integer,primary_key=True,index=True)
    sender_wallet_id=Column(Integer,ForeignKey('users.id'),nullable=True,index=True)
    receiver_wallet_id=Column(Integer,ForeignKey('users.id'),nullable=True,index=True)
    amount=Column(Float,nullable=False)
    timestamp=Column(DateTime)
    transaction_id = Column(String, nullable=True)
    transaction_type = Column(String, nullable=True)
    status = Column(String, nullable=True)  # Add this to your model
