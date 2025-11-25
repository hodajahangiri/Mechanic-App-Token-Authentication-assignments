from flask import Blueprint

parts_bp = Blueprint("parts_bp", __name__)

# It has to be here after creating blueprint
from . import routes
