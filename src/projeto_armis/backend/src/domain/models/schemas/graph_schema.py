from typing import List

from pydantic import BaseModel, Field

from domain.models.schemas.entity_schema import EntitySchema
from domain.models.schemas.relationship_schema import RelationshipSchema


class GraphSchema(BaseModel):
    entities: List[EntitySchema] = Field(
        default_factory=list,
        description="Lista de todas as entidades extraídas"
    )

    relations: List[RelationshipSchema] = Field(
        default_factory=list,
        description="Lista de todas as relações extraídas"
    )