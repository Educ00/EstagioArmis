import json
import os

from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
import datetime

# Entidades:
#   campos: name, category, description

# Relationships:
#   campos: source, target, value

load_dotenv()


def teste():
    graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"),
                       password=os.getenv("NEO4J_PASSWORD"))

    nodes = ["node1", "node2", "node3", "node4", "node5", "node6"]

    create_teste_node = '''
        CREATE (:Entidade {nome: $name});
    '''

    results = []
    for node in nodes:
        results.append(graph.query(create_teste_node, params={"name": node}))

    return results


def return_all_nodes():
    graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"),
                       password=os.getenv("NEO4J_PASSWORD"))
    query_template = '''
        MATCH (m) return m
    '''
    result = graph.query(query_template)
    return result


def return_all_nodes_and_relations():
    graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"),
                       password=os.getenv("NEO4J_PASSWORD"))
    query_template = '''
        MATCH (m)-[r]-(n) return m, r, n
    '''
    result = graph.query(query_template)
    return result


def delete_all_nodes():
    graph = Neo4jGraph(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"),
                       password=os.getenv("NEO4J_PASSWORD"))
    query_template = '''
        MATCH (m) detach delete m
    '''
    result = graph.query(query_template)
    return result


def format_string(string: str, remove_spaces=False):
    final = ""
    if " " in string and remove_spaces:
        temp = string.split(" ")
        for i, chunk in enumerate(temp):
            temp[i] = chunk.capitalize()
        for chunk in temp:
            final = final + chunk
    else:
        final = string.capitalize()

    return final


def import_nodes(nodes: [(str, str, str)]):
    db_uri = os.getenv("NEO4J_URI")
    db_username = os.getenv("NEO4J_USERNAME")
    db_password = os.getenv("NEO4J_PASSWORD")

    graph = Neo4jGraph(db_uri, username=db_username, password=db_password)

    for i, node in enumerate(nodes):
        print(f"   A guardar node #{i + 1}/{len(nodes)}...")
        name, category, description = node
        name = format_string(name, remove_spaces=True)
        category = format_string(category, remove_spaces=True)
        description = format_string(description)
        query_template = f"CREATE (:{category} {{name: $name, description: $description}});"
        graph.query(query_template, params={"name": name, "description": description})
        print("   Sucesso!")


def import_relationships(relationships: [(str, str, str)]):
    db_uri = os.getenv("NEO4J_URI")
    db_username = os.getenv("NEO4J_USERNAME")
    db_password = os.getenv("NEO4J_PASSWORD")

    graph = Neo4jGraph(db_uri, username=db_username, password=db_password)

    for i, relationship in enumerate(relationships):
        print(f"   A guardar relação #{i + 1}/{len(relationships)}")
        source, target, value = relationship
        source = format_string(source)
        target = format_string(target)
        value = format_string(value, remove_spaces=True)

        query_template = f"""
            MATCH (source {{name: $source}}), (target {{name: $target}})
            CREATE (source)-[:{value}]->(target);
            """

        graph.query(query_template, params={"source": source, "target": target})


def main():
    dir = "./ficheiros/output"
    ficheiro = "respostas1.txt"
    path = dir + "/" + ficheiro

    with open(path, "r") as json_data:
        data = json.load(json_data)

    nodes = []
    for entity in data["entities"]:
        nodes.append((entity["name"], entity["category"], entity["description"]))

    relationships = []
    for relationship in data["relationships"]:
        relationships.append(
            (relationship["source"], relationship["target"], relationship["value"]))

    print("A importar nodes...")
    import_nodes(nodes)
    print("Nodes importados!")

    print("A importar relações...")
    import_relationships(relationships)
    print("Relações importadas!")
    
    print("Grafo: ")
    grafo = return_all_nodes_and_relations()
    for coisa in grafo:
        print(coisa)


if __name__ == "__main__":
    main()
