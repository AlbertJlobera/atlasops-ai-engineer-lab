from langchain_openai import ChatOpenAI

from app.config import MODEL_JUDGE


llm = ChatOpenAI(
    model=MODEL_JUDGE,
    temperature=0,
    timeout=30,
    max_retries=2,
)