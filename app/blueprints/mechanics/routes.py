from app.blueprints.mechanics import mechanics_bp
from app.models import Mechanics, db
from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import service_tickets_schema
from werkzeug.security import generate_password_hash, check_password_hash

@mechanics_bp.route('', methods=["POST"])
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check if email exist or not because email is unique attribute
    exist_mechanic = db.session.query(Mechanics).where(Mechanics.email == data["email"]).first()
    if exist_mechanic:
        return jsonify({"error" : f"{data["email"]} is already associated with a mechanic's account."}), 400
    data["password"] = generate_password_hash(data["password"])
    new_mechanic = Mechanics(**data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route('', methods=["GET"])
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route('/<int:mechanic_id>', methods=["GET"])
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route('/<int:mechanic_id>', methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted mechanic with id: {mechanic_id}"}), 200
   
@mechanics_bp.route('/<int:mechanic_id>', methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
       return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check the email Mechanic wants to update not be taken with another mechanic
    existing_email = db.session.query(Mechanics).where(Mechanics.email == mechanic_data["email"], Mechanics.id != mechanic_id).first()
    if existing_email:
        return jsonify({"error" : f"{mechanic_data["email"]} is already taken with another mechanic."}), 400
    mechanic_data["password"] = generate_password_hash(mechanic_data["password"])
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully mechanic with id: {mechanic_id} updated."}), 200

@mechanics_bp.route('/service_tickets/<int:mechanic_id>',methods=["GET"])
def read_mechanic_service_tickets(mechanic_id):
    mechanic = db.session.get(Mechanics,mechanic_id)
    if not mechanic:
        return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    return service_tickets_schema.jsonify(mechanic.tickets), 200
