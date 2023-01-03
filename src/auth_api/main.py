# Set up a quick FastAPI test app.
import uvicorn
from fastapi import FastAPI

from .api.v1 import router as v1_router
from .config import HOST, PORT

app = FastAPI()

app.include_router(v1_router, prefix='/api/v1', tags=['api/v1'])


if __name__ == '__main__':
    uvicorn.run(
        app,  # type: ignore
        host=HOST,
        port=PORT
    )
