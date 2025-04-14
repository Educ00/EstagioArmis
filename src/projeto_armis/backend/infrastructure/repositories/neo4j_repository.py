from application.dtos.entity_dto import EntityDTO
from application.dtos.relationship_dto import RelationshipDTO
from application.mappers.entity_mapper import EntityMapper
from application.mappers.relationship_mapper import RelationshipMapper
from domain.models.entity import Entity
from domain.models.relationship import Relationship
from infrastructure.repositories.base_repository import BaseRepository


class Neo4jRepository(BaseRepository):
    
    def import_nodes(self, nodes: list[Entity]) -> list[EntityDTO]:
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
            list_to_return.append(EntityMapper.to_dto(node))
        return list_to_return
    
    def import_relationships(self, relationships: list[Relationship]) -> list[RelationshipDTO]:
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
            print(f"source: {source}, target: {target}, value: {value}")
            
            self.run_query(query_template, params={"source": source, "target": target})
            list_to_return.append(RelationshipMapper.to_dto(relationship))
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
        self.adapter.db.refresh_schema()
        return self.adapter.db.get_schema