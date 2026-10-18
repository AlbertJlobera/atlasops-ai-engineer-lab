from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from app.config import MODEL_EMBEDDING


embeddings = OpenAIEmbeddings(
    model=MODEL_EMBEDDING,
)