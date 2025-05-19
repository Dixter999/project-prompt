# Backend API Test Template

This is a Python FastAPI project for testing Anthropic's markdown generation capabilities with backend API projects.

## Features

- RESTful API endpoints
- Data models with validation
- Authentication middleware
- Database integration
- Basic error handling
- API documentation

## Structure

- `main.py` - Entry point for the API
- `models/` - Data models
- `routes/` - API routes
- `services/` - Business logic
- `middleware/` - Authentication and other middleware
- `db/` - Database connection and models

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```

## API Documentation

When running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
