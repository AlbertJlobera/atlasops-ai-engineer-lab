import os


# Dummy credentials for unit tests.
# Unit tests must not make real OpenAI API calls.
os.environ.setdefault(
    "OPENAI_API_KEY",
    "test-api-key"
)

# Avoid sending unit test traces to LangSmith.
os.environ.setdefault(
    "LANGCHAIN_TRACING_V2",
    "false"
)