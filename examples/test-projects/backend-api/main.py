"""
Main application entry point for the FastAPI backend
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from db.database import engine
from db import models
from routes import users, items, auth
from middleware.auth import get_current_user

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Test API",
    description="A test API for Anthropic markdown generation verification",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router, tags=["Users"], prefix="/users")
app.include_router(
    items.router, 
    tags=["Items"], 
    prefix="/items",
    dependencies=[Depends(get_current_user)]
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint that returns API information"""
    return {
        "message": "Welcome to the Test API",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Test API for Anthropic Verification",
        version="0.1.0",
        description="This API is used for testing the markdown generation capabilities of Anthropic Claude.",
        routes=app.routes,
    )
    
    # Custom extension
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
