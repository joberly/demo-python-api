import os
import pytest
import sys

# code path magic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

# put this after the magic so it magically works
from db_migrate import migrate

# set things up just like the app does
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    migrate()
