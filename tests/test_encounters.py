from httpx import AsyncClient, ASGITransport
import pytest

from api import app
from model import Patient, Encounter

@pytest.fixture(autouse=True)
def test_setup_db():
    Patient.delete().execute()

# Get empty patient encounters list
@pytest.mark.asyncio
async def test_get_patient_encounters_empty():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/patients/{patient.id}/encounters/")
        assert response.status_code == 200
        assert response.json() == []

# Get single patient encounter in list
@pytest.mark.asyncio
async def test_get_patient_encounters_single():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    encounter = Encounter.create(patient=patient, date="2021-01-01")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/patients/{patient.id}/encounters/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(encounter.id),
                "date": "2021-01-01",
            }
        ]
