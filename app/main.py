from fastapi import FastAPI

from app.users.user_router import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/api/v1", tags=["users"])


@app.get("/")
def home():
    return {"message": "Hello World!"}
