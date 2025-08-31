from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
import os
from dotenv import load_dotenv

# Load environment variables from the current directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI(title="Datafy API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development environment
        "https://zenith-ed.netlify.app"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)