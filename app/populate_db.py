# populate_db.py
import sys
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.models import Countries, EnergyType, EnergyUseType, Units, EnergyRecord
from process_energy_data import process_and_predict_energy_consumption

"""_summary_
    We populate our database in bulk using a batch processing strategy. This approach involves gathering a set of records in memory before inserting them collectively, optimizing the process of data insertion.
    """


# Function to get or create objects and return a mapping
def get_or_create_object(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        try:
            session.flush()  # Attempt to flush objects to the database
        except IntegrityError:  # Catch duplicates and other database integrity issues
            session.rollback()  # Flush failed, object likely already exists
            instance = (
                session.query(model).filter_by(**kwargs).first()
            )  # Try to get it again
        return instance


# Load and insert data using bulk operations
def load_data(session, data):
    # Maps to store references to already created objects
    countries_lookup = {}
    energy_type_lookup = {}
    energy_use_type_lookup = {}
    units_lookup = {}

    # List to hold new EnergyRecord objects for bulk insertion
    records_to_insert = []

    for entry in data:
        energy_consumption = (
            float(entry["energy_consumption"])
            if pd.notna(entry["energy_consumption"])
            else None
        )
        year = entry["year"]
        countries = entry["countries"]
        energy_types = entry["energy_types"]
        energy_use_types = entry["energy_use_types"]
        units = entry["units"]

        # Get or create related objects and update lookups
        if countries not in countries_lookup:
            countries_lookup[countries] = get_or_create_object(
                session, Countries, name=countries
            )
        if energy_types not in energy_type_lookup:
            energy_type_lookup[energy_types] = get_or_create_object(
                session, EnergyType, code=energy_types
            )
        if energy_use_types not in energy_use_type_lookup:
            energy_use_type_lookup[energy_use_types] = get_or_create_object(
                session, EnergyUseType, type=energy_use_types
            )
        if units not in units_lookup:
            units_lookup[units] = get_or_create_object(session, Units, name=units)

        # Create new EnergyRecord object
        records_to_insert.append(
            EnergyRecord(
                countries_id=countries_lookup[countries].id,
                energy_types_id=energy_type_lookup[energy_types].id,
                energy_use_types_id=energy_use_type_lookup[energy_use_types].id,
                units_id=units_lookup[units].id,
                year=year,
                energy_consumption=energy_consumption,
            )
        )

    # Bulk insert new records
    session.bulk_save_objects(records_to_insert)
    session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # Extract data
        data_df = process_and_predict_energy_consumption()

        # Convert DataFrame to a list of dictionaries
        data = data_df.to_dict("records")

        # Insert data in a new session with bulk operations
        session = Session(bind=db.engine)
        try:
            load_data(session, data)
            print("Data inserted successfully")
        except Exception as e:
            print(f"Error during bulk insert: {e}", file=sys.stderr)
        finally:
            session.close()
