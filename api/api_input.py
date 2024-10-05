from pydantic import BaseModel

class PatientInput(BaseModel):
    first_name: str
    last_name: str
