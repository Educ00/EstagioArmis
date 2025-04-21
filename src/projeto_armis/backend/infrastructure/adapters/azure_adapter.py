from os import getenv

from datetime import datetime

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_community.vectorstores import AzureSearch
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from core.constants import modeloGpt4omini, openaiApiVersion, openAiApiType, json_schema1, modeloGpt4o, modeloAda


class AzureAdapter:
    llm_base : AzureChatOpenAI= None
    llm = None
    llm_embeddings_base : AzureOpenAIEmbeddings = None
    vector_store : AzureSearch = None
    search_client : SearchClient = None
    def __init__(self):
        self.llm_base = self.get_llm_base()
        self.llm = None
        self.llm_embeddings_base = self.get_llm_embeddings_base()
        self.vector_store = self.get_vector_store()
    def get_llm_base(self):
        """
        Retrieves the instance of the AzureChatOpenAI
        :return: AzureChatOpenAI instance
        """
        if self.llm_base is None:
            self.change_schema()
        return self.llm_base
    
    def get_llm_embeddings_base(self):
        print("[Azure Adapter]: Initializing LLM Embeddings instance...")
        if self.llm_embeddings_base is None:
            self.llm_embeddings_base = AzureOpenAIEmbeddings(
                model= modeloAda,
                azure_endpoint= getenv("MODELS_ENDPOINT"),
                api_key= getenv("MODELS_ENDPOINT_KEY"),
                #openai_api_version=openaiApiVersion
            )
        print("[Azure Adapter]: LLM Embeddings Instance Created.")
        return self.llm_embeddings_base
    
    def get_vector_store(self):
        print("[Azure Adapter]: Initializing Azure Search Instance...")
        if self.vector_store is None:
            self.vector_store = AzureSearch(
                azure_search_endpoint=getenv("AZURE_URL"),
                azure_search_key=getenv("AZURE_URL_KEY"),
                index_name=getenv("INDEX_NAME_1"),
                embedding_function=self.llm_embeddings_base
            )
        print("[Azure Adapter]: Azure Search Instance Created.")
        self.get_search_client()
        return self.vector_store
    
    def get_search_client(self):
        print("[Azure Adapter]: Initializing Azure Search Client Instance...")
        if self.search_client is None:
            self.search_client = SearchClient(
                endpoint=getenv("AZURE_URL"),
                index_name=getenv("INDEX_NAME_1"),
                credential=AzureKeyCredential(getenv("AZURE_URL_KEY"))
            )
        print("[Azure Adapter]: Azure Search Client Instance Created.")
            
        return self.search_client
    
    def change_schema(self, json_schema = None):
        """
        Saves an instance of AzureChatOpenAI
        :param json_schema: json_schema of the output
        """
        if not self.llm_base:
            print("[Azure Adapter]: Initializing LLM instance...")
            self.llm_base = AzureChatOpenAI(
                openai_api_version=openaiApiVersion,
                #deployment_name=modeloGpt4o,
                deployment_name=modeloGpt4omini,
                azure_endpoint=getenv("MODELS_ENDPOINT"),
                openai_api_key=getenv("MODELS_ENDPOINT_KEY"),
                openai_api_type=openAiApiType,
            )
        temp_llm = self.get_llm_base()
        if json_schema:
            print("[Azure Adapter]: With schema...")
            temp_llm = temp_llm.with_structured_output(json_schema, strict=True)
        self.llm = temp_llm
        print("[Azure Adapter]: LLM Instance Created.")
        
    def change_index(self, index: str):
        self.vector_store = AzureSearch(
            azure_search_endpoint=getenv("AZURE_URL"),
            azure_search_key=getenv("AZURE_URL_KEY"),
            index_name=index,
            embedding_function=self.llm_embeddings_base
        )
        self.search_client = SearchClient(
            endpoint=getenv("AZURE_URL"),
            index_name=index,
            credential=AzureKeyCredential(getenv("AZURE_URL_KEY"))
        )

    def call_llm(self,prompt_template: str, **kwargs):
        """
        Calls an LLM and retrieves the answer 
        :param prompt_template: template of the prompt
        :param kwargs: parameters of the prompt template
        :return: response of LLM
        """
            
            
        print("[Azure Adapter]: Calling LLM")
        start = datetime.now()
        prompt_template = PromptTemplate.from_template(prompt_template)
        prompt = prompt_template.format(**kwargs)
        message = HumanMessage(content=prompt)
        print("[Azure Adapter]: Thinking...")
        with get_openai_callback() as cb:
            response = self.llm.invoke([message])
        #print(f"[Azure Adapter]: Prompt Tokens: {cb.prompt_tokens}")
        #print(f"[Azure Adapter]: Completion Tokens: {cb.completion_tokens}")
        #print(f"[Azure Adapter]: Total Tokens: {cb.total_tokens}")
        #print(f"[Azure Adapter]: Total Cost (Dollar): {cb.total_cost}")
        end = datetime.now()
        print("[Azure Adapter]: LLM Called.")
        return response, start, end, cb
    
    def call_vector_store(self, query):
        print("[Azure Adapter]: Calling Azure Ai Search")
        start = datetime.now()
        response = self.vector_store.similarity_search(query, search_type="hybrid")
        end = datetime.now()
        print("[Azure Adapter]: Azure Ai Search Called")
        return response, start, end

    def import_documents(self, docs):
        return self.vector_store.add_documents(documents=docs)