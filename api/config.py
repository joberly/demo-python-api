from dynaconf import Dynaconf

# Load settings from a .env file if present, otherwise get them from the environment.
# Expected environment variables:
# - DEMO_DATABASE_DRIVER: sqlite or postgresql
# - DEMO_DATABASE_NAME: database name
# - DEMO_DATABASE_USER: database user (only for postgresql)
# - DEMO_DATABASE_PASSWORD: database password (only for postgresql)
# - DEMO_DATABASE_HOST: database host (only for postgresql)
# - DEMO_DATABASE_PORT: database port (only for postgresql)

settings = Dynaconf(
    envvar_prefix="DEMO",
    settings_files=['.env'],
    environments=True,
    load_dotenv=True,
)
