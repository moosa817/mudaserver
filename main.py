from fastapi import FastAPI
import uvicorn
from app.core.config import config


def main():
    uvicorn.run(app="app.server:app",reload=True,host="0.0.0.0",port=8000)

if __name__ == "__main__":
    main()