from datetime import datetime
from fastapi import APIRouter, HTTPException
from peewee import IntegrityError

from .api_input import EncounterInput
from .api_output import EncounterOutput
from config import log
from model import Patient, Encounter
from .routers import routers

router = APIRouter()

# Patient encounters API endpoints

@router.post("/patients/{patient_id}/encounters/")
async def add_patient_encounter(patient_id: str, encounter: EncounterInput):
    try:
        # Check the date format first
        try:
            datetime.strptime(encounter.date, "%Y-%m-%d")
        except ValueError:
            log.info("invalid encounter date format", patient_id=patient_id, date=encounter.date)
            raise HTTPException(status_code=400, detail="invalid date format")
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id)
            raise HTTPException(status_code=404, detail="patient not found")
        # Create the new patient encounter
        encounter = Encounter.create(patient=patient, date=encounter.date)
        return EncounterOutput.from_encounter(encounter)

    except IntegrityError:
        log.error("failure creating encounter", patient_id=patient_id, date=encounter.date)
        raise HTTPException(status_code=400, detail="failure creating encounter")

@router.get("/patients/{patient_id}/encounters/")
async def get_patient_encounters(patient_id: str):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id)
            raise HTTPException(status_code=404, detail="patient not found")

        # Retrieve encounters
        # This might be a bit inefficient as it retrieves all encounters for the patient
        # but for this demo, we'll let it go.
        patient.encounters.dicts().execute()
        return [ EncounterOutput.from_encounter(encounter) for encounter in patient.encounters ]
    except IntegrityError:
        log.error("failure retrieving encounters", patient_id=patient_id)
        raise HTTPException(status_code=400, detail="failure retrieving encounters")

@router.get("/patients/{patient_id}/encounters/{encounter_id}")
async def get_patient_encounter(patient_id: str, encounter_id: str):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id, encounter_id=encounter_id)
            raise HTTPException(status_code=404, detail="patient not found")

        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.id == encounter_id, Encounter.patient == patient_id)
        if not encounter:
            log.info("patient encounter not found", patient_id=patient_id, encounter_id=encounter_id)
            raise HTTPException(status_code=404, detail="encounter not found")

        return EncounterOutput.from_encounter(encounter)

    except IntegrityError:
        log.error("failure retrieving encounter", patient_id=patient_id, encounter_id=encounter_id)
        raise HTTPException(status_code=400, detail="failure retrieving encounter")

routers.append(router)
