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
{"id":"52d8a27a-4596-4713-99bf-4d7115da1762","first_name":"John","last_name":"Oberly"}

$ curl -X GET http://localhost:80/patients/
[{"id":"52d8a27a-4596-4713-99bf-4d7115da1762","first_name":"John","last_name":"Oberly"}]

$ curl -X GET http://localhost:80/patients/52d8a27a-4596-4713-99bf-4d7115da1762
{"id":"52d8a27a-4596-4713-99bf-4d7115da1762","first_name":"John","last_name":"Oberly"}
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
