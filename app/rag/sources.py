from pathlib import PurePosixPath


def normalize_source_name(
    source: str | None,
) -> str:

    if not source:
        return ""

    normalized = source.replace(
        "\\",
        "/",
    )

    return PurePosixPath(
        normalized
    ).name


def build_sources(results):
    sources = []

    for doc, score in results:
        source_type = doc.metadata.get(
            "source_type"
        )

        if source_type == "code":
            sources.append(
                {
                    "source": doc.metadata.get(
                        "source"
                    ),
                    "path": doc.metadata.get(
                        "path"
                    ),
                    "module": doc.metadata.get(
                        "module"
                    ),
                    "symbol": doc.metadata.get(
                        "symbol"
                    ),
                    "symbol_type": doc.metadata.get(
                        "symbol_type"
                    ),
                    "start_line": doc.metadata.get(
                        "start_line"
                    ),
                    "end_line": doc.metadata.get(
                        "end_line"
                    ),
                    "score": score,
                }
            )

        else:
            sources.append(
                {
                    "source": normalize_source_name(
                        doc.metadata.get(
                            "source"
                        )
                    ),
                    "section": doc.metadata.get(
                        "section"
                    ),
                    "subsection": doc.metadata.get(
                        "subsection"
                    ),
                    "score": score,
                }
            )

    return sources