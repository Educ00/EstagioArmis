import os
import json
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_neo4j import Neo4jGraph

from langchain_openai import AzureChatOpenAI
from neo4j.exceptions import CypherSyntaxError

modeloGpt4o = "GPT-4o"
modeloGpt4omini = "GPT-4o-mini"

MAX_CORRECTION_ATTEMPTS = 5


json_schema1 = {
    "title": "LLMResponseSchema",
    "description": "Schema to define the LLM response format.",
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The response generated by the LLM"
        }
    },
    "required": ["response"]
}

template = '''
        <instructions>{instructions}</instructions>
        <schema>{schema}</schema>
        <question>{question}</question>
    '''

instructions1 = """
    Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.
    Instructions:
    Use only the provided relationship types and properties.
    Do not use any other relationship types or properties that are not provided.
    Do not respond with any context, only the query.
    """

template_only_instructions = """
        <instructions>{instructions}</instructions>
    """

instructions_generate_invalid_query = """
    Task: Generate a random Cypher a query with some syntax errors so I can train my bot how to correct it.
    Do not respond with any context, only the query.
    """

instructions_correct_syntax = """
    Task: The syntax of the Cypher query is wrong. Correct it.
    Follow the provided schema to correct the query.
    Do not use any other relationship types or properties that are not provided. 
    Do not respond with any context, only the query.
    """


def initialize_neo4j(url: str, username: str, password: str):
    return Neo4jGraph(url=url, username=username, password=password)

def initialize_azureOpenAI_llm(model_deployment_name: str, azure_endpoint: str, openai_api_key: str,
                               openai_api_type: str, openai_api_version: str = "2024-02-01", output_schema: json = None):
    llm = AzureChatOpenAI(
        openai_api_version=openai_api_version,
        deployment_name=model_deployment_name,
        azure_endpoint=azure_endpoint,
        openai_api_key=openai_api_key,
        openai_api_type=openai_api_type,
    )

    if output_schema:
        llm = llm.with_structured_output(output_schema)

    return llm

def run_query(graph: Neo4jGraph, query: str, query_params: {} = None):
    print("A chamar base de dados")
    if query_params:
        return graph.query(query, query_params)
    else:
        return graph.query(query)
        


def call_llm(llm: AzureChatOpenAI, prompt_template: str, **kwargs):
    print("A chamar LLM")
    prompt_template = PromptTemplate.from_template(prompt_template)
    prompt = prompt_template.format(**kwargs)
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    return response


def main():
    graph = initialize_neo4j(url=os.getenv("NEO4J_URI"), username=os.getenv("NEO4J_USERNAME"), password=os.getenv("NEO4J_PASSWORD"))
    graph_schema = graph.get_schema

    llm = initialize_azureOpenAI_llm(
        model_deployment_name=modeloGpt4omini,
        azure_endpoint=os.getenv("ModelsEndpoint"),
        openai_api_key=os.getenv("ModelsKey"),
        openai_api_type="azure",
        #gopenai_api_version="2024-02-01",
        openai_api_version="2024-10-21",
        output_schema=json_schema1
    )
    
    question1 = "Quem é a personagem, o que faz e para onde quer ir?"
    print("A converter pergunta: \"", question1, "\"")
    
    llm_response = call_llm(llm, template, instructions=instructions1, schema=graph_schema, question=question1)
    
    # Para testar uma query sintaticamente errada
    #llm_response = call_llm(llm, template_only_instructions, instructions=instructions_generate_invalid_query)
    
    print("Resposta LLM: ", llm_response)
    graph_response = ""
    try:
        graph_response = run_query(graph, llm_response["query"])
    except CypherSyntaxError:
        print("Sintaxe errada.")
        correction_attempt = 0
        while correction_attempt <= MAX_CORRECTION_ATTEMPTS:
            print(f"Tentativa de correção #{correction_attempt+1}/{MAX_CORRECTION_ATTEMPTS}")
            correction_attempt += 1
            llm_response = call_llm(llm, template, instructions=instructions_correct_syntax, schema=graph_schema, question=question1)
            try:
                graph_response = graph.query(llm_response["query"])
                break
            except CypherSyntaxError:
                print("Resposta errada de novo: " + llm_response["query"])
        if correction_attempt == MAX_CORRECTION_ATTEMPTS:
            graph_response = "Não foi possivel consultar a base de dados porque a query era inválida!"
    print("Query: ", llm_response["query"])
    print("Consulta do Grafo: ", graph_response)

    


if __name__ == '__main__':
    load_dotenv()
    main()