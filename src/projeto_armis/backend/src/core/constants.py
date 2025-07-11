UPLOAD_FOLDER = "uploads"

modeloAda = "text-embedding-ada-002"
modeloGpt4o = "GPT-4o"
modeloGpt4omini = "GPT-4o-mini"
openaiApiVersion = "2024-10-21"
openAiApiType = "azure"

prompt_template0 = """
<instructions>{instructions}</instructions>
"""

prompt_template1 = '''
<instructions>{instructions}</instructions>
<text>{text}</text>
'''

prompt_template2 = '''
<instructions>{instructions}</instructions>
<schema>{schema}</schema>
<question>{question}</question>
'''

prompt_template3 = """
<instructions>{instructions}</instructions>
<question>{question}</question>
<answer>{answer}</answer>
"""

prompt_instructions1 = '''
List all entities and relationships you find, ensuring each is clearly defined, contextualized, and strictly based on the text.

Some key points to follow while identifying additional entities and relationships are:
- Entities must be meaningful, and it should be specific object or concept, avoid ambiguous entities.
  1. Specificity: Entity names must be specific and indicative of their nature.
  2. Diversity: Entities should be identified at multiple levels of detail, from general overviews to specific functionalities.
  3. Uniqueness: Similar entities should be consolidated to avoid redundancy, with each entity distinctly represented.

- Metadata must directly relate to and describe their respective entities.
  1. Accuracy: All metadata should be factual, verifiable from the text, and not based on external assumptions.
  2. Structure: Metadata should be organized in a comprehensive JSON tree, with the first field labeled "topic", facilitating structured data integration and retrieval.

- Relationships:
  1. Entities must be in entities list, don't use non-existing entities.
  2. Carefully examine the text to identify all relationships between clearly-related entities, ensuring each relationship is correctly captured with accurate details about the interactions.
  3. Clearly define the relationships, ensuring accurate directionality that reflects the logical or functional dependencies among entities. 
     This means identifying which entity is the source, which is the target, and what the nature of their relationship is (e.g., $source_entity depends on $target_entity for $relationship).
  4. Extract as many relationships as possible.

- Please endeavor to extract all meaningful entities and relationships from the text, avoid subsequent additional gleanings.
- Maintain language consistency in the terminology used to describe these entities and relationships, except it is necessary to preserve the original meaning.

Your task is to ensure that all extracted entities and their relationships are factual and verifiable directly from the text itself, without relying on external knowledge or assumptions.
'''

prompt_instructions2 = '''
You are a very smart studint that loves to analyse texts.
Extract all entities and relationships from the chunk of the text, following these guidelines:

ENTITIES:
- Specific and non-ambiguous
- The metadata must have the "name", the "category" and the "description" as fields.
- All information must be directly from the text or context.

RELATIONSHIPS:
- Only connect entities in your entities list
- Specify directionality (source_entity → target_entity via relationship)
- Capture all direct connections  
- Capture all implicit connections.

REQUIREMENTS:
- Maintain consistent terminology
- Base all extractions strictly on text content or context, not external knowledge
- Be aware of duplicates.
- Produce a clean JSON.
- Merge the results from the for the final answer.
'''

prompt_instructions3 = """
Your job is to create a complete knowledge graph with entities and relationships from the text.
All the details about the text should be represented in the database!
Also follow the following guidelines:

ENTITIES:
- Include name, category, description
- Be comprehensive - extract everything
- No duplicates
- May be objects, places, people,etc...

RELATIONSHIPS:
- Connect entities with source → relationship → target
- Include explicit AND implicit connections
- Include supporting context

IMPORTANT:
- Before Answering think about the task.
- Do not try to be smart -> don't group possible entities -> create separate entities.
- All Entities and relationships must be written in the language of the text.
"""

