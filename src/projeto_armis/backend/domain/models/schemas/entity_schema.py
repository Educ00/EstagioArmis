from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    name: str = Field(..., description="None da Entidade")
    category : str = Field(..., description="Categoria da Entidade")
    description : str = Field(..., description="Descrição da Entidadde")    