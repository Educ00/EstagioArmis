from pydantic import BaseModel, Field


class RelationshipSchema(BaseModel):
    source: str = Field(..., description="Entidade de origem")
    target: str = Field(..., description="Entidade de destino")
    value: str = Field(..., description="Rótulo/valor da relação")