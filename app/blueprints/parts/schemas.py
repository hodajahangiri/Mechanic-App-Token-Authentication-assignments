from app.models import Parts, PartDescriptions
from app.extensions import ma


class PartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parts
        include_fk = True

part_schema = PartSchema()
parts_schema = PartSchema(many=True)
