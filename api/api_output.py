from model import Patient, Encounter, CPTCode, LineItem
from typing import TypedDict

# Data output classes
class PatientOutput(TypedDict):
    id: str
    first_name: str
    last_name: str

    @classmethod
    def from_patient(cls, patient: Patient) -> "PatientOutput":
        return cls(
            id=str(patient.id),
            first_name=patient.first_name,
            last_name=patient.last_name,
        )

class EncounterOutput(TypedDict):
    uuid: str
    date: str

    @classmethod
    def from_encounter(cls, encounter: Encounter) -> "EncounterOutput":
        return cls(
            uuid=str(encounter.uuid),
            date=str(encounter.date),
        )

class LineItemOutput(TypedDict):
    cpt_code: str
    cpt_code_description: str
    units: int

    @classmethod
    def from_line_item(cls, line_item: LineItem) -> "LineItemOutput":
        return cls(
            cpt_code=line_item.cpt_code.code,
            cpt_code_description=line_item.cpt_code.description,
            units=line_item.units,
        )
