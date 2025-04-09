from os import getenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

from core.constants import modeloGpt4omini, openaiApiVersion, openAiApiType, json_schema1, modeloGpt4o


class AzureAdapter:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            openai_api_version=openaiApiVersion,
            #deployment_name=modeloGpt4o,
            deployment_name=modeloGpt4omini,
            azure_endpoint=getenv("ModelsEndpoint"),
            openai_api_key=getenv("ModelsKey"),
            openai_api_type=openAiApiType,
        ).with_structured_output(json_schema1)
        
    def set_output_schema(self, json_schema):
        self.llm = AzureChatOpenAI(
            openai_api_version=openaiApiVersion,
            #deployment_name=modeloGpt4o,
            deployment_name=modeloGpt4omini,
            azure_endpoint=getenv("ModelsEndpoint"),
            openai_api_key=getenv("ModelsKey"),
            openai_api_type=openAiApiType,
        ).with_structured_output(json_schema)
        

    def call_llm(self,prompt_template: str, **kwargs):
        prompt_template = PromptTemplate.from_template(prompt_template)
        prompt = prompt_template.format(**kwargs)
        message = HumanMessage(content=prompt)
        response = self.llm.invoke([message])
        return response