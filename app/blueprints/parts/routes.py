from . import parts_bp
from .schemas import part_schema, parts_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, Parts



@parts_bp.route('', methods=['POST'])
def create_part():
    try:
        data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    quantity = request.args.get('gty', 1, type=int)
    count = 0
    base_serial = data["serial_number"]
    new_serial = base_serial
    serial = 1 
    while count < quantity:
        while check_existing_serial_number(new_serial):
            new_serial = base_serial + "-" + str(serial)
            serial += 1
        data['serial_number'] = new_serial
        new_part = Parts(**data)
        db.session.add(new_part)
        count += 1
    db.session.commit()
    return jsonify(f"Successfully created {quantity} part(s) with description id: {data["desc_id"]}(s)."), 200


def check_existing_serial_number(serial_number):
    existing_part = db.session.query(Parts).where(Parts.serial_number==serial_number).first()
    if existing_part:
        return True
    return False

@parts_bp.route('', methods=['GET'])
def get_all_parts():
    parts = db.session.query(Parts).all()
    response = []
    for part in parts:
        response_format = {
            "part": part_schema.dump(part),
            "part_name" : part.part_description.name,
            "part_price" : part.part_description.price
        }
        response.append(response_format)
    return jsonify(response), 200

@parts_bp.route('/<int:part_id>', methods=['GET'])
def get_specific_part(part_id):
    part = db.session.get(Parts,part_id)
    if part:
        return part_schema.jsonify(part), 200
    return jsonify({"message" : f"part with part_id : {part_id} not found"})

@parts_bp.route('/<int:part_id>',methods=['PUT'])
def update_part(part_id):
    part_to_update = db.session.get(Parts,part_id)
    if not part_to_update:
        return jsonify({"message" : f"Part with id: {part_id} not found"}), 404
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    # Check to avoid duplicate serial number
    exist_serial_number = db.session.query(Parts).where(Parts.serial_number==part_data["serial_number"], Parts.id != part_to_update.id).first()
    if exist_serial_number:
        return jsonify({"message" : f"This serial number: {part_data["serial_number"]} belongs to another product, you can not choose it,"}), 400
    
    for key, value in part_data.items():
        setattr(part_to_update, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully part with id: {part_id} updated."}), 200











