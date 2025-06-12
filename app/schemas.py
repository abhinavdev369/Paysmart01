from pydantic import BaseModel,field_validator, EmailStr
from typing import Optional
class UserCreate(BaseModel):
    id: Optional[int]=None
    email: None |EmailStr
    hashed_password:None |str
    full_name:None | str = None
   
class WalletFund(BaseModel):
    user_id: int
    amount: float
    return_url: Optional[str]
    cancel_url: Optional[str]

    @field_validator('amount')
    def valbalance(cls, v):
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return v
class FundWalletRequest(BaseModel):
    user_id: int
    amount: float
    return_url: str
    cancel_url: str
    
from pydantic import BaseModel
from typing import Literal

class PayPalResource(BaseModel):
    id: str

class PayPalWebhookSchema(BaseModel):
    event_type: Literal["CHECKOUT.ORDER.COMPLETED"]
    resource: PayPalResource


class TransactionSchema(BaseModel):
    sender_id: Optional[int]  # Optional if system-generated
    receiver_id: int
    amount: float
    transaction_id: Optional[str] = None
