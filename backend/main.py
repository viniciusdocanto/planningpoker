import uvicorn
import os
from app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Note: Using "app.main:app" for reload to work correctly with uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
