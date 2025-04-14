from application.dtos.relationship_dto import RelationshipDTO
from domain.models.relationship import Relationship


class RelationshipMapper:
    
    @staticmethod
    def to_domain(dto: RelationshipDTO): 
        return Relationship(
            source=dto.source,
            target=dto.target,
            value=dto.value
        )
    
    
    @staticmethod
    def to_dto(relationship: Relationship):
       return RelationshipDTO(
           source=relationship.source,
           target=relationship.target,
           value=relationship.value
       )