# Set up a quick FastAPI test app.
import uvicorn
from fastapi import FastAPI

from .config import HOST, PORT

app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello Worlds"}

if __name__ == '__main__':
    uvicorn.run(
        app,  # type: ignore
        host=HOST,
        port=PORT
    )
