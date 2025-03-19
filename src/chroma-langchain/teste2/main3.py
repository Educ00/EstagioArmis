from dotenv import load_dotenv
import os

load_dotenv()

modelsEndpoint = os.getenv('ModelsEndpoint')

print(modelsEndpoint)
