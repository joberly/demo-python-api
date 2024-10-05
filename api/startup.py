from api import app
from config import log
from db_migrate import migrate

@app.on_event("startup")
def startup_event():
    log.info("starting up")
    migrate()
