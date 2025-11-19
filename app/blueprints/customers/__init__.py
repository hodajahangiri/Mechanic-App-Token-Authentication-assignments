from flask import Blueprint

customers_bp = Blueprint('customers_bp', __name__)

# It has to be here after creating blueprint
from . import routes