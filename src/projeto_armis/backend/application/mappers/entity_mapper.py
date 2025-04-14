from application.dtos.entity_dto import EntityDTO
from domain.models.entity import Entity


class EntityMapper:

    @staticmethod
    def to_entity(dto: EntityDTO):
        return Entity(
            name=dto.name,
            category=dto.category,
            description=dto.description
        )
    
    @staticmethod
    def to_entities(dtos: list[EntityDTO]):
        list_to_return : list[Entity] = []
        for dto in dtos:
            list_to_return.append(EntityMapper.to_entity(dto))
        return list_to_return

    @staticmethod
    def to_dto(entity: Entity):
        return EntityDTO(
            name=entity.name,
            category=entity.category,
            description=entity.description
        )
    
    @staticmethod
    def to_dtos(entities: list[Entity]):
        list_to_return : list[EntityDTO] = []
        for entity in entities:
            list_to_return.append(EntityMapper.to_dto(entity))
        return list_to_return
