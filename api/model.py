from peewee import Model, CharField, ForeignKeyField, DateField, IntegerField, UUIDField
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

# For now, create the tables if they don't exist.
# In production we'd use a migration tool but this is fine for a demo.
db.create_tables([Patient, CPTCode, Encounter, LineItem])
