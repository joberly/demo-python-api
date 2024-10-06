import os
import sys
import uvicorn

from api import app
from config import log, settings

if __name__ == "__main__":
    log.info("starting uvicorn")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
