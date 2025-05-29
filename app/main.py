from fastapi import FastAPI
from .routes import dashboard
from .database import Base, engine

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Test Execution Dashboard")

# Register routes
app.include_router(dashboard.router, prefix="/api")
