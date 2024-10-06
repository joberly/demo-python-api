from httpx import AsyncClient, ASGITransport
import pytest

from api import app
from model import Patient, Encounter

@pytest.fixture(scope='function', autouse=True)
def test_setup_db():
    Patient.delete().execute()
    Encounter.delete().execute()

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

# Test adding encounter to non-existent patient
@pytest.mark.asyncio
async def test_add_encounter_nonexistent_patient():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/patients/123/encounters/", json={"date": "2021-01-01"})
        assert response.status_code == 404
        assert response.json() == {"detail": "patient not found"}

# Test adding encounter with invalid date format
@pytest.mark.asyncio
async def test_add_encounter_invalid_date_format():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/patients/{patient.id}/encounters/", json={"date": "not-a-date"})
        assert response.status_code == 400
        assert response.json() == {"detail": "invalid date format"}

# Test get patient encounters for an invalid patient ID
@pytest.mark.asyncio
async def test_get_patient_encounters_invalid_patient_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/patients/123/encounters/")
        assert response.status_code == 404
        assert response.json() == {"detail": "patient not found"}
