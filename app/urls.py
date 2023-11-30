from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from . import db
from app.schemas.energy_record_schema import EnergyRecordSchema
from app.models import (
    EnergyRecord,
    Countries,
    EnergyType,
    EnergyUseType,
    Units,
)

energy_record_schema = EnergyRecordSchema()
api_blueprint = Blueprint("api", __name__)


# Separate route for the root endpoint (Welcome message)
@api_blueprint.route("/", methods=["GET"])
def root():
    return "Welcome to the Energy Data API!"


@api_blueprint.route("/energy_records/", methods=["GET", "POST"])
def energy_records():
    if request.method == "GET":
        # Return all energy records
        records = EnergyRecord.query.all()
        records_data = [
            {
                "id": record.id,
                "countries": record.countries.name,
                "energy_types": record.energy_types.code,
                "energy_use_types": record.energy_use_types.type,
                "units": record.units.name,
                "year": record.year,
                "energy_consumption": record.energy_consumption,
            }
            for record in records
        ]
        return jsonify(records_data)

    elif request.method == "POST":
        data = request.get_json()
        try:
            # Validate the incoming JSON data with the Marshmallow schema
            validated_data = energy_record_schema.load(data)

            # If the data is valid, proceed to fetch related instances
            countries = Countries.query.filter_by(
                name=validated_data["countries"]
            ).first()
            energy_types = EnergyType.query.filter_by(
                code=validated_data["energy_types"]
            ).first()
            energy_use_types = EnergyUseType.query.filter_by(
                type=validated_data["energy_use_types"]
            ).first()
            units = Units.query.filter_by(name=validated_data["units"]).first()

            validated_data = energy_record_schema.load(data)
            new_record = EnergyRecord(
                countries=countries,
                energy_types=energy_types,
                energy_use_types=energy_use_types,
                units=units,
                year=validated_data["year"],
                energy_consumption=validated_data["energy_consumption"],
            )

            db.session.add(new_record)
            db.session.commit()
            return jsonify({"message": "New energy record added successfully!"}), 201

        except ValidationError as e:
            # Return the validation errors from Marshmallow
            return jsonify({"error": "Validation error", "messages": e.messages}), 400


@api_blueprint.route(
    "/energy_record_detail/<int:record_id>", methods=["GET", "PUT", "DELETE"]
)
def energy_record_detail(record_id):
    if request.method == "GET":
        # Return a specific energy record
        record = EnergyRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Energy Record not found!"}), 404

        record_data = {
            "id": record.id,
            "countries": record.countries.name,
            "energy_types": record.energy_types.code,
            "energy_use_types": record.energy_use_types.type,
            "units": record.units.name,
            "year": record.year,
            "energy_consumption": record.energy_consumption,
        }
        return jsonify(record_data), 200

    elif request.method == "PUT":
        data = request.get_json()
        record = EnergyRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Energy Record not found!"}), 404

        energy_record_schema.context["put_request"] = True

        try:
            validated_data = energy_record_schema.load(data, partial=True)
            for key, value in validated_data.items():
                if key == "countries":
                    country_instance = Countries.query.filter_by(name=value).first()
                    if not country_instance:
                        return (
                            jsonify({"error": f"Country name {value} not found!"}),
                            404,
                        )
                    record.countries = country_instance
                elif key == "energy_types":
                    energy_type_instance = EnergyType.query.filter_by(
                        code=value
                    ).first()
                    if not energy_type_instance:
                        return (
                            jsonify({"error": f"Energy type code {value} not found!"}),
                            404,
                        )
                    record.energy_types = energy_type_instance
                elif key == "energy_use_types":
                    energy_use_type_instance = EnergyUseType.query.filter_by(
                        type=value
                    ).first()
                    if not energy_use_type_instance:
                        return (
                            jsonify({"error": f"Energy use type {value} not found!"}),
                            404,
                        )
                    record.energy_use_types = energy_use_type_instance
                elif key == "units":
                    unit_instance = Units.query.filter_by(name=value).first()
                    if not unit_instance:
                        return jsonify({"error": f"Unit name {value} not found!"}), 404
                    record.units = unit_instance
                else:
                    setattr(record, key, value)

            db.session.commit()
            return jsonify({"message": "Energy Record updated successfully!"}), 200
        except ValidationError as e:
            return jsonify({"error": "Validation error", "messages": e.messages}), 400

    elif request.method == "DELETE":
        # Delete an existing energy record
        record = EnergyRecord.query.get(record_id)
        if not record:
            return jsonify({"error": "Energy Record not found!"}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Energy Record deleted successfully!"}), 200
