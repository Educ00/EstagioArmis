import os
import pickle
import json

from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage

load_dotenv()

#os.getenv("ModelsEndpoint")
#os.getenv("ModelsKey")
#os.getenv("AzureUrl")
#os.getenv("AzureKey")

modeloAda = "text-embedding-ada-002"
modeloGpt4o = "GPT-4o"
modeloGpt4omini = "GPT-4o-mini"

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
- Capture all meaningful connections

REQUIREMENTS:
- Be comprehensive - extract all information in one pass
- Maintain consistent terminology
- Base all extractions strictly on text content, not external knowledge
- Produce a clean JSON.
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


# ---------------------------- Plano 1 --------------------------------
# Passo 1 - Dividir o texto em chunks de tamanho n (a definir, podemos começar com 200) com algum overlaping (20 é capaz de ser bom).
# Passo 2 - Criar uma prompt que pede para extrair entidades, relações entre entidades e informações.
# Passo 3 - Iterar sobre os chunks.
# Passo 4 - Pegar na lista de informações e pedir para verificar sobre entidades e relações duplicadas ou equivalentes.

# -----------------

def split_text(directory: str, chunk_size: int = 250, chunk_overlap: int = 50):
    loader = DirectoryLoader(directory)
    print("   Directory: ", directory)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    return chunks


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
        llm = llm.with_structured_output(json_schema1)

    return llm


def call_llm(llm: AzureChatOpenAI, prompt_template: str, **kwargs):
    print("A chamar LLM")
    prompt_template = PromptTemplate.from_template(prompt_template)
    prompt = prompt_template.format(**kwargs)
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    return response


# -------------------------

call_with_context = True


def main():
    dir = "./ficheiros"
    print("A ler ficheiros...")
    chunks = split_text(directory=dir + "/input", chunk_size=250, chunk_overlap=25)
    print("A inicializar instância do LLM")
    llm = initialize_azureOpenAI_llm(
        model_deployment_name=modeloGpt4omini,
        azure_endpoint=os.getenv("ModelsEndpoint"),
        openai_api_key=os.getenv("ModelsKey"),
        openai_api_type="azure",
        #gopenai_api_version="2024-02-01",
        openai_api_version="2024-10-21",
        output_schema=json_schema1
    )

    template = '''
        <instructions>{instructions}</instructions>
        <text>{text}</text>
    '''

    if not call_with_context:
        print("Sem contexto")
        responses = []
        for chunk in chunks:
            responses.append(call_llm(llm=llm, prompt_template=template, instructions=prompt_instructions2, text=chunk))

    else:
        print("Com contexto")
        responses = []

        messages = [
            {"role": "system", "content": prompt_instructions2},
            {"role": "user", "content": "Please follow everything."}
        ]

        response = llm.invoke(messages)
        response_str = json.dumps(response)
        messages.append({"role": "assistant", "content": response_str})

        for i, chunk in enumerate(chunks):
            print(f"Chunk #{i + 1}/{len(chunks)}")
            messages.append({"role": "user", "content": f"Chunk #{i + 1}/{len(chunks)}: {chunk}"})

            response = llm.invoke(messages)
            response_str = json.dumps(response)
            responses.append(response)
            messages.append({"role": "assistant", "content": response_str})

    #print("Repostas: ")

    #for response in responses:
    #    print("   response:")
    #    print(response)

    os.makedirs(dir + "/output", exist_ok=True)
    arquivos = [f for f in os.listdir(dir + "/output") if f.startswith("respostas") and f.endswith(".txt")]
    N = len(arquivos) + 1
    caminho_arquivo = os.path.join(dir + "/output", f"respostas{N}.txt")
    print("A guardar resposta em: ", caminho_arquivo)
    data = responses[-1]

    # formatamos com indentação
    data = json.dumps(data, indent=4)

    # convertemos para string e trocamos os chars literais para os escape chars
    #data = str(data).replace(r"\n", "\n").replace(r"\"", "\"").replace("  ", "\t").replace("\"```json", "").replace("```\"", "")

    with open(caminho_arquivo, 'w', encoding='utf-8') as outp:  # Overwrites any existing file.
        # carregamos a indentação e guardamos
        json.dump(json.loads(data, strict=False), outp, indent=4)


if __name__ == "__main__":
    main()
