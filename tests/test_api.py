import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Base,User,Wallet,Transaction
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
import httpx

TEST_DATABASE_URL="postgresql://postgres:2004@localhost:5432/smart_test"

engine=create_engine (TEST_DATABASE_URL)
TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
app.dependency_overrides[get_db]=override_get_db
client=TestClient(app)
@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_register_user(setup_database):
    response = client.post(
        "/users/register",
        json={"email": "testuser@example.com", "hashed_password": "password1234", "full_name": "hello"}
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully", "user_id": 1,"wallet_id":1}

import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_fund_wallet(setup_database, mocker):
    # Initialize the test client (assuming setup_database provides the FastAPI app)
    client = setup_database  # Replace with TestClient(app) if setup_database is not the client

    # Register a user first and capture the user_id
    register_response = client.post(
        "/users/register",
        json={
            "email": "funduser@gmail.com",
            "password": "password123",
            "full_name": "Testing Name"
        }
    )
    assert register_response.status_code == 201  # Assuming 201 for successful registration
    user_data = register_response.json()
    user_id = user_data.get("id")  # Extract user_id from response to avoid hardcoding

    # Create a mock Payment instance
    mock_payment = mocker.MagicMock()
    mock_payment.create.return_value = True
    mock_payment.links = [
        {"rel": "approval_url", "href": "https://www.sandbox.paypal.com/approve"}
    ]  # Fixed typo: sandboc -> sandbox
    mock_payment.id = "PAYID-TEST123"

    # Mock the Payment class to return the mock instance
    mocker.patch("paypalrestsdk.Payment", return_value=mock_payment)

    # Send request to fund wallet
    response = client.post(
        "/wallets/fund",
        json={
            "user_id": user_id,  # Use dynamic user_id from registration
            "amount": 100.0,
            "return_url": "http://localhost:8000/wallets/fund/execute",
            "cancel_url": "http://localhost:8000/wallets/fund/cancel"
        }
    )

    # Assert the response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}: {response.text}"
    response_data = response.json()
    assert "approval_url" in response_data, "Expected 'approval_url' in response"
    assert response_data["approval_url"] == "https://www.sandbox.paypal.com/approve"
    
@pytest.mark.asyncio
async def test_get_wallet_balance(setup_database):
    client.post("/users/register",json={"email":"balanceuser@gmail.com","password":"password123","full_name":"balanceuser"})
    db=TestingSessionLocal()
    wallet=db.query(Wallet).filter(Wallet.user_id==3).first()
    wallet.balance=50.0
    db.commit()
    db.close()
    response=client.get("/wallets/balance/3")
    assert response.status_code==200
    assert response.json()=={"user_id":3,"balance":50.0}

@pytest.mark.asyncio
async def test_get_transaction_history(setup_database):
    client.post(
        "/users/register",
        json={"email": "sender@gmail.com", "password": "pass123", "full_name": "Sender"}
    )
    client.post(
        "/users/register",
        json={"email": "receiver@gmail.com", "password": "pass123", "full_name": "Receiver"}
    )
    db = TestingSessionLocal()
    sender_wallet = db.query(Wallet).filter(Wallet.user_id == 4).first()
    sender_wallet.balance = 100.0
    db.commit()
    db.close()

    # Perform a transfer (update endpoint if needed)
    client.post(
        "/p2p_transaction",  # Changed to /p2p_transaction if that's the correct endpoint
        json={"sender_id": 4, "receiver_id": 5, "amount": 30.0}
    )

    response = client.get("/wallets/transactions/4")
    assert response.status_code == 200
    assert len(response.json()) == 1  # Expecting one transaction

@pytest.mark.asyncio
async def test_fund_wallet_execute(setup_database,mocker):
    client.post("/users/register",json={"email":"executeuser@gamil.com","password":"pass123","full_name":"executename"})
    mock_payment=mocker.MagicMock()
    mock_payment.execute.return_value=True
    mock_payment.transactions-[{"amount":{"total":"50.0"}}]
    mocker.patch("paypalrestsdk.Payment.find",return_value=mock_payment)

    response=client.get("/wallets/fund/execute?payment_id=PAYID-TEST123&payer_id=PAYERID-TEST")
    assert response.status_code==200
    assert response.json()=={"message":"payment success"}

@pytest.mark.asyncio
async def test_fund_wallet_cancel(setup_database):
    response=client.get("wallets/fund/cancel")
    assert response.status_code==200
    assert response.json() == {"message":"Payment cancelled"}

