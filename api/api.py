from datetime import datetime
from fastapi import FastAPI, HTTPException
from peewee import IntegrityError
from typing import TypedDict

from api_output import EncounterOutput, LineItemOutput, PatientOutput
import model
from model import Patient, CPTCode, Encounter, LineItem

app = FastAPI()

# Patients API endpoints

@app.post("/patients/")
async def add_patient(first_name: str, last_name: str):
    try:
        patient = Patient.create(first_name=first_name, last_name=last_name)
        return PatientOutput.from_patient(patient)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure creating patient")
    
@app.get("/patients/{patient_id}")
async def get_patient(patient_id: int):
    try:
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")
        return PatientOutput.from_patient(patient)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure retrieving patient")

# Patient encounters API endpoints

@app.post("/patients/{patient_id}/encounters/")
async def add_encounter(patient_id: int, date: str):
    try:
        # Check the date format first
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid date format")
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")
        # Create the new patient encounter
        encounter = Encounter.create(patient=patient, date=date)
        return EncounterOutput.from_encounter(encounter)

    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure creating encounter")

@app.get("/patients/{patient_id}/encounters/")
async def get_encounters(patient_id: int):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")

        # Retrieve encounters
        # This might be a bit inefficient as it retrieves all encounters for the patient
        # but for this demo, we'll let it go.
        patient.encounters.dicts().execute()
        return [ EncounterOutput.from_encounter(encounter) for encounter in patient.encounters ]
    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure retrieving encounters")

@app.get("/patients/{patient_id}/encounters/{encounter_id}")
async def get_encounter(patient_id: int, encounter_id: int):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")

        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.uuid == encounter_id, Encounter.patient == patient_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="encounter not found")

        return EncounterOutput.from_encounter(encounter)

    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure retrieving encounter")

# Patient encounter line items API endpoints

@app.post("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
async def add_line_item(patient_id: int, encounter_id: int, cpt_code: str, units: int):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")
        
        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.uuid == encounter_id, Encounter.patient == patient_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="encounter not found")
        
        # Check if the CPT code exists
        cpt = CPTCode.get_or_none(CPTCode.code == cpt_code)
        if not cpt:
            raise HTTPException(status_code=404, detail="CPT code not found")
        
        # Create the line item
        line_item = LineItem.create(encounter=encounter, cpt_code=cpt, units=units)
        return { "success": True }
    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure creating line item")

@app.get("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
async def get_line_items(patient_id: int, encounter_id: int):
    try:
        # Check if the patient exists and retrieve
        patient = Patient.get_or_none(Patient.id == patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")
        
        # Check if the encounter exists and retrieve
        encounter = Encounter.get_or_none(Encounter.uuid == encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="encounter not found")
        
        # Ensure the encounter is for this patient
        if encounter.patient != patient:
            raise HTTPException(status_code=404, detail="encounter not found")
        
        # Retrieve line items with CPT code descriptions
        # This might also be a bit inefficient because an encounter might have
        # a lot of line items, but for the purposes of a demo, we'll let it go.
        line_items = model.get_line_items_for_encounter(encounter)
        return [ LineItemOutput.from_line_item(line_item) for line_item in line_items ]

    except IntegrityError:
        raise HTTPException(status_code=400, detail="failure retrieving line items")
