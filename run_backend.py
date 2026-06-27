"""
Run FastAPI backend server
"""
import uvicorn

if __name__ == "__main__":
    print("="*60)
    print("STARTING REGINTEL AI COMPLIANCE BACKEND")
    print("="*60)
    print("\nBackend will start on: http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Alternative Docs: http://localhost:8000/api/redoc")
    print("\nPress CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
