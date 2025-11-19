from app.models import Customers
from app.extensions import ma


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_login_schema = CustomerSchema(exclude=['first_name','last_name', 'phone', 'address'])