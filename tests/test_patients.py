from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from api import app
from model import Patient

@pytest.fixture(autouse=True)
def test_setup_db():
    Patient.delete().execute()

@pytest.mark.asyncio
async def test_get_patients_empty():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/patients/")
        assert response.status_code == 200
        assert response.json() == []

@pytest.mark.asyncio
async def test_get_patients():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/patients/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(patient.id),
                "first_name": "Pat",
                "last_name": "Doe",
            }
       ]
