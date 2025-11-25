from flask import Blueprint

part_descriptions_bp = Blueprint("part_descriptions_bp", __name__)

# It has to be here after creating blueprint
from . import routes
