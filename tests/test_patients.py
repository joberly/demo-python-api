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
async def test_get_patients_single():
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

# Add multiple patients
@pytest.mark.asyncio
async def test_multiple_patients_roundtrip():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        patient_data = [
            {"first_name": "Pat", "last_name": "Doe"},
            {"first_name": "Skylar", "last_name": "Smith"},
            {"first_name": "Alex", "last_name": "Johnson"},
        ]

        for data in patient_data:
            response = await ac.post("/patients/", json=data)
            assert response.status_code == 200
            # Add the patient ID to the data
            data["id"] = response.json()["id"]

        # Get patients
        response = await ac.get("/patients/")
        assert response.status_code == 200

        # Check the response data contains only the patients we added
        assert len(response.json()) == len(patient_data)
        for data in patient_data:
            assert data in response.json()

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
