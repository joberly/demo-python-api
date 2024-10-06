from fastapi import APIRouter, HTTPException
from peewee import IntegrityError

from .api_input import LineItemInput
from .api_output import LineItemOutput
from config import log
import model
from model import Patient, CPTCode, Encounter, LineItem
from .routers import routers

router = APIRouter()

# Patient encounter line items API endpoints

@router.post("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
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

@router.get("/patients/{patient_id}/encounters/{encounter_id}/line_items/")
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

routers.append(router)
