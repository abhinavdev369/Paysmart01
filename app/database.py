from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL="postgresql://postgres:2004@localhost:5432/smart"
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()