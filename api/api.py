from datetime import datetime
from fastapi import FastAPI, HTTPException
from peewee import IntegrityError
from typing import TypedDict

from api_input import PatientInput, EncounterInput, LineItemInput
from api_output import EncounterOutput, LineItemOutput, PatientOutput
from config import log
import model
from model import Patient, CPTCode, Encounter, LineItem

app = FastAPI()

# Patients API endpoints

@app.post("/patients/")
async def add_patient(patient: PatientInput):
    try:
        patient = Patient.create(first_name=patient.first_name, last_name=patient.last_name)
        return PatientOutput.from_patient(patient)
    except IntegrityError:
        log.error("failure creating patient")
        raise HTTPException(status_code=400, detail="failure creating patient")

@app.get("/patients/")
async def get_patients():
    patients = Patient.select()
    return [ PatientOutput.from_patient(patient) for patient in patients ]
    
@app.get("/patients/{patient_id}")
async def get_patient(patient_id: str):
    try:
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id)
            raise HTTPException(status_code=404, detail="patient not found")
        return PatientOutput.from_patient(patient)
    except IntegrityError:
        log.error("failure retrieving patient", patient_id=patient_id)
        raise HTTPException(status_code=400, detail="failure retrieving patient")

# Patient encounters API endpoints

@app.post("/patients/{patient_id}/encounters/")
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

@app.get("/patients/{patient_id}/encounters/")
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

@app.get("/patients/{patient_id}/encounters/{encounter_id}")
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

# Patient encounter line items API endpoints

@app.post("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
async def add_patient_encounter_line_item(patient_id: str, encounter_id: str, line_item: LineItemInput):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id, encounter_id=encounter_id)
            raise HTTPException(status_code=404, detail="patient not found")
        
        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.id == encounter_id, Encounter.patient == patient_id)
        if not encounter:
            log.info("encounter not found", patient_id=patient_id, encounter_id=encounter_id)
            raise HTTPException(status_code=404, detail="encounter not found")
        
        # Check if the CPT code exists
        cpt = CPTCode.get_or_none(CPTCode.code == line_item.cpt_code)
        if not cpt:
            log.info("CPT code not found", cpt_code=line_item.cpt_code)
            raise HTTPException(status_code=404, detail="CPT code not found")
        
        # Create the line item
        line_item = LineItem.create(encounter=encounter, cpt_code=cpt, units=line_item.units)

        # Return the line item output data
        return LineItemOutput.from_line_item(line_item)

    except IntegrityError:
        log.error("failure creating line item", patient_id=patient_id, encounter_id=encounter_id)
        raise HTTPException(status_code=400, detail="failure creating line item")

@app.get("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
async def get_patient_encounter_line_items(patient_id: str, encounter_id: str):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            log.info("patient not found", patient_id=patient_id)
            raise HTTPException(status_code=404, detail="patient not found")
        
        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.id == encounter_id, Encounter.patient == patient_id)
        if not encounter:
            log.info("encounter not found", patient_id=patient_id, encounter_id=encounter_id)
            raise HTTPException(status_code=404, detail="encounter not found")
        
        # Retrieve line items with CPT code descriptions
        # This might also be a bit inefficient because an encounter might have
        # a lot of line items, but for the purposes of a demo, we'll let it go.
        line_items = model.get_line_items_for_encounter(encounter)
        return [ LineItemOutput.from_line_item(line_item) for line_item in line_items ]

    except IntegrityError:
        log.error("failure retrieving line items", patient_id=patient_id, encounter_id=encounter_id)
        raise HTTPException(status_code=400, detail="failure retrieving line items")
