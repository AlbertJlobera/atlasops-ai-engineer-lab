from pathlib import Path


def build_context(results):
    context_parts = []

    for i, (doc, score) in enumerate(results, start=1):
        source = Path(doc.metadata.get("source", "")).name
        section = doc.metadata.get("section")
        subsection = doc.metadata.get("subsection")

        context_parts.append(
            f"""
[Chunk {i}]
Source: {source}
Section: {section}
Subsection: {subsection}

{doc.page_content}
"""
        )

    return "\n\n".join(context_parts)