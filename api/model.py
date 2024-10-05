from peewee import Model, CharField, ForeignKeyField, DateField, IntegerField
from db_config import db

# Patient data model
class Patient(Model):
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
