from pydantic import BaseModel

# input body for POST /patients
class PatientInput(BaseModel):
    first_name: str
    last_name: str

# input body for POST /patients/{patient_id}/encounters
class EncounterInput(BaseModel):
    date: str

# input body for POST /patients/{patient_id}/encounters/{encounter_id}/line_items
class LineItemInput(BaseModel):
    cpt_code: str
    units: int
