from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma, AzureSearch
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

modeloAda = "text-embedding-ada-002"
modeloGpt4o = "GPT-4o"
modeloGpt4omini = "GPT-4o-mini"

load_dotenv()
#os.getenv("ModelsEndpoint")
#os.getenv("ModelsKey")
#os.getenv("AzureUrl")
#os.getenv("AzureKey")

directory = "./data/"
persistence_directory = "db"

def load_docs(directory):
    loader = DirectoryLoader(directory)
    documents = loader.load()
    return documents


def split_docs(documents, chunk_size=250, chunk_overlap=20):
    text_spliter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_spliter.split_documents(documents)
    return docs


def call_llm_with_context(query, context):
    llm = AzureChatOpenAI(
        openai_api_version="2024-02-01",
        deployment_name=modeloGpt4omini,
        azure_endpoint=os.getenv("ModelsEndpoint"),
        openai_api_key=os.getenv("ModelsKey"),
        openai_api_type="azure",
    )

    template = '''
    Usando o contexto fornecido responde às perguntas do utilizador.
    <query>{query}</query>
    <context>{context}</context>
    '''

    prompt_template = PromptTemplate.from_template(template)
    prompt = prompt_template.format(query=query, context=context)
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    
    return response

def carregar_as_coisas():
    global db, vector_store, embeddings
    print("A carregar documentos...")
    documents = load_docs(directory)
    print("A separar documentos em chunks...")
    docs = split_docs(documents)
    
    print("A criar embeddings...")
    #embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    embeddings = AzureOpenAIEmbeddings(
        model=modeloAda,
        azure_endpoint=os.getenv("ModelsEndpoint"),
        api_key=os.getenv("ModelsKey"),
        openai_api_version="2024-02-01",
    )
    
    print("A guardar documentos na chromaDB local...")
    db = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persistence_directory)
    text = ["O céu é esverdiada às quartas.", "O céu é a amarelado às segundas.", "O céu é azul o resto dos dias.", "Gosto do Ronaldo."]
    db.add_texts(text)
    #db.persist()
    
    print("A guardar documentos na cloud azure...")
    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AzureUrl"),
        azure_search_key=os.getenv("AzureKey"),
        index_name="estagio-eduardocarreiro-teste1",
        embedding_function=embeddings,
    )
    
    vector_store.add_documents(documents=docs)
    vector_store.add_texts(text)

def carregar_apenas_conexoes():
    global db, vector_store, embeddings

    print("A criar embeddings...")
    embeddings = AzureOpenAIEmbeddings(
        model=modeloAda,
        azure_endpoint=os.getenv("ModelsEndpoint"),
        api_key=os.getenv("ModelsKey"),
        openai_api_version="2024-02-01",
    )

    print("A conectar à chromaDB local...")
    db = Chroma(persist_directory=persistence_directory, embedding_function=embeddings)

    print("A conectar à Azure Search...")
    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AzureUrl"),
        azure_search_key=os.getenv("AzureKey"),
        index_name="estagio-eduardocarreiro-teste1",
        embedding_function=embeddings,
    )

def delete_all_documents_paged():
    SEARCH_SERVICE_NAME = "amorim-search-service-002"
    SEARCH_INDEX_NAME = "estagio-eduardocarreiro-teste1"
    API_KEY = os.getenv("AzureKey")
    # Construir a URL do serviço
    endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
    
    # Criar o cliente de pesquisa
    search_client = SearchClient(endpoint=endpoint,
                                 index_name=SEARCH_INDEX_NAME,
                                 credential=AzureKeyCredential(API_KEY))
    deleted_count = 0
    while True:
        results = list(search_client.search(search_text="*", top=1000))
        if not results:
            break  # Sai do loop se não houver mais documentos

        documents_to_delete = [{"@search.action": "delete", "id": doc["id"]} for doc in results]
        search_client.upload_documents(documents=documents_to_delete)
        deleted_count += len(documents_to_delete)

    print(f"Total de documentos excluídos: {deleted_count}")
    

def print_all_docs():
    SEARCH_SERVICE_NAME = "amorim-search-service-002"
    SEARCH_INDEX_NAME = "estagio-eduardocarreiro-teste1"
    API_KEY = os.getenv("AzureKey")
    # Construir a URL do serviço
    endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
    
    # Criar o cliente de pesquisa
    search_client = SearchClient(endpoint=endpoint,
                                 index_name=SEARCH_INDEX_NAME,
                                 credential=AzureKeyCredential(API_KEY))
    results = search_client.search(search_text="*")  # "*" retorna todos os documentos
    for doc in results:
        print(doc)
        
delete_all_documents_paged()
#print_all_docs()
exit(0)

db : Chroma = None
vector_store : AzureSearch = None
embeddings : AzureOpenAIEmbeddings = None

carregar_as_coisas()
#carregar_apenas_conexoes()

sair = False
while not sair:
    query = str(input("Digite a query: "))
    if query == "sair":
        sair = True

    if not sair:
        matching_docs = db.similarity_search(query)
        matching_docs2 = vector_store.similarity_search(query, search_type="hybrid")
        print(f"ChromaDB: {matching_docs}")
        print(f"Azure: {matching_docs2}")
        print("A dar fetch resposta para chromaDB...")
        response = call_llm_with_context(query, matching_docs)
        print("A dar fetch resposta para azure...")
        response2 = call_llm_with_context(query, matching_docs2)
        print(f"Resposta ChromaDB: {response}")
        print(f"Resposta Azure: {response2}")
    else:
        vector_store.client.close()