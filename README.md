# demo-python-api
Demo Python REST API using Postgres deployed with Kubernetes

## Description

This is a demo Python REST API using Postgres as its database, deploying with Kubernetes. It's a mock healthcare provider billing system. The database schema has tables for patients, encounters, line items, and [Current Procedural Terminology (CPT) codes](https://www.aapc.com/resources/what-is-cpt).

## Running the Demo

Note that this was developed on a system with the following specs:
- Windows 11
- Docker Desktop 4.34.2
- Docker Desktop Kubernetes 1.30.2

Your mileage may vary a bit with other systems, but it _should_ generally work. :)

### Prerequisites

Manually install the following before getting started.

1. Install Docker Desktop
2. Enable Kubernetes in Docker Desktop
3. Install Python 3.11
4. Install curl to send requests to the API.

### Install 

Run `make install` to install code dependencies.

### Test

Run `make test` to run unit tests with code coverage output.

### Docker Registry

Run `make registry` to run the Docker Registry locally with Docker. Since this isn't something we'd normally use in a production environment, we'll just run it with Docker locally on port 5000. This enables Kubernetes to find local images. Running `make push` will ensure the registry is running. 

### Predeploy

Run `make predeploy` to deploy some things that are needed to run the demo. This installs the [ingress-nginx controller](https://kubernetes.github.io/ingress-nginx/) to allow ingress to our API running in Kubernetes.

### Deploy

Run `make deploy` to deploy a [Postgres database](deploy/01-postgres.yaml) as well as the [demo API](deploy/02-api.yaml) on Kubernetes. This ensures the image is pushed to the local registry and predeploy steps are done.

## Using the API

Use `curl` to send requests to the API locally with HTTP on port 80. Here are some example runs:

```
$ curl -X POST -H "Content-Type: application/json" -d '{"first_name": "John", "last_name": "Oberly"}' http://localhost:80/patients/
{"id":"13d62589-66b8-414f-ba05-7e4fc1c3ac1b","first_name":"John","last_name":"Oberly"}

$ curl -X GET http://localhost:80/patients/
[{"id":"13d62589-66b8-414f-ba05-7e4fc1c3ac1b","first_name":"John","last_name":"Oberly"}]

$ curl -X GET http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b
{"id":"13d62589-66b8-414f-ba05-7e4fc1c3ac1b","first_name":"John","last_name":"Oberly"}

$ curl -X POST -H "Content-Type: application/json" -d '{"date": "2024-01-01"}' http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b/encounters/
{"id":"ffa61c9a-9de2-4bec-8590-d174ff386db7","date":"2024-01-01"}

$ curl -X GET http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b/encounters/
[{"id":"ffa61c9a-9de2-4bec-8590-d174ff386db7","date":"2024-01-01"}]

$ curl -X GET http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b/encounters/ffa61c9a-9de2-4bec-8590-d174ff386db7
{"id":"ffa61c9a-9de2-4bec-8590-d174ff386db7","date":"2024-01-01"}

$ curl -X POST -H "Content-Type: application/json" -d '{"cpt_code": "99213", "units": 0}' http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b/encounters/ffa61c9a-9de2-4bec-8590-d174ff386db7/line_items/
{"cpt_code":"99213","cpt_code_description":"Office or other outpatient visit, established patient, moderate","units":0}

$ curl -X GET -H "Content-Type: application/json" http://localhost:80/patients/13d62589-66b8-414f-ba05-7e4fc1c3ac1b/encounters/ffa61c9a-9de2-4bec-8590-d174ff386db7/line_items/
[{"cpt_code":"99213","cpt_code_description":"Office or other outpatient visit, established patient, moderate","units":0}]
```

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

### POST /patients/

Creates a patient.

#### Input

JSON object body:
- `first_name`: string
- `last_name`: string

#### Output

JSON object:
- `id`: UUID
- `first_name`: string
- `last_name`: string

### GET /patients/

Retrieves all patients.

#### Input

None

#### Output

JSON list of objects each containing the following:
- `id`: UUID
- `first_name`: string
- `last_name`: string

### GET /patients/{patient_id}/

Retrieves a patient.

#### Input

In URL:
- `patient_id`: UUID of patient

#### Output

JSON object:
- `id`: UUID
- `first_name`: string
- `last_name`: string


### POST /patients/{patient_id}/encounters/

Creates a patient encounter.

#### Input

In URL:
- `patient_id`: UUID of patient

JSON object body:
- `date`: Date (YYYY-mm-dd format) of encounter

#### Output

JSON object:
- `id`: Globally unique UUID of encounter
- `date`: Date of encounter

### GET /patients/{patient_id}/encounters/

#### Input

In URL:
- `patient_id`: UUID of patient

#### Output

JSON list of objects each containing the following:
- `id`: Globally unique UUID of encounter
- `date`: Date of encounter

### GET /patients/{patient_id}/encounters/{encounter_id}/

#### Input

In URL:
- `patient_id`: UUID of patient
- `encounter_id`: UUID of patient encounter

#### Output

JSON object:
- `id`: Globally unique UUID of encounter
- `date`: Date of encounter

### POST /patients/{patient_id}/encounters/{encounter_id}/line_items/

#### Input

In URL:
- `patient_id`: UUID of patient
- `encounter_id`: UUID of patient encounter

JSON object body:
- `cpt_code`: string, CPT code for line item
- `units`: int, number of units for line item

#### Output

JSON object:
- `cpt_code`: string, CPT code for line item
- `cpt_code_description`: string, CPT code description
- `units`: int, number of units for line item

### GET /patients/{patient_id}/encounters/{encounter_id}/line_items/

#### Input

In URL:
- `patient_id`: UUID of patient
- `encounter_id`: UUID of patient encounter

#### Output

JSON list of objects each containing the following:
- `cpt_code`: string, CPT code for line item
- `cpt_code_description`: string, CPT code description
- `units`: int, number of units for line item

## Internals

- Peewee for the ORM because it's light.
- FastAPI for the REST API middleware because it's light too.
- Postgres for the database because it's easy to deploy for demo purposes.
- SQLite for unit testing because it doesn't need deployment.
- Kubernetes for deployment because who doesn't like making their local machine go **_brrrrrr_**.
- Tables are created and CPT codes are loaded at API start as part of an internal database migration step.

## Test Coverage

Some bad paths are not tested just for the purposes of a demo, but bad _inputs_ do have some coverage.

```
---------- coverage: platform win32, python 3.11.9-final-0 -----------
Name                            Stmts   Miss  Cover
---------------------------------------------------
conftest.py                         8      0   100%
src\api\api.py                     14      4    71%
src\api\config.py                   5      0   100%
src\api\db_config.py               13      4    69%
src\api\db_migrate.py              21      0   100%
src\api\model.py                   29      0   100%
src\api\routers\__init__.py         6      0   100%
src\api\routers\api_input.py        9      0   100%
src\api\routers\api_output.py      22      0   100%
src\api\routers\encounters.py      54     19    65%
src\api\routers\health.py           7      1    86%
src\api\routers\line_items.py      46      4    91%
src\api\routers\patients.py        32      5    84%
src\api\routers\routers.py          3      0   100%
---------------------------------------------------
TOTAL                             269     37    86%
```

## Known Issues

Health checks spam the logs a bit.
