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
    
    new_description = PartDescriptions(**data)
    db.session.add(new_description)
    db.session.commit()
    return part_description_schema.jsonify(new_description), 201





