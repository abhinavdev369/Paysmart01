<h1 align="center"> PaySmart -FastAPI+PayPal Integration</h1>
PaySmart is a backend Payment management system built using FastAPI that integrates PayPal for real time transactions. It supports user registration,wallet funding,P2P( peer to peer) money transfers , and transaction history tracking using a PostgreSQL database

Features:
-User registration with hashed passwords
-Wallet management (fund wallet and balance)
-Peer to peer transactions between users
-Paypal integration using both Rest API and SDK
-Transaction login with transaction type and status
-PostgreSQL for robust backend development using SQLALchemy
-Pydantic for validation
-Jinja2 template for rendering and static file support
-Authentication using passlib(bcrypt) for hashing 
🔁 API Endpoints
Method	Endpoint	Description
POST	/users/register	Register a new user
POST	/wallets/fund	Fund wallet using PayPal
POST	/create-order	Create PayPal order (REST API)
POST	/capture-order/{order_id}	Capture PayPal order
GET	/payment/success	Callback for success payment
GET	/payment/cancel	Callback for canceled payment
POST	/transactions/p2p	Transfer funds to another user
POST	/webhook	PayPal webhook listener
GET	/	Basic HTML UI

Sandbox credentials shall be used for testing
