import uvicorn

from backend.config import settings
from backend.main import app

if __name__ == "__main__":
    uvicorn.run("run:app", host=settings.HOST, port=settings.PORT, reload=True)
