from config import log
from db_config import db
from model import Patient, CPTCode, Encounter, LineItem

"""
Preload CPT codes from cpt_codes.csv. Again, this is not something you'd want to
do like this in production. In production, we'd probably have some kind of
external process that would read them from an object in a bucket or something
and add them to the database. We'd also have to deal with updates and deletions
and how that affects related data in other tables. For the purposes of a demo,
this is fine.
"""
def preload_cpt_codes():
    with open("cpt_codes.csv") as f:
        for line in f:
            code, description = line.strip().split(",")
            CPTCode.create(code=code, description=description)
    num_cpt_codes = CPTCode.select().count()
    log.info(f"preloaded {num_cpt_codes} CPT codes")

"""
For now, create the tables if they don't exist.
In production we'd use a migration tool but this is fine for a demo.
See above for CPT code preload notes.
"""
def migrate():
    log.info("creating tables")
    db.create_tables([Patient, CPTCode, Encounter, LineItem])
    log.info("tables created")
    log.info("preloading CPT codes")
    preload_cpt_codes()
    log.info("CPT codes preloaded")
