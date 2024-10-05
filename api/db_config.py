import os
from peewee import SqliteDatabase, PostgresqlDatabase
from config import settings

# Initialize the database connection based on driver type
db = None
db_driver = settings.DATABASE_DRIVER
match db_driver:
    # SQLite database from file
    case 'sqlite':
        db = SqliteDatabase(settings.DATABASE_NAME)
    # PostgreSQL database connection
    case 'postgresql':
        db = PostgresqlDatabase(
            settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
        )
    case _:
        raise ValueError(f"unsupported database driver: {db_driver}")
