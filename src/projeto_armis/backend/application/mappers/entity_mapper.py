from application.dtos.entity_dto import EntityDTO
from domain.models.entity import Entity
from domain.models.schemas.entity_schema import EntitySchema


class EntityMapper:

    @staticmethod
    def to_domain(obj: EntityDTO | EntitySchema | list[EntityDTO] | list[EntitySchema]) -> list[Entity] | Entity:
        if isinstance(obj, list):
            list_to_return : list[Entity] = []
            for a in obj:
                list_to_return.append(EntityMapper.to_domain(a))
            return list_to_return
        # Caso seja um único objeto
        return Entity(
            name=obj.name,
            category=obj.category,
            description=obj.description
        )

    @staticmethod
    def to_dto(entity: Entity | list[Entity]) -> list[EntityDTO] | EntityDTO:
        if isinstance(entity, list):
            list_to_return : list[EntityDTO] = []
            for a in entity:
                list_to_return.append(EntityMapper.to_dto(a))
            return list_to_return
        # Caso seja um único objeto
        return EntityDTO(
            name=entity.name,
            category=entity.category,
            description=entity.description
        )
