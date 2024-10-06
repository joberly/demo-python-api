from httpx import AsyncClient, ASGITransport
import pytest

from api import app
from model import Patient, Encounter, LineItem, CPTCode

@pytest.fixture(scope='function', autouse=True)
def test_setup_db():
    Patient.delete().execute()
    Encounter.delete().execute()
    LineItem.delete().execute()

# Get empty patient encounter line item list
@pytest.mark.asyncio
async def test_get_patient_encounter_line_items_empty():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    encounter = Encounter.create(patient=patient, date="2021-01-01")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/patients/{patient.id}/encounters/{encounter.id}/line_items/")
        assert response.status_code == 200
        assert response.json() == []

# Add multiple line items for a patient encounter, retrieve them using the API
# and verify that all the data is correct
@pytest.mark.asyncio
async def test_get_patient_encounter_line_items_multiple():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    encounter = Encounter.create(patient=patient, date="2021-01-01")
    line_item_data = [
        {"cpt_code": "99213", "units": 0},
        {"cpt_code": "81001", "units": 1},
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for data in line_item_data:
            response = await ac.post(f"/patients/{patient.id}/encounters/{encounter.id}/line_items/", json=data)
            assert response.status_code == 200
            # Also get the description directly from the database and add it into the data
            cpt_code = CPTCode.get(CPTCode.code == data["cpt_code"])
            data["cpt_code_description"] = cpt_code.description

        response = await ac.get(f"/patients/{patient.id}/encounters/{encounter.id}/line_items/")
        assert response.status_code == 200
        assert len(response.json()) == len(line_item_data)
        for data in line_item_data:
            assert data in response.json()

# Test adding line item to encounter for non-existent patient
@pytest.mark.asyncio
async def test_add_line_item_nonexistent_patient():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/patients/123/encounters/123/line_items/", json={"cpt_code": "99213", "units": 0})
        assert response.status_code == 404
        assert response.json() == {"detail": "patient not found"}


# Test adding line item to encounter for non-existent encounter
@pytest.mark.asyncio
async def test_add_line_item_nonexistent_encounter():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/patients/{patient.id}/encounters/123/line_items/", json={"cpt_code": "99213", "units": 0})
        assert response.status_code == 404
        assert response.json() == {"detail": "encounter not found"}


# Test adding line item with invalid CPT code
@pytest.mark.asyncio
async def test_add_line_item_invalid_cpt_code():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    encounter = Encounter.create(patient=patient, date="2021-01-01")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(f"/patients/{patient.id}/encounters/{encounter.id}/line_items/", json={"cpt_code": "99999", "units": 0})
        assert response.status_code == 404
        assert response.json() == {"detail": "CPT code not found"}

# Test getting line items for invalid patient ID
@pytest.mark.asyncio
async def test_get_line_items_invalid_patient_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/patients/123/encounters/123/line_items/")
        assert response.status_code == 404
        assert response.json() == {"detail": "patient not found"}

# Test getting line items for invalid encounter ID but valid patient ID
@pytest.mark.asyncio
async def test_get_line_items_invalid_encounter_id():
    patient = Patient.create(first_name="Pat", last_name="Doe")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/patients/{patient.id}/encounters/123/line_items/")
        assert response.status_code == 404
        assert response.json() == {"detail": "encounter not found"}
