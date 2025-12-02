from . import part_descriptions_bp
from .schemas import part_description_schema, part_descriptions_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import db, PartDescriptions


@part_descriptions_bp.route('', methods=['POST'])
def create_part_description():
    try:
        data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    # Avoid to create duplicate description
    description = db.session.query(PartDescriptions).where(PartDescriptions.name==data["name"],PartDescriptions.price==data["price"], PartDescriptions.made_in==data["made_in"]).first()
    if description:
        return jsonify({"message" : "These description is already exist, you can not add same description."}),400
    new_description = PartDescriptions(**data)
    db.session.add(new_description)
    db.session.commit()
    return part_description_schema.jsonify(new_description), 201


@part_descriptions_bp.route('', methods=['GET'])
def get_all_part_descriptions():
    part_descriptions = db.session.query(PartDescriptions).all()
    if len(part_descriptions)==0:
        return jsonify({"message" : "There is no part description to show."}), 200
    return part_descriptions_schema.jsonify(part_descriptions), 200

@part_descriptions_bp.route('/search_by_name', methods=['GET'])
def get_all_descriptions_by_name():
    name = request.args.get("name")
    if name is None:
        return jsonify({"message" : "You have to send the name of part that you want to search."}), 200
    part_descriptions = db.session.query(PartDescriptions).where(PartDescriptions.name.ilike(f"%{name}%")).all()
    if len(part_descriptions)==0:
        return jsonify({"message" : "There is no part description to show."}), 200
    return part_descriptions_schema.jsonify(part_descriptions), 200

@part_descriptions_bp.route('/<int:part_description_id>',methods=['PUT'])
def update_part_description(part_description_id):
    part_description = db.session.get(PartDescriptions,part_description_id)
    if not part_description:
        return jsonify({"message" : f"Description with id: {part_description_id} not found"}), 404
    try:
        description_data = part_description_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    
    for key, value in description_data.items():
        setattr(part_description, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully description with id: {part_description_id} updated."}), 200

@part_descriptions_bp.route('/<int:part_description_id>', methods=['DELETE'])
def delete_part_description(part_description_id):
    part_description_to_delete = db.session.get(PartDescriptions,part_description_id)
    if not part_description_to_delete:
        return jsonify({"message" : f"Description with id: {part_description_id} not found"}), 404
    if len(part_description_to_delete.parts)>0:
        return jsonify({"message" : f"Some parts has relationship with this description, you can not delete it."}), 200
    db.session.delete(part_description_to_delete)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted description with id: {part_description_id}"}), 200


