import os
import pytest
import sys

# Add the root directory of your project to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './src/api')))

from db_migrate import migrate

# set things up just like the app does
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    migrate()
