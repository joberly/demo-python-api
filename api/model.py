from peewee import Model, CharField, ForeignKeyField, DateField, IntegerField, UUIDField
from typing import List
import uuid

from db_config import db

# Patient data model
class Patient(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    first_name = CharField()
    last_name = CharField()

    class Meta:
        database = db

# Current Procedural Terminology (CPT) code data model
class CPTCode(Model):
    code = CharField(unique=True)
    description = CharField()

    class Meta:
        database = db

# Encounter data model
class Encounter(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4)
    patient = ForeignKeyField(Patient, backref='encounters')
    date = DateField()

    class Meta:
        database = db

# Line item data model
class LineItem(Model):
    encounter = ForeignKeyField(Encounter, backref='line_items')
    cpt_code = ForeignKeyField(CPTCode)
    units = IntegerField()

    class Meta:
        database = db

# Get extended line items for an encounter
# This is probably a bit inefficient because an encounter might have
# many line items, AND we're joining it with the CPT table to get code
# descriptions. This might be a good candidate for a more efficient query.
# For the demo, we'll keep it simple.
def get_line_items_for_encounter(encounter: Encounter) -> List[LineItem]:
    return (LineItem
        .select()
        .join(CPTCode)
        .where(LineItem.encounter == encounter)
        .execute())
