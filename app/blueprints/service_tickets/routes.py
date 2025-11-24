from .schemas import service_ticket_schema, service_tickets_schema
from app.blueprints.service_tickets import service_tickets_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Service_tickets, db, Customers, Mechanics
from app.blueprints.mechanics.schemas import mechanics_schema
from app.utils.auth import token_required
from sqlalchemy import select
from app.extensions import limiter

@service_tickets_bp.route('', methods=["POST"])
@limiter.limit("3 per hour")
@token_required
def create_service_ticket():
    user_role = request.user_role
    if user_role == "customer":
        customer_id = request.user_id
        customer = db.session.get(Customers, customer_id)
        if not customer:
            return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
        try:
            data = service_ticket_schema.load(request.json)
        except ValidationError as e:
            return jsonify({"error message" : e.messages}), 400
        print(data)

        new_service_ticket = Service_tickets(**data,customer=customer)
        db.session.add(new_service_ticket)
        customer.service_tickets.append(new_service_ticket)
        db.session.commit()
        return service_ticket_schema.jsonify(new_service_ticket), 201
    else:
        return jsonify({"message" : f"{user_role} is not allowed."})

@service_tickets_bp.route('', methods=["GET"])
def read_service_tickets():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Service_tickets)
        service_tickets = db.paginate(query,page=page, per_page=per_page) #Handles our pagination so we don't have to be worry about pagination with hard code
        return service_tickets_schema.jsonify(service_tickets), 200
    except:
        service_tickets = db.session.query(Service_tickets).all()
        return service_tickets_schema.jsonify(service_tickets), 200

@service_tickets_bp.route('/<int:service_ticket_id>', methods=["GET"])
def read_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    return service_ticket_schema.jsonify(service_ticket), 200

@service_tickets_bp.route('/<int:service_ticket_id>', methods=["DELETE"])
def delete_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted service_ticket with id: {service_ticket_id}"}), 200

@service_tickets_bp.route('/<int:service_ticket_id>', methods=["PUT"])
def update_service_ticket(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    for key, value in service_ticket_data.items():
        setattr(service_ticket, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully service_ticket with id: {service_ticket_id} updated."}), 200

@service_tickets_bp.route('/mechanics/<int:service_ticket_id>', methods=["GET"])
def read_service_ticket_mechanics(service_ticket_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    return mechanics_schema.jsonify(service_ticket.mechanics)
    

@service_tickets_bp.route('/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>', methods=["PUT"])
def add_mechanic_to_service_ticket(service_ticket_id,mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics,mechanic_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    if not mechanic:
       return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)
        mechanic.tickets.append(service_ticket)
        db.session.commit()
        return jsonify({"message" : f"Successfully mechanic with id: {mechanic_id} added to service_ticket with id:{service_ticket_id}."}), 200
    else:
        return jsonify({"message" : f"{mechanic.last_name} is already added in service_ticket with id:{service_ticket_id}."}),200


@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=["PUT"])
def remove_mechanic_from_service_ticket(service_ticket_id,mechanic_id):
    service_ticket = db.session.get(Service_tickets, service_ticket_id)
    mechanic = db.session.get(Mechanics,mechanic_id)
    if not service_ticket:
        return jsonify({"error" : f"Service_ticket with id: {service_ticket_id} not found."}), 404
    if not mechanic:
       return jsonify({"error" : f"Mechanic with id: {mechanic_id} not found."}), 404
    if mechanic in service_ticket.mechanics:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({"message" : f"Successfully mechanic with id: {mechanic_id} removed from service_ticket with id:{service_ticket_id}."}), 200
    else:
        return jsonify({"message" : f"{mechanic.last_name} is not in service_ticket with id: {service_ticket.id}"}),200
