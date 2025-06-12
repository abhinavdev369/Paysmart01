from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Wallet, Transaction
from app.schemas import UserCreate, WalletFund, TransactionSchema,FundWalletRequest,PayPalResource,PayPalWebhookSchema
from passlib.context import CryptContext
import requests
import base64
import paypalrestsdk
from contextlib import contextmanager
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import os
load_dotenv()
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_SANDBOX_URL = "https://api-m.sandbox.paypal.com"
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PayPal access token
def get_paypal_access_token() -> str:
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(f"{PAYPAL_SANDBOX_URL}/v1/oauth2/token", headers=headers, data={"grant_type": "client_credentials"})
    response.raise_for_status()
    return response.json()["access_token"]

@app.post("/create-order")
def create_order():
    access_token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": "10.00"
            }
        }]
    }
    response = requests.post(f"{PAYPAL_SANDBOX_URL}/v2/checkout/orders", headers=headers, json=body)
    return response.json()

@app.post("/capture-order/{order_id}")
def capture_order(order_id: str):
    access_token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.post(f"{PAYPAL_SANDBOX_URL}/v2/checkout/orders/{order_id}/capture", headers=headers)
    return response.json()

# Database transaction context manager
@contextmanager
def db_transaction(db: Session):
    try:
        yield 
        db.commit()
    except Exception:
        db.rollback()
        raise

@app.post("/users/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = pwd_context.hash(user.hashed_password)
    db_user = User(id=user.id, email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    with db_transaction(db):
        db.add(db_user)
        db_wallet = Wallet(user_id=db_user.id, balance=0.0)
        db.add(db_wallet)
        db.flush()  # Ensure wallet ID is available
    return {"message": "User registered successfully", "user_id": db_user.id, "wallet_id": db_wallet.id}
@app.post("/wallets/fund")
async def fund_wallet(request: FundWalletRequest, db: Session = Depends(get_db)):
    # Validate user
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create PayPal payment
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {
                "total": f"{request.amount:.2f}",  # Format as string with 2 decimals
                "currency": "USD"
            }
        }],
        "redirect_urls": {
            "return_url": request.return_url,
            "cancel_url": request.cancel_url
        }
    })
    
    if not payment.create():
        raise HTTPException(status_code=400, detail=f"Payment creation failed: {payment.error}")

    # Log transaction
    transaction = Transaction(
        sender_id=request.user_id,  # External source (PayPal)
        receiver_id=request.user_id,
        amount=request.amount,
        timestamp=datetime.utcnow(),
        transaction_id=payment.id
    )
    wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()# Assuming the wallet ID is the same as user ID
    wallet.balance += request.amount
    db.add(transaction)
    db.commit()

    # Return approval URL and transaction ID
    for link in payment.links:
        if link.rel == "approval_url":
            return {
                "approval_url": link.href,
                "transaction_id": payment.id
            }
    raise HTTPException(status_code=500, detail="Approval URL not found")
@app.get("/payment/success")
async def payment_success(order_id: str, db: Session = Depends(get_db)):
    access_token = get_paypal_access_token()
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.post(f"{PAYPAL_SANDBOX_URL}/v2/checkout/orders/{order_id}/capture", headers=headers)
    response.raise_for_status()
    capture_data = response.json()

    if capture_data["status"] != "COMPLETED":
        raise HTTPException(status_code=400, detail="Payment capture failed")

    with db_transaction(db):
        transaction = db.query(Transaction).filter(Transaction.transaction_id == order_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        transaction.status = "completed"
        wallet = db.query(Wallet).filter(Wallet.id == transaction.sender_wallet_id).first()
        wallet.balance += transaction.amount
        db.flush()

    return {"message": "Payment successful", "payment_id": order_id}

@app.get("/payment/cancel")
async def payment_cancel():
    return {"message": "Payment cancelled"}

@app.post("/transactions/p2p")
async def p2p_transaction(transfer: TransactionSchema, db: Session = Depends(get_db), user_id: int = 1):  # Replace with auth
    sender_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    receiver = db.query(User).filter(User.id == transfer.receiver_id).first()
    if not sender_wallet or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")
    receiver_wallet = db.query(Wallet).filter(Wallet.user_id == receiver.id).first()
    if not receiver_wallet:
        raise HTTPException(status_code=404, detail="Receiver wallet not found")
    if sender_wallet.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    with db_transaction(db):
        sender_wallet.balance -= transfer.amount
        receiver_wallet.balance += transfer.amount
        transaction = Transaction(
            sender_wallet_id=user_id,
            receiver_wallet_id=receiver.id,
            amount=transfer.amount,
            transaction_type="p2p",
            status="completed"
        )
        db.add(transaction)
        db.flush()

    return {"message": "Transfer successful", "transaction_id": transaction.id}

@app.get("/wallets/transactions/{user_id}")
async def get_transaction_history(user_id: int, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    transactions = db.query(Transaction).filter(
        (Transaction.sender_wallet_id == wallet.id) | (Transaction.receiver_wallet_id == wallet.id)
    ).all()
    return [{"id": t.id, "amount": t.amount, "timestamp": t.timestamp, "type": t.transaction_type, "status": t.status} for t in transactions]

@app.post("/webhook")
async def paypal_webBosch(data: PayPalWebhookSchema):
    order_id = data.resource.id
    return {"status": "received"}