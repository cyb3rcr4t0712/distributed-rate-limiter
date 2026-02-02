from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import uvicorn
import os
from app.rate_limiter import limiter
from app import analytics

app = FastAPI(title="HacxGPT Rate Limiter")

# Configuration
DEFAULT_LIMIT = 100  # requests
DEFAULT_WINDOW = 60000  # 1 minute in milliseconds

async def get_client_id(request: Request):
    # Extract API Key or fall back to IP
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key}"
    
    # Fallback to client IP (useful for testing)
    client_host = request.client.host
    return f"ip:{client_host}"

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip health checks
    if request.url.path == "/health":
        return await call_next(request)

    client_id = await get_client_id(request)
    endpoint = request.url.path
    
    # Check limit
    allowed = limiter.allow_request(
        client_id=client_id,
        endpoint=endpoint,
        limit=DEFAULT_LIMIT,
        window_ms=DEFAULT_WINDOW
    )

    if not allowed:
        analytics.log_violation(client_id, endpoint)
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please retry later."}
        )

    # Log valid request for analytics
    analytics.log_request(client_id, endpoint)
    
    response = await call_next(request)
    
    # Add headers to show remaining quota (optional but nice)
    remaining = DEFAULT_LIMIT - limiter.get_current_usage(client_id, endpoint)
    response.headers["X-RateLimit-Limit"] = str(DEFAULT_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
    
    return response

@app.get("/")
async def root():
    return {"message": "System operational. Try to break it."}

@app.post("/api/resource")
def resource():
    return {"message": "Resource accessed"}

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)