from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from langchain_community.utilities import SQLDatabase  # Use langchain_community for newer versions
# Load environment variables from .env
load_dotenv()
# Load DB URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: postgres://user:pass@host/dbname
# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reflect schema
metadata = MetaData()
metadata.reflect(bind=engine)

# List of actual table names in the connected DB
table_names = list(metadata.tables.keys())

# Optional Base class if you're using ORM models
Base = declarative_base()

# LangChain SQLDatabase instance (to be used in LLM chains)
db = SQLDatabase(engine=engine)
