from app.models import Parts, PartDescriptions
from app.extensions import ma


class PartDescriptionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PartDescriptions
        include_fk = True

part_description_schema = PartDescriptionSchema()
part_descriptions_schema = PartDescriptionSchema(many=True)