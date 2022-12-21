# Set up a quick FastAPI test app.
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello Worlds"}

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,  # type: ignore
        host=host,
        port=port
    )
