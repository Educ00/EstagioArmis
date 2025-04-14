from os import getenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from core.constants import modeloGpt4omini, openaiApiVersion, openAiApiType, json_schema1, modeloGpt4o


class AzureAdapter:
    llm_base : AzureChatOpenAI= None
    llm = None
    def __init__(self):
        self.llm_base = self.get_llm_base()
        self.llm = None
        
    def get_llm_base(self):
        """
        Retrieves the instance of the AzureChatOpenAI
        :return: AzureChatOpenAI instance
        """
        if self.llm_base is None:
            self.change_schema()
        return self.llm_base
    
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
        
        

    def call_llm(self,prompt_template: str, **kwargs):
        from datetime import datetime
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
        response = self.llm.invoke([message])
        end = datetime.now()
        print("[Azure Adapter]: LLM Called.")
        return response, start, end