from sqlalchemy import create_engine, text
from models import Base
from credentials import DB_PORT

# Database connection URL for PostgreSQL
DATABASE_URL = f"postgresql+psycopg2://postgres:kumaresh@localhost:{DB_PORT}/postgres"
TARGET_DB = "spiderman"

from urllib.parse import urlparse, urlunparse

def get_target_db_url():
    parsed_url = urlparse(DATABASE_URL)
    # Replace only the database name in the path
    new_path = f"/{TARGET_DB}"
    return urlunparse(parsed_url._replace(path=new_path))

def drop_and_recreate_database():
    # Connect to the default database (e.g., "postgres") to perform administrative tasks
    admin_engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    with admin_engine.connect() as connection:
        # Terminate active connections to the target database
        print(f"Terminating active connections to the database '{TARGET_DB}'...")
        connection.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TARGET_DB}' AND pid <> pg_backend_pid();
        """))
        
        # Drop the database if it exists
        print(f"Dropping the database '{TARGET_DB}' if it exists...")
        connection.execute(text(f"DROP DATABASE IF EXISTS {TARGET_DB};"))
        
        # Recreate the database
        print(f"Creating the database '{TARGET_DB}'...")
        connection.execute(text(f"CREATE DATABASE {TARGET_DB};"))
    
    print("Database dropped and recreated successfully.")

def recreate_schema():
    # Get the updated URL pointing to the target database
    target_db_url = get_target_db_url()
    schema_engine = create_engine(target_db_url)
    
    # Recreate all tables based on SQLAlchemy models
    print("Recreating the schema...")
    Base.metadata.create_all(schema_engine)
    print("Schema recreated successfully.")

if __name__ == "__main__":
    drop_and_recreate_database()
    recreate_schema()