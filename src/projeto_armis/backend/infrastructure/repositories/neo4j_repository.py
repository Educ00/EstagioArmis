from infrastructure.repositories.base_repository import BaseRepository


class Neo4jRepository(BaseRepository):
    
    def import_nodes(self, nodes: (str, str, str)) -> int:
        """
        Imports a node to the database. 
        :param nodes: tuple of string (name, category, description)
        :return: number of relationships
        """
        i = 0
        for node in nodes:
            name, category, description = node
            name = self._format_string(name, remove_spaces=True)
            category = self._format_string(category, remove_spaces=True)
            description = self._format_string(description)
            query_template = f"CREATE (:{category} {{name: $name, description: $description}});"
            self.run_query(query=query_template, params={"name": name, "description": description})
            i += 1
        return i
    
    def import_relationships(self, relationships: (str, str, str)) -> int:
        """
        Imports a relationship to the database. 
        :param relationships: tuple of string (origin node, target node, value)
        :return: number of relationships
        """
        i = 0
        for relationship in relationships:
            source, target, value = relationship
            source = self._format_string(source, remove_spaces=True)
            target = self._format_string(target, remove_spaces=True)
            value = self._format_string(value, remove_spaces=True)
    
            query_template = f"""
                MATCH (source {{name: $source}}), (target {{name: $target}})
                CREATE (source)-[:{value}]->(target);
                """
            print(f"source: {source}, target: {target}, value: {value}")
            self.run_query(query_template, params={"source": source, "target": target})
            i += 1
        return i
            
    
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