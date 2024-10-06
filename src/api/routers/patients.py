from fastapi import APIRouter, HTTPException
from peewee import IntegrityError

from .api_input import PatientInput
from .api_output import PatientOutput
from config import log
from model import Patient
from .routers import routers

router = APIRouter()

# Patients API endpoints

@router.post("/patients/")
async def add_patient(patient: PatientInput):
    try:
        patient = Patient.create(first_name=patient.first_name, last_name=patient.last_name)
        return PatientOutput.from_patient(patient)
    except IntegrityError:
        log.error("failure creating patient")
        raise HTTPException(status_code=400, detail="failure creating patient")

@router.get("/patients/")
async def get_patients():
    patients = Patient.select()
    return [ PatientOutput.from_patient(patient) for patient in patients ]
    
@router.get("/patients/{patient_id}")
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

routers.append(router)
