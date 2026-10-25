import time
from pathlib import Path

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

# 1. Find the saved vector database
PROJECT_DIR = Path(__file__).resolve().parent
CHROMA_DIR = PROJECT_DIR / "chroma_db"

# 2. Load the same embedding model used during ingestion
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# 3. Connect to the existing ChromaDB collection
vector_store = Chroma(
    collection_name="incidenttrace_knowledge",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)

# 4. Load the Llama 3.1 language model
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0
)

# 5. Create the instructions for the AI
prompt = ChatPromptTemplate.from_template("""
You are IncidentTrace AI, an IT outage investigation assistant.

Answer the user's question using only the context provided below.

If the context does not contain enough information, say so.
Do not invent logs, events, or root causes.
Suggest practical investigation steps when appropriate.

Context:
{context}

User question:
{question}

Provide:
1. A short explanation
2. Possible causes supported by the context
3. Recommended investigation steps
4. The source files used
""")

# 6. Ask a question
def ask_question(question: str):
    # Retrieve the 4 most relevant document chunks
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        return "I could not find relevant information in the knowledge base."

    # Combine retrieved text and its source filenames
    context_parts = []

    for doc in retrieved_docs:
        source = doc.metadata.get("source", "Unknown source")
        context_parts.append(
            f"Source: {source}\nContent: {doc.page_content}"
        )

    context = "\n\n".join(context_parts)

    # Generate an answer using the retrieved context
    messages = prompt.format_messages(
        context=context,
        question=question
    )

    response = llm.invoke(messages)

    return response.content


# 7. Run a simple terminal chat
if __name__ == "__main__":
    print("===================================")
    print(" Welcome to IncidentTrace AI")
    print(" Type 'exit' to stop")
    print("===================================")

    while True:
        user_question = input("\nEnter your question: ")

        if user_question.strip().lower() in ["exit", "quit"]:
            print("IncidentTrace AI stopped.")
            break

        if not user_question.strip():
            print("Please enter a question.")
            continue

        try:
            answer = ask_question(user_question)
            print("\nIncidentTrace AI Answer:\n")
            print(answer)

        except Exception as error:
            print(f"\nAn error occurred: {error}")
