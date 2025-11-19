from flask import Blueprint

mechanics_bp = Blueprint('mechanics_bp', __name__)

# It has to be here after creating blueprint
from . import routes