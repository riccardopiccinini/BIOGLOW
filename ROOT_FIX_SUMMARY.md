## Fix for 404 Error on Root Path

### Issue:
After deploying the BIOGLOW system to Render, accessing the root URL ("/") returned a 404 Not Found error because no route was defined for the root path in the FastAPI application.

### Fix Applied:
Added a root route to `/backend/main.py`:

```python
@app.get("/")
async def root():
    return {"message": "BIOGLOW Biodiversity Monitoring System is running", "status": "ok", "docs": "/docs"}
```

### Changes Made:
- File: `/backend/main.py`
- Added root route after the `/health` endpoint
- Returns a JSON response with system status and link to documentation

### Verification:
- The updated main.py file compiles successfully with no syntax errors
- The root route will now return a 200 OK response with system status information
- All existing routes remain unchanged

### Deployment Instructions:
Since you're deploying to Render:
1. No local file changes are needed for environment variables (they're set in Render dashboard)
2. Simply push this updated main.py to your repository
3. Trigger a redeploy on Render
4. The root path ("/") will now return a proper response instead of 404

### Expected Behavior:
- GET / → 200 OK with JSON: {"message": "BIOGLOW Biodiversity Monitoring System is running", "status": "ok", "docs": "/docs"}
- All existing endpoints (/ping, /health, /observations, etc.) continue to work as before
