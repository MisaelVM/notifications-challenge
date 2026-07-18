from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.users.user_router import router as user_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/api/v1", tags=["users"])


@app.get("/")
def home():
    return {"message": "Hello World!"}
