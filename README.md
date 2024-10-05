# demo-python-api
Demo Python REST API using Postgres deployed with Kubernetes

## Description

This is a demo Python REST API using Postgres as its database, deploying with Kubernetes. It's a mock healthcare provider billing system. The database schema has tables for patients, encounters, line items, and [Current Procedural Terminology (CPT) codes](https://www.aapc.com/resources/what-is-cpt).

## Data Model

- Patient
  - Has a unique identifier chosen at creation
  - Has many encounters
- Encounter
  - Has one patient
  - Has one date
  - Has many line items
- Line Item
  - Has one encounter
  - Has one CPT code
  - Has one number of units (integer for now, basically just a count)
- CPT Code
  - Has one description
  - No backrefs for now as there will be many, many line items

## API

The API has the following methods:
1. Add a patient - inputs: first and last name of patient, outputs: unique patient ID
2. Add an encounter - inputs: patient ID, date, outputs: unique encounter ID
3. Add a line item - inputs: encounter ID, CPT code
4. Query patient encounters - inputs: patient ID, outputs: list of encounter IDs and dates
5. Query encounter line items - inputs: encounter ID, outputs: patient name, list of line items with their CPT codes with description for each

## Internals

- Peewee for the ORM because it's light.
- FastAPI for the REST API middleware because it's light too.
- Postgres for the database because it's easy to deploy for demo purposes.
- SQLite for unit testing because it doesn't need deployment.
- Kubernetes for deployment because who doesn't like making their local machine go **_brrrrrr_**.
