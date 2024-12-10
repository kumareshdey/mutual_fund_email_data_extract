
from sqlalchemy import text
from models import Base
from db_connection import engine

# create

# with engine.connect() as connection:
#     # Create a new database called 'spiderman'
#     connection.execute(text("CREATE DATABASE spiderman"))

Base.metadata.create_all(engine)


# # Rename the column directly in the database
# with engine.connect() as connection:
#     connection.execute(text("ALTER TABLE CAMS_WBR9 RENAME COLUMN HOLDING_NA TO HOLDING_NAT;"))


# with engine.connect() as connection:
#     result = connection.execute(text("SELECT * FROM information_schema.columns WHERE table_name = 'CAMS_WBR9'"))
#     print([row[0] for row in result])


# with engine.connect() as connection:
#     result = connection.execute(text(
#         "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';"
#     ))
#     print([row[0] for row in result])
