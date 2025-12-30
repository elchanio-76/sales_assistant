#!/home/lchanio/projects/sales_assistant/.venv/bin/python


from sqlalchemy import MetaData, create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DB_URL')

engine = create_engine(db_url)
metadata = MetaData()
metadata.reflect(bind=engine)

# Generate DDL as string
from sqlalchemy.schema import CreateTable
for table in metadata.sorted_tables:
    print(str(CreateTable(table).compile(engine)))