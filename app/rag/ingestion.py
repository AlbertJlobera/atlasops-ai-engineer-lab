from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter

from app.config import DOCUMENTS_PATH




def load_documents(path: Path = DOCUMENTS_PATH):
    loader = DirectoryLoader(
        path=str(path),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    return loader.load()


def get_splitter():
    return MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "title"),
            ("##", "section"),
            ("###", "subsection"),
        ]
    )


def extract_document_metadata(doc):
    metadata = {
        "source": doc.metadata["source"],
        "legacy": "Status: Legacy" in doc.page_content,
    }

    for line in doc.page_content.splitlines():

        if line.startswith("Version:"):
            metadata["version"] = line.split("Version:", 1)[1].strip()

        elif line.startswith("Updated:"):
            metadata["updated"] = line.split("Updated:", 1)[1].strip()

        elif line.startswith("Owner:"):
            metadata["owner"] = line.split("Owner:", 1)[1].strip()

    return metadata


def build_chunks():
    documents = load_documents()
    splitter = get_splitter()

    chunks = []

    for doc in documents:

        doc_metadata = extract_document_metadata(doc)

        doc_chunks = splitter.split_text(doc.page_content)

        for chunk in doc_chunks:

            chunk.metadata = {
                **doc_metadata,
                **chunk.metadata
            }

            for line in chunk.page_content.splitlines():

                if line.startswith("Status:"):
                    chunk.metadata["status"] = (
                        line.split("Status:", 1)[1].strip()
                    )

        chunks.extend(doc_chunks)

    # Eliminamos chunks sin sección ni subsección
    chunks = [
        chunk
        for chunk in chunks
        if chunk.metadata.get("section") is not None
        or chunk.metadata.get("subsection") is not None
    ]

    return chunks