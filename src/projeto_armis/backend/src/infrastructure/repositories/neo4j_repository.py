from datetime import datetime

import sys

from langchain_community.callbacks import get_openai_callback
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import AzureChatOpenAI

from application.dtos.entity_dto import EntityDTO
from application.dtos.relationship_dto import RelationshipDTO
from application.mappers.entity_mapper import EntityMapper
from application.mappers.relationship_mapper import RelationshipMapper
from domain.models.entity import Entity
from domain.models.relationship import Relationship
from infrastructure.adapters.neo4j_adapter import Neo4jAdapter


class Neo4jRepository: 
    
    def __init__(self, neo4j_adapter : Neo4jAdapter):
        self.neo4j_adapter = neo4j_adapter


    def run_query(self, query: str, params: dict = None):
        """
        Runs a query in the database
        :param query: query
        :param params: parameters of the query
        :return: query results
        """
        return self.neo4j_adapter.run_query(query, params or {})
    
    def query_graph(self, question: str, llm: AzureChatOpenAI, allow_dangerous_requests: bool = True, return_intermediate_steps: bool = True, validate_cypher: bool = True):
        graph = self.neo4j_adapter.db
        with get_openai_callback() as cb:

            chain = GraphCypherQAChain.from_llm(
                llm=llm,
                graph=graph,
                top_k=sys.maxsize-1,
                #verbose=True,
                allow_dangerous_requests=allow_dangerous_requests,
                return_intermediate_steps=return_intermediate_steps,
                validate_cypher=validate_cypher,
                callbacks=[cb]
            )
            response = chain.invoke({"query": question})
        return response, cb
    
    def import_nodes(self, nodes: list[EntityDTO]) -> list[EntityDTO]:
        # TODO: implementar transações
        """
        Imports a node to the database. 
        :param nodes: tuple of string (name, category, description)
        :return: [EntityDTO]
        """
        list_to_return : list[EntityDTO] = []        
        for node in nodes:
            name, category, description = node.name, node.category, node.description
            name = self._format_string(name, remove_spaces=True)
            category = self._format_string(category, remove_spaces=True)
            description = self._format_string(description)
            query_template = f"CREATE (:{category} {{name: $name, description: $description}});"
            self.run_query(query=query_template, params={"name": name, "description": description})
            list_to_return.append(node)
        return list_to_return
    
    def import_relationships(self, relationships: list[RelationshipDTO]) -> list[RelationshipDTO]:
        # TODO: implementar transações
        """
        Imports a relationship to the database. 
        :param relationships: tuple of string (origin node, target node, value)
        :return: [RelationshipDTO]
        """
        list_to_return : list[RelationshipDTO] = []
        for relationship in relationships:
            source, target, value = relationship.source, relationship.target, relationship.value
            source = self._format_string(source, remove_spaces=True)
            target = self._format_string(target, remove_spaces=True)
            value = self._format_string(value, remove_spaces=True)
            query_template = f"""
                MATCH (source {{name: $source}}), (target {{name: $target}})
                CREATE (source)-[:{value}]->(target);
                """            
            self.run_query(query_template, params={"source": source, "target": target})
            list_to_return.append(relationship)
        return list_to_return
            
    
    def get_all_nodes(self):
        """
        Returns all nodes
        :return: nodes
        """
        query_template = '''
        MATCH (m) return m
        '''
        results = self.run_query(query=query_template)
        return results
    
    def clean_db(self) -> None:
        """
        Clean Entire Database
        """
        query_template = '''
        MATCH (m) detach delete m
        '''
        self.run_query(query_template)

    def _format_string(self, string: str, remove_spaces=False):
        """
        Capitalizes the first word. If the remove_spaces parameter is set to True, joins the words and capitalizes the first letter of each word.
        :param string: String to format 
        :param remove_spaces: If True, removes spaces from the string
        :return: formated string
        """
        final = ""
        if " " in string and remove_spaces:
            temp = string.split(" ")
            for i, chunk in enumerate(temp):
                temp[i] = chunk.capitalize()
            for chunk in temp:
                final = final + chunk
        else:
            final = string.capitalize()
    
        final = ''.join(char for char in final if char.isalnum() or char == " ")
    
        return final

    def get_schema(self):
        """
        Refreshes the schema of the database and returns it.
        :return: schema
        """
        self.neo4j_adapter.db.refresh_schema()
        return self.neo4j_adapter.db.get_schema

    def get_structured_schema(self):
        """
        Refreshes the schema of the database and returns it.
        :return: schema
        """
        self.neo4j_adapter.db.refresh_schema()
        return self. neo4j_adapter.db.get_structured_schema