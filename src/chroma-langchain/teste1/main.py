from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Criar um modelo de embeddings atualizado
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Criar a base de dados vetorial Chroma
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Adicionar textos à base de dados
texts = ["O céu é azul", "Os pássaros voam", "O oceano é profundo"]
db.add_texts(texts)

# Fazer uma pesquisa semântica
query = "Qual a cor do céu?"
results = db.similarity_search(query, k=1)  # Retorna o documento mais próximo
print(results)
