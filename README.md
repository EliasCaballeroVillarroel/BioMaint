# BioMaint

**Medical Equipment Maintenance Management System — Prototype**

BioMaint is a personal software project focused on organizing medical equipment maintenance information in healthcare facilities.

The project aims to centralize equipment records, locations, failures, maintenance activities, technicians, and service contracts, providing a foundation for future maintenance tracking and data analysis.

## Current features

- Management of clinics, locations, and medical equipment.
- Failure registration and tracking.
- Maintenance records associated with equipment and, optionally, failures.
- Assignment of technicians to maintenance activities.
- Service contract management.
- Relational data modeling using SQLAlchemy and MySQL.
- CRUD operations implemented in Python.

## Tech stack

- **Language:** Python
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Configuration:** python-dotenv

## Project status

BioMaint is under active development. The current version focuses on the relational data model and CRUD operations. An HTTP API, automated testing, and future data-analysis features are planned.

This is a portfolio and learning project, not a validated clinical or hospital production system.

## Planned improvements

- Build a REST API with FastAPI.
- Improve validation and error handling.
- Add automated tests.
- Containerize the application with Docker.
- Explore equipment maintenance analytics and predictive maintenance.

## Local setup

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the dependencies listed in `requirements.txt`.
4. Copy `.env.example` to `.env` and fill in your MySQL connection settings (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`).
5. Create the databases with `python -m database.inicializar_bases`. This creates the development database (`DB_NAME`) with its tables and sample data from `database/semillas/llenado_tablas_biomaint.sql`, plus an empty `biomaint_test` database for the test suite. It is safe to run again: it skips loading if the development database already has data.
6. Start the API with `uvicorn main:app --reload` (docs at http://127.0.0.1:8000/docs) or run the tests with `pytest`.

Never commit database credentials or other secrets to the repository.

## Author

Developed as a personal software and data engineering portfolio project, combining biomedical engineering knowledge with Python and relational database development.