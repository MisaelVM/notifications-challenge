from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.core.database import engine
from app.core.exception_handlers import (
    register_exception_handlers,
)
from app.core.logger import setup_logging
from app.notifications.router import router as notifications_router
from app.users.router import router as user_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(log_level="DEBUG")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(user_router, prefix="/api/v1", tags=["users"])
app.include_router(notifications_router, prefix="/api/v1", tags=["notifications"])


@app.get("/")
def home():
    return {"message": "Hello World!"}


app.mount("/", StaticFiles(directory="static"), name="static")
