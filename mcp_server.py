from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# --------------
# TOOLS
# --------------

@mcp.tool(
    name="read_doc_contents",
    description="Reads the contents of a document and return its contents as a string.",
)
def read_document(
    doc_id: str = Field(description="The ID of the document to read.") 
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found.")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edits a document by replacing a string in the document content with a new string.",
)
def edit_document(
    doc_id: str = Field(description="The ID of the document that will be edited."),
    old_string: str = Field(description="The string to be replaced in the document. Must match exactly, including whitespace."),
    new_string: str = Field(description="The string to replace the old string with."),
) -> None:
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found.")
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)

# --------------
# RESOURCES
# --------------

# Decorator
@mcp.resource(
    "docs://documents", # Direct resource URI
    mime_type="application/json",
)
# Resource function
def list_documents() -> list[str]:
    return list(docs.keys())


@mcp.resource(
    "docs://documents/{doc_id}", # Templated resource URI (with parameter)
    mime_type="text/plain",
)
def fetch_document(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found.")
    return docs[doc_id]

# --------------
# PROMPTS
# --------------

# Thoroughly tested, evalled, tailored for this one specific use case
@mcp.prompt(
    name="format",
    description="Reformats a document into markdown format.",
)
def format_document(
    doc_id: str = Field(description="The ID of the document to format.")
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat the contents of the document with ID '{doc_id}' into markdown format.
    Add headers, bullet points, and other markdown elements as appropriate to enhance readability.
    Use the 'edit_document' tool to make the necessary changes in the documents.
    """
    return [base.UserMessage(prompt)]
    


# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
