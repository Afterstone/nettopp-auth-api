# Set up a quick FastAPI test app.
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Worlds"}
