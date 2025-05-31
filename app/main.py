from fastapi import FastAPI
from .routes import dashboard
from .database import Base, engine

from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

from app.routes.dashboard import router as dashboard_router

# Load environment variables from .env
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Test Execution Dashboard")

# Add this block to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(dashboard_router)

# Optional root endpoint
@app.get("/")
def root():
    return {"status": "OK"}


# Register routes
app.include_router(dashboard.router, prefix="/api")
