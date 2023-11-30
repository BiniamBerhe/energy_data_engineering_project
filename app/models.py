from . import db


class Countries(db.Model):
    __tablename__ = "countries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    energy_records = db.relationship("EnergyRecord", backref="countries", lazy=True)


class EnergyType(db.Model):
    __tablename__ = "energy_types"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False, unique=True)
    energy_records = db.relationship("EnergyRecord", backref="energy_types", lazy=True)


class EnergyUseType(db.Model):
    __tablename__ = "energy_use_types"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False, unique=True)
    energy_records = db.relationship(
        "EnergyRecord", backref="energy_use_types", lazy=True
    )


class Units(db.Model):
    __tablename__ = "units"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    energy_records = db.relationship("EnergyRecord", backref="units", lazy=True)


class EnergyRecord(db.Model):
    __tablename__ = "energy_records"
    id = db.Column(db.Integer, primary_key=True)
    countries_id = db.Column(
        db.Integer, db.ForeignKey("countries.id"), nullable=False, index=True
    )
    energy_types_id = db.Column(
        db.Integer, db.ForeignKey("energy_types.id"), nullable=False, index=True
    )
    energy_use_types_id = db.Column(
        db.Integer, db.ForeignKey("energy_use_types.id"), nullable=False, index=True
    )
    units_id = db.Column(
        db.Integer, db.ForeignKey("units.id"), nullable=False, index=True
    )
    year = db.Column(db.Integer, nullable=False)
    energy_consumption = db.Column(db.Float, nullable=False)
