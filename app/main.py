from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chatbotassistant import router as chatbot_router
from app.routes.dashboard import router as dashboard_router

# Load environment variables from .env
load_dotenv()


# Initialize FastAPI app
app = FastAPI(title="Test Execution Dashboard")

# Enable CORS (you can restrict origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(dashboard_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")

# Root health check
@app.get("/")
def root():
    return {"status": "OK"}