prompt_instructions4 = """
O teu trabalho é extrair um grafo de conhecimento COMPLETO e RICO em detalhes a partir de qualquer texto de entrada. Deves representar no grafo todos os pormenores, explícitos e implícitos, sem omissões e maximizando o número de entidades e relações.

1) DEFINIÇÕES CLARAS

— Entidade: qualquer elemento conceitual, concreto ou abstrato, mencionado ou inferível no texto. Inclui, mas não se limita a:
    • Pessoas (e.g., "Maria Oliveira")
    • Organizações (e.g., "Universidade de Lisboa")
    • Locais (e.g., "Praça do Comércio")
    • Objetos (e.g., "Laptop")
    • Eventos (e.g., "Conferência Anual de IA 2024")
    • Conceitos (e.g., "Inteligência Artificial")
    • Datas e períodos (e.g., "21 de abril de 2025")
    • Valores (e.g., "100€")
  
— Relação: conexão ou associação entre duas entidades, seja explicitamente escrita ou implicitamente inferida. Inclui:
    • Relações diretas (verbos, preposições: "trabalha em", "localizado em")
    • Relações descritivas ("é parte de", "é tipo de")
    • Relações contextuais e hierárquicas ("durante", "antes de", "causado por")
    • Inferências lógicas (e.g., se A compra B, inferir que B é produto de A)

2) ORIENTAÇÕES PARA MAXIMIZAÇÃO

— Extrai todas as entidades, mesmo variações (e.g., "iPhone", "o smartphone").
— Evita fusões intempestivas: trata termos distintos como entidades separadas.
— Identifica todas as relações possíveis: explícitas (verbos, preposições) e implícitas (inferências lógicas e contextuais).
— Prefere dividir relações compostas em várias ligações atômicas (cada verbo/preposição gera uma relação).
— Se uma frase listar várias entidades com mesma relação, gera múltiplas entradas.

3) BOAS PRÁTICAS

— Antes de responder, pensa em todas as possíveis entidades e relações.
— Garante que não existam duplicados em "entities".
"""

instructions_generate_cypher_query = """
Task: Generate Cypher queries to query a Neo4j graph database based on the provided schema definition. Care about the context of the question.
Instructions:
Before Answering think about the task.
Do not use any other entities, relationship types or properties that are not provided.
Do not respond with any context, only the query.
"""

instructions_correct_syntax = """
    Task: The syntax of the Cypher query is wrong. Correct it.
    Before Answering think about the task.
    Follow the provided schema to correct the query.
    Do not use any other relationship types or properties that are not provided. 
    Do not respond with any context, only the query.
    """

instructions_format_answer_to_question = """
Task: Format to a nice phrase the answer provided.
Instructions:
-  Before Answering think about the task.
- Provide only the phrase.
- You can use the answer to create a well-structured and polished response.
- Focus on making it sound natural and clear.
"""

instructions_group_results = """
Task: Format the given text following the instructions:
Instructions:
- Ensure everything is in the same language. If you need to, translate.
- Before Answering think about the task.
- Combine the provided JSON lists into a single clean JSON.
- Place all entities in the 'entities' list and all relationships in the 'relationships' list.
- Remove duplicates from both lists based on the following rules:
  - Entities with the same `name` (case-insensitive) and similar `description` or `category` are considered duplicates. For example, "árvores" and "Árvores" are the same entity.
  - Entities with the same name (ignoring capitalization) but different categories or descriptions can be considered duplicates if the differences are minimal or refer to the same concept.
  - For relationships, ensure no duplicate entries based on the same `source`, `target`, and `value`. If the combination of these is identical, treat it as a duplicate.
  - Relationships with the same `source` and `target` but completely different 'value' are not duplicates.
- Ensure that all relationships in their final list relate to entities in their final list.
"""


json_schema1 = {
    "title": "GraphSchema",
    "description": "Schema to define entities and relationships.",
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "description": "List of entities",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the entity"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category or label of the entity"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the entity"
                    }
                },
                "required": ["name", "category", "description"]
            }
        },
        "relationships": {
            "type": "array",
            "description": "List of relationships between entities",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Name of the origin entity"
                    },
                    "target": {
                        "type": "string",
                        "description": "Name of the target entity"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value or label of the relationships"
                    }
                },
                "required": ["source", "target", "value"]
            }
        }
    },
    "required": ["entities", "relationships"]
}

json_schema2 = {
    "title": "LLMResponseSchema",
    "description": "Schema to define the LLM response format.",
    "type": "object",
    "properties": {
        "response": {
            "type": "string",
            "description": "The response generated by the LLM"
        }
    },
    "required": ["response"]
}