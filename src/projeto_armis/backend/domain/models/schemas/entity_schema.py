from typing import Literal

from pydantic import BaseModel, Field

class EntitySchema(BaseModel):
    name: str = Field(..., description="None da Entidade")
    # https://learn.microsoft.com/en-us/ai-builder/prebuilt-entity-extraction dia 30/04/2025 17:17
    category : Literal[
        "Seres Vivos", "Objetos", "Lugares e Espaços", "Eventos e Processos", "Organizações e Instituições",
        "Conceitos e Ideias", "Propriedades e Qualidades", "Tempo e Quantidades"
    ] = Field(..., description="Categoria da Entidade")
    description : str = Field(..., description="Descrição da Entidadde")    