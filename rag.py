
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

# Find the project folder
BASE_DIR = Path(__file__).resolve().parent

# Convert text into embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create a local vector database
client = chromadb.PersistentClient(
    path=str(BASE_DIR / "chroma_db")
)

collection = client.get_or_create_collection(
    name="hospital_it_support"
)

# Store hospital IT instructions
def load_knowledge():
    guide = (BASE_DIR / "hospital_it_guide.txt").read_text(
        encoding="utf-8"
    )

    sections = [
        section.strip()
        for section in guide.split("\n\n")
        if section.strip()
    ]

    embeddings = model.encode(sections).tolist()

    collection.upsert(
        ids=[f"guide_{i}" for i in range(len(sections))],
        documents=sections,
        embeddings=embeddings
    )

# Search the database
def search_knowledge(question):
    query_embedding = model.encode([question]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=1
    )

    documents = results.get("documents", [[]])[0]

    if documents:
        return documents[0]

    return "No matching IT instructions were found."

# Load the knowledge base
load_knowledge()
