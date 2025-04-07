UPLOAD_FOLDER = "uploads"

modeloAda = "text-embedding-ada-002"
modeloGpt4o = "GPT-4o"
modeloGpt4omini = "GPT-4o-mini"
openaiApiVersion = "2024-10-21"
openAiApiType = "azure"

prompt_template = '''
<instructions>{instructions}</instructions>
<text>{text}</text>
'''

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
Extract all entities and relationships from the text, following these guidelines:

ENTITIES:
- Specific, meaningful, and non-ambiguous
- Consolidated to avoid redundancy
- The metadata must have the "name", the "category" and the "description" as fields.
- All information must be directly from the text

RELATIONSHIPS:
- Only connect entities in your entities list
- Specify directionality (source_entity → target_entity via relationship)
- Capture all meaningful connections, either direct or implicit

REQUIREMENTS:
- Be comprehensive - extract all information in one pass
- Maintain consistent terminology
- Base all extractions strictly on text content, not external knowledge
- Produce a clean JSON.
- Be aware of duplicates, provided in the context.
- Respect the context.
'''

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