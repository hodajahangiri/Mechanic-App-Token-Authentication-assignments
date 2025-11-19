from app.blueprints.customers import customers_bp
from app.models import Customers, db, Service_tickets
from .schemas import customer_schema, customers_schema, customer_login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import service_tickets_schema
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth import encode_token, token_required

#LOGIN ROUTE
@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        credential_data = customer_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    customer = db.session.query(Customers).where(Customers.email == credential_data["email"]).first()
    if customer and check_password_hash(customer.password, credential_data["password"]):
        customer_token = encode_token(customer.id, role="customer")
        response = {
            "message" : f"Successfully logged in. Welcome {customer.first_name}",
            "token" : customer_token
        }
        return jsonify(response)
    else:
        return jsonify({"error message" : "Invalid email or password."}), 400

@customers_bp.route('', methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    # Check if email exist or not because email is unique attribute
    exist_customer = db.session.query(Customers).where(Customers.email == data["email"]).first()
    if exist_customer:
        return jsonify({"error" : f"{data["email"]} is already associated with an account."}), 400
    data["password"] = generate_password_hash(data["password"])
    new_customer = Customers(**data)
    db.session.add(new_customer)
    db.session.commit()
    new_customer_token = encode_token(new_customer.id, role="customer")
    response = {"customer_data" : data,
                "token" : new_customer_token}
    return jsonify(response), 201

@customers_bp.route('', methods=["GET"])
def read_customers():
    customers = db.session.query(Customers).all()
    return customers_schema.jsonify(customers), 200

@customers_bp.route('/profile', methods=["GET"])
@token_required
def read_customer():
    user_role = request.user_role
    if user_role == "customer":
        customer_id = request.user_id
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
        return customer_schema.jsonify(customer), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."})

@customers_bp.route('', methods=["DELETE"])
@token_required
def delete_customer():
    user_role = request.user_role
    if user_role == "customer":
        customer_id = request.user_id
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
        if len(customer.service_tickets)>0:
            # Delete All service tickets for a specific user
            db.session.query(Service_tickets).where(Service_tickets.customer_id == customer.id).delete()
            db.session.commit()
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message" : f"Successfully deleted customer with id: {customer_id}"}), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."})
    
@customers_bp.route('', methods=["PUT"])
@token_required
def update_customer():
    user_role = request.user_role
    if user_role == "customer":
        customer_id = request.user_id
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
        try:
            customer_data = customer_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error message" : e.messages}), 400
        # Check the email customer wants to update not be taken with another customer
        existing_email = db.session.query(Customers).where(Customers.email == customer_data["email"], Customers.id != customer_id).first()
        if existing_email:
            return jsonify({"error" : f"{customer_data["email"]} is already taken with another customer."}), 400
        customer_data["password"] = generate_password_hash(customer_data["password"])
        for key, value in customer_data.items():
            setattr(customer, key, value)
        db.session.commit()
        return jsonify({"message" : f"Successfully customer with id: {customer_id} updated."}), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."})
    
@customers_bp.route('/service_tickets', methods=["GET"])
@token_required
def read_customer_service_tickets():
    user_role = request.user_role
    if user_role == "customer":
        customer_id = request.user_id
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
        return service_tickets_schema.jsonify(customer.service_tickets), 200
    else:
        return jsonify({"message" : f"{user_role} is not allowed."})
