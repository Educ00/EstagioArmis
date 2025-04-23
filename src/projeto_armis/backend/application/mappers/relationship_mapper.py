from application.dtos.relationship_dto import RelationshipDTO
from domain.models.relationship import Relationship
from domain.models.schemas.relationship_schema import RelationshipSchema


class RelationshipMapper:
    
    @staticmethod
    def to_domain(obj: RelationshipDTO | RelationshipSchema | list[RelationshipDTO] | list[RelationshipSchema]) -> list[Relationship] | Relationship:
        if isinstance(obj, list):
            list_to_return : list[Relationship] = []
            for a in obj:
                list_to_return.append(RelationshipMapper.to_domain(a))
            return list_to_return
        return Relationship(
            source=obj.source,
            target=obj.target,
            value=obj.value
        )
    
    
    @staticmethod
    def to_dto(obj: Relationship | list[Relationship]) -> list[RelationshipDTO] | RelationshipDTO:
        if isinstance(obj, list):
            list_to_return : list[RelationshipDTO] = []
            for a in obj:
                list_to_return.append(RelationshipMapper.to_dto(a))
            return list_to_return
        return RelationshipDTO(
            source=obj.source,
            target=obj.target,
            value=obj.value
        )