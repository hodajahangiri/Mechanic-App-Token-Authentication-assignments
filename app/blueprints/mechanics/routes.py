from app.blueprints.mechanics import mechanics_bp
from app.models import Mechanics, db
from .schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import service_tickets_schema
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token, token_required
from app.extensions import limiter, cache

#LOGIN ROUTE
@mechanics_bp.route('/login', methods=['POST'])
@limiter.limit("20 per minute", override_defaults=True)
def login():
    try:
        credential_data = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    mechanic = db.session.query(Mechanics).where(Mechanics.email == credential_data["email"]).first()
    if mechanic and check_password_hash(mechanic.password, credential_data["password"]):
        customer_token = encode_token(mechanic.id, "mechanic")
        response = {
            "message" : f"Successfully logged in. Welcome {mechanic.first_name}",
            "token" : customer_token
        }
        return jsonify(response)
    else:
        return jsonify({"error message" : "Invalid email or password."}), 400

@mechanics_bp.route('', methods=["POST"])
@limiter.limit("10 per hour")
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
    new_mechanic_token = encode_token(new_mechanic.id, "mechanic")
    response = {"mechanic_data" : data,
                "token" : new_mechanic_token}
    return jsonify(response), 201

@mechanics_bp.route('', methods=["GET"])
@limiter.limit("20 per minute", override_defaults=True)
@cache.cached(timeout=10)
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route('/profile', methods=["GET"])
@token_required
def read_mechanic():
    user_role = request.user_role
    if user_role == "mechanic":
        mechanic_id = request.user_id
        mechanic = db.session.get(Mechanics, mechanic_id)
        if not mechanic:
            return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
        return mechanic_schema.jsonify(mechanic), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."}), 400

@mechanics_bp.route('', methods=["DELETE"])
@token_required
def delete_mechanic():
    user_role = request.user_role
    if user_role == "mechanic":
        mechanic_id = request.user_id
        mechanic = db.session.get(Mechanics, mechanic_id)
        if not mechanic:
            return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({"message" : f"Successfully deleted mechanic with id: {mechanic_id}"}), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."}), 400
    

@mechanics_bp.route('', methods=["PUT"])
@token_required
def update_mechanic():
    user_role = request.user_role
    if user_role == "mechanic":
        mechanic_id = request.user_id
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
    else:
        return jsonify({"message" : f"{user_role} is not allowed."}), 400
    
@mechanics_bp.route('/service_tickets',methods=["GET"])
@token_required
def read_mechanic_service_tickets():
    user_role = request.user_role
    if user_role == "mechanic":
        mechanic_id = request.user_id
        mechanic = db.session.get(Mechanics,mechanic_id)
        if not mechanic:
            return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
        return service_tickets_schema.jsonify(mechanic.tickets), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."}), 400
    

@mechanics_bp.route('/hard_work_mechanic', methods=["GET"])
def get_hard_work_mechanic():
    mechanics = db.session.query(Mechanics).all()
    mechanics.sort(key = lambda mechanic : len(mechanic.tickets), reverse=True)
    hard_work_mechanic = mechanics[0]
    response = {
        "mechanic" : mechanic_schema.dump(hard_work_mechanic),
        "tickets_count" : len(hard_work_mechanic.tickets)
    }
    return jsonify(response), 200

@mechanics_bp.route('/sort_by_work', methods=["GET"])
def get_sorted_mechanic_list_by_work():
    mechanics = db.session.query(Mechanics).all()
    mechanics.sort(key = lambda mechanic : len(mechanic.tickets), reverse=True)
    sorted_mechanics_list = []
    for mechanic in mechanics:
        mechanic_result_format = {
            "mechanic" : mechanic_schema.dump(mechanic),
            "tickets_count" : len(mechanic.tickets)
        }
        sorted_mechanics_list.append(mechanic_result_format)
    return jsonify(sorted_mechanics_list), 200
