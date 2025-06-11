from datetime import datetime
from os import getenv


from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from core.constants import modeloGpt4omini, openaiApiVersion, openAiApiType, json_schema1, modeloGpt4o, modeloAda


class AzureAdapter:
    llm_base : AzureChatOpenAI= None
    llm = None
    llm_embeddings_base : AzureOpenAIEmbeddings = None
    def __init__(self):
        self.llm_base = self.get_llm_base()
        self.llm = None
        self.llm_embeddings_base = self.get_llm_embeddings_base()
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

    
    def change_schema(self, json_schema = None):
        """
        Saves an instance of AzureChatOpenAI
        :param json_schema: json_schema of the output
        """
        if not self.llm_base:
            print("[Azure Adapter]: Initializing LLM instance...")
            self.llm_base = AzureChatOpenAI(
                openai_api_version=openaiApiVersion,
                deployment_name=modeloGpt4o,
                #deployment_name=modeloGpt4omini,
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

    def call_llm(self,prompt_template: str, **kwargs):
        """
        Calls an LLM and retrieves the answer 
        :param prompt_template: template of the prompt
        :param kwargs: parameters of the prompt template
        :return: response of LLM
        """
            
        print("[Azure Adapter]: Calling LLM")
        prompt_template = PromptTemplate.from_template(prompt_template)
        prompt = prompt_template.format(**kwargs)
        message = HumanMessage(content=prompt)
        response = self.llm.invoke([message])
        return response