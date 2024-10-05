from config import settings
from db_config import db
from db_migrate import migrate

def main():
    migrate()
