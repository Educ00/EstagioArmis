from difflib import SequenceMatcher
from domain.models.schemas.graph_schema import GraphSchema
from domain.models.schemas.entity_schema import EntitySchema
from domain.models.schemas.relationship_schema import RelationshipSchema
from langchain_core.prompts import ChatPromptTemplate
from typing import List


class GraphAgent:
    def __init__(self, llm):
        self.llm = llm
        self.known_entities: List[EntitySchema] = []
        self.known_relations: List[RelationshipSchema] = []

    def _is_similar_entity(self, e1: EntitySchema, e2: EntitySchema, threshold: float = 0.8) -> bool:
        same_category = e1.category.lower().strip() == e2.category.lower().strip()
        similar_name = SequenceMatcher(None, e1.name.lower().strip(), e2.name.lower().strip()).ratio() >= threshold
        return same_category and similar_name

    def _entity_exists(self, new_entity: EntitySchema) -> bool:
        #return any(self._is_similar_entity(new_entity, existing) for existing in self.known_entities)
        return any(
            new_entity.name == e.name and
            new_entity.description == e.category and
            new_entity.category == e.category
            for e in self.known_entities
        )

    def _relation_exists(self, new_relation: RelationshipSchema) -> bool:
        return any(
            new_relation.source == r.source and
            new_relation.target == r.target and
            new_relation.value == r.value
            for r in self.known_relations
        )

    def extract_from_chunk(self, chunk: str) -> GraphSchema:
        # Fase 1: Extração de entidades
        entity_prompt = ChatPromptTemplate.from_messages([
            ("system", "Extrai todas as **entidades** do texto fornecido"),
            ("human", "{text}")
        ])
        print("Entities")
        structured_llm_entities = self.llm.with_structured_output(schema=GraphSchema)
        entity_messages = entity_prompt.invoke({"text": chunk})
        entity_output: GraphSchema = structured_llm_entities.invoke(entity_messages)

        new_entities = []
        for e in entity_output.entities:
            if not self._entity_exists(e):
                self.known_entities.append(e)
                new_entities.append(e)

        # Fase 2: Extração de relações (usando o contexto atual de entidades)
        entities_context = "\n".join([f"{e.name} ({e.category})" for e in self.known_entities])
        relation_prompt = ChatPromptTemplate.from_messages([
            ("system", "Com base nas seguintes entidades:\n\n"
                       f"{entities_context}\n\n"
                       "Extrai todas as **relações** entre estas entidades no texto fornecido, implícitas e explicitas. Ignora novas entidades."),
            ("human", "{text}")
        ])
        print("Relationships")
        structured_llm_relations = self.llm.with_structured_output(schema=GraphSchema)
        relation_messages = relation_prompt.invoke({"text": chunk})
        relation_output: GraphSchema = structured_llm_relations.invoke(relation_messages)

        new_relations = []
        for r in relation_output.relations:
            if not self._relation_exists(r):
                self.known_relations.append(r)
                new_relations.append(r)

        # Retorna apenas o que foi novo neste chunk
        return GraphSchema(entities=new_entities, relations=new_relations)
