from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import log
from db_migrate import migrate
from routers import routers

# migrate the database on startup, including preload data
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("starting up")
    migrate()
    yield
    log.info("shutting down")

# create the FastAPI app
app = FastAPI(lifespan=lifespan)

# add the routers to the app
for router in routers:
    app.include_router(router)
