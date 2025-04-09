from os import getenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from core.constants import modeloGpt4omini, openaiApiVersion, openAiApiType, json_schema1, modeloGpt4o


class AzureAdapter:
    llm = None
    def __init__(self):
        self.llm = self.get_llm()
        
    def get_llm(self):
        """
        Retrieves the instance of the AzureChatOpenAI
        :return: AzureChatOpenAI instance
        """
        if self.llm is None:
            self.create_new_llm()
        return self.llm
    
    def create_new_llm(self, json_schema=None):
        """
        Saves an instance of AzureChatOpenAI
        :param json_schema: json_schema of the output
        """
        print("Initializing LLM instance...")
        temp_llm = AzureChatOpenAI(
            openai_api_version=openaiApiVersion,
            deployment_name=modeloGpt4o,
            #deployment_name=modeloGpt4omini,
            azure_endpoint=getenv("MODELS_ENDPOINT"),
            openai_api_key=getenv("MODELS_ENDPOINT_KEY"),
            openai_api_type=openAiApiType,
        )
        
        if json_schema:
            print("   With schema...")
            temp_llm = temp_llm.with_structured_output(json_schema)
        self.llm = temp_llm
        print("Done")
        
        

    def call_llm(self,prompt_template: str, **kwargs):
        """
        Calls an LLM and retrieves the answer 
        :param prompt_template: template of the prompt
        :param kwargs: parameters of the prompt template
        :return: response of LLM
        """
        print("Calling LLM")
        prompt_template = PromptTemplate.from_template(prompt_template)
        prompt = prompt_template.format(**kwargs)
        message = HumanMessage(content=prompt)
        print(" Thinking...")
        response = self.llm.invoke([message])
        print("Done")
        return response