from flask import Blueprint

service_tickets_bp = Blueprint('service_tickets_bp', __name__)

# It has to be here after creating blueprint
from . import routes
