
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# 1. Set project and data folders
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "Data"
CHROMA_DIR = PROJECT_DIR / "chroma_db"

# 2. Read only our knowledge-base folders
knowledge_folders = [
    "application_logs",
    "deployment_records",
    "incident_reports",
    "troubleshooting_guides",
]

documents = []

for folder_name in knowledge_folders:
    folder_path = DATA_DIR / folder_name

    if not folder_path.is_dir():
        print(f"Warning: Folder not found: {folder_path}")
        continue

    for file_path in folder_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [
            ".txt", ".log", ".md"
        ]:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            if content.strip():
                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path.relative_to(DATA_DIR)),
                            "document_type": folder_name,
                        },
                    )
                )

print(f"Documents loaded: {len(documents)}")

if not documents:
    raise ValueError(
        "No knowledge-base documents found. Check your Data folders."
    )

# 3. Split documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
)

chunks = text_splitter.split_documents(documents)

print(f"Text chunks created: {len(chunks)}")

# 4. Connect to the embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# 5. Rebuild the ChromaDB collection
vector_store = Chroma(
    collection_name="incidenttrace_knowledge",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)

# Delete the old collection so previous runs aren't duplicated
vector_store.delete_collection()

vector_store = Chroma(
    collection_name="incidenttrace_knowledge",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)

# 6. Store the new chunks
vector_store.add_documents(chunks)

print("Successfully stored document chunks in ChromaDB!")
print(f"Database location: {CHROMA_DIR}")
