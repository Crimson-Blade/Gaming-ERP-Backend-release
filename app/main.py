from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from .database import engine
from . import models
from .endpoints import registrations, systems, orders, menu, billing, session
from dotenv import load_dotenv


# Create all database models
models.Base.metadata.create_all(bind=engine)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Replace with frontend URL in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# Include all routers
app.include_router(registrations.router)
app.include_router(systems.router)
app.include_router(orders.router)
app.include_router(menu.router)
app.include_router(billing.router)
app.include_router(session.router)