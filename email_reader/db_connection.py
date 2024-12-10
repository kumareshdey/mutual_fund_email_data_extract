from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from setup import log

DATABASE_URL = "postgresql+psycopg2://postgres:kumaresh@localhost:5433/spiderman"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def test_connection():
    try:
        with engine.connect() as connection:
            print("Connection to PostgreSQL database successful!")
    except Exception as e:
        print(f"Error: Could not connect to the PostgreSQL database.\nDetails: {e}")

if __name__ == "__main__":
    test_connection()
