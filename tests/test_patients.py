from httpx import AsyncClient, ASGITransport
import pytest

from api import app
from model import Patient

@pytest.fixture(autouse=True)
def test_setup_db():
    Patient.delete().execute()

# Get empty patients list
@pytest.mark.asyncio
async def test_get_patients_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/patients/")
        assert response.status_code == 200
        assert response.json() == []

# Get single patient in list
@pytest.mark.asyncio
async def test_get_patients():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/patients/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(patient.id),
                "first_name": "Pat",
                "last_name": "Doe",
            }
       ]

# Get single patient by ID
@pytest.mark.asyncio
async def test_get_patient():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/patients/{patient.id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": str(patient.id),
            "first_name": "Pat",
            "last_name": "Doe",
        }
