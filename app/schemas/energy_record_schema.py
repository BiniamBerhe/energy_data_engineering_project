from marshmallow import Schema, fields, validate, ValidationError
from marshmallow import validates_schema
from app.models import (
    EnergyRecord,
    Countries,
    EnergyType,
    EnergyUseType,
    Units,
)


class EnergyRecordSchema(Schema):
    countries = fields.String(
        required=True,
        validate=validate.Length(min=3),
        error_messages={
            "required": "countries is required",
        },
    )
    energy_types = fields.String(
        required=True, error_messages={"required": "energy_types is required"}
    )
    energy_use_types = fields.String(
        required=True, error_messages={"required": "energy_use_types is required"}
    )
    units = fields.String(
        required=True, error_messages={"required": "units is required"}
    )
    year = fields.Integer(
        required=True,
        error_messages={
            "required": "year is required",
            "invalid": "year must be an integer",
        },
    )
    energy_consumption = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={
            "required": "energy_consumption is required",
            "range": "energy_consumption must be greater than or equal to 0",
            "invalid": "energy_consumption must be a float",
        },
    )

    @validates_schema(skip_on_field_errors=True)
    def validate_unique(self, data, **kwargs):
        # Retrieve related instances from the database
        countries = Countries.query.filter_by(name=data["countries"]).first()
        energy_types = EnergyType.query.filter_by(code=data["energy_types"]).first()
        energy_use_types = EnergyUseType.query.filter_by(
            type=data["energy_use_types"]
        ).first()
        units = Units.query.filter_by(name=data["units"]).first()

        # Check for duplicate records in the database only on POST
        existing_record = EnergyRecord.query.filter_by(
            countries=countries,
            energy_types=energy_types,
            energy_use_types=energy_use_types,
            units=units,
            year=data["year"],
            energy_consumption=data["energy_consumption"],
        ).first()

        if existing_record:
            raise ValidationError("Duplicate record")

    @validates_schema(skip_on_field_errors=True)
    def validate_existing_record(self, data, **kwargs):
        # This validation applies only for PUT requests
        if self.context.get("put_request"):
            print("Validating existing record for PUT request.")
        else:
            print("Validation skipped for non-PUT request.")
