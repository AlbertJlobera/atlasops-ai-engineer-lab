from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

CONNECTION = "postgresql+psycopg://atlasops:atlasops@localhost:5433/atlasops"
DOCS_COLLECTION = "atlasops_docs"
CODE_COLLECTION = "atlasops_code"
MODEL_EMBEDDING = "text-embedding-3-small"
MODEL_JUDGE = "gpt-4o-mini"
DEFAULT_K = 3
CODE_DEFAULT_K = 5

SENSITIVE_TOOLS = {
    "restart_service"
}

DOCUMENTS_PATH = Path(
    r"C:\Ai Proyecto\AI_Engineer_Lab_01_AtlasOps\knowledge_base"
)