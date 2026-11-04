from pathlib import Path
import ast
from langchain_core.documents import Document

def load_python_files(path):
    return list(Path(path).rglob("*.py"))

def get_module_name(file_path, root_path):
    return file_path.relative_to(root_path).with_suffix("").as_posix().replace("/", ".")

def parse_python_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    return source, tree

def extract_code_chunks(file_path, root_path):
    source, tree = parse_python_file(file_path)
    module_name = get_module_name(file_path, root_path)

    chunks = []
    module_code = []

    lines = source.splitlines()

    for node in tree.body:

        # Functions, async functions and classes
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            start_line = node.lineno - 1
            end_line = node.end_lineno

            code_chunk = lines[start_line:end_line]

            chunks.append({
                "module": module_name,
                "name": node.name,
                "type": type(node).__name__,
                "code": "\n".join(code_chunk),
                "start_line": start_line + 1,
                "end_line": end_line,
            })

        # Module-level variables / constants
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            start_line = node.lineno - 1
            end_line = node.end_lineno

            module_code.extend(
                lines[start_line:end_line]
            )

    # Create one chunk with module-level code
    if module_code:
        chunks.append({
            "module": module_name,
            "name": module_name,
            "type": "module",
            "code": "\n".join(module_code),
            "start_line": None,
            "end_line": None,
        })

    return chunks

def build_code_documents(root_path):
    python_files = load_python_files(root_path)

    all_documents = []

    for file_path in python_files:
        chunks = extract_code_chunks(file_path, root_path)

        for chunk in chunks:
            document = Document(
                page_content=chunk["code"],
                metadata={
                    "source": file_path.name,
                    "path": str(file_path.relative_to(root_path)),
                    "module": chunk["module"],
                    "symbol": chunk["name"],
                    "symbol_type": chunk["type"],
                    "source_type": "code",
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                }
            )

            all_documents.append(document)

    return all_documents