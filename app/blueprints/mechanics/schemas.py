from app.models import Mechanics
from app.extensions import ma


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicSchema(exclude=["first_name", "last_name", "phone", "address", "salary"])