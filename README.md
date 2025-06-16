<h1 align="center"> PaySmart -FastAPI+PayPal Integration</h1>
PaySmart is a backend Payment Management System built using FastAPI that integrates PayPal for real-time transactions.  
It supports user registration, wallet funding, peer-to-peer (P2P) money transfers, and transaction history tracking, with PostgreSQL as the backend database.

---

## 🔧 Features

- 🔐 User registration with hashed passwords
- 💰 Wallet management (funding and balance tracking)
- 🔁 Peer-to-peer (P2P) transactions between users
- 💳 PayPal integration using **REST API** and **SDK**
- 📜 Transaction logging with type and status
- 🗄️ PostgreSQL backend using SQLAlchemy ORM
- ✅ Data validation using **Pydantic**
- 🧾 Jinja2 templates + static file support
- 🔑 Password hashing with **Passlib (bcrypt)**

---

## 📡 API Endpoints

| Method | Endpoint                     | Description                              |
|--------|------------------------------|------------------------------------------|
| POST   | `/users/register`            | Register a new user                      |
| POST   | `/wallets/fund`              | Fund wallet using PayPal                 |
| POST   | `/create-order`              | Create PayPal order (REST API)           |
| POST   | `/capture-order/{order_id}`  | Capture PayPal order                     |
| GET    | `/payment/success`           | Callback for successful payment          |
| GET    | `/payment/cancel`            | Callback for canceled payment            |
| POST   | `/transactions/p2p`          | Transfer funds to another user           |
| POST   | `/webhook`                   | PayPal webhook listener                  |
| GET    | `/`                          | Basic HTML UI using Jinja2 templates     |

---

## 🧪 Testing

- 🧾 Use **PayPal sandbox credentials** for all test transactions.
- Ensure environment variables like `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` are set in your `.env` file.

---

## 📂 Tech Stack

- **Backend**: FastAPI
- **Payment Integration**: PayPal REST API & SDK
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Passlib (bcrypt)
- **Templating**: Jinja2
- **Validation**: Pydantic

IMAGES:
  ![image](https://github.com/user-attachments/assets/b04c52fa-1bef-4068-bb96-9a9a80cc98dc)
  ![image](https://github.com/user-attachments/assets/606a1338-21ee-481a-addb-51e028c4f985)
  ![image](https://github.com/user-attachments/assets/6a39d5ec-75e3-4df9-ac38-a13abf0391fd)



