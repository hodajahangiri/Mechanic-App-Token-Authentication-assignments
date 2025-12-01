from flask import Flask
from .extensions import ma, limiter, cache 
from .models import db
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp
from .blueprints.service_tickets import service_tickets_bp
from .blueprints.parts import parts_bp
from .blueprints.part_descriptions import part_descriptions_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

#creating swagger blueprint
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL,API_URL, config={'app_name': 'Mechanic Shop'})

def create_app(config_name):
    # Initialize my flask app
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # Register Blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(parts_bp, url_prefix='/parts')
    app.register_blueprint(part_descriptions_bp, url_prefix='/part_descriptions')
    app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)


    return app