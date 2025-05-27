import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Konfiguration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "rag"
VECTOR_SIZE = 384  # for 'all-MiniLM-L6-v2'
DATA_DIR = os.getenv("DATA_DIR", "./data") 

# Qdrant-Client initialisieren
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Collection anlegen, falls sie fehlt
if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

# Embedding-Modell laden
model = SentenceTransformer("all-MiniLM-L6-v2")

# Textsplitter: 800 Zeichen/Chunk, 100 Overlap
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

print(f"Start Ingestion from {DATA_DIR} ...")
for fname in os.listdir(DATA_DIR):
    if not fname.endswith(".txt"):
        continue
    path = os.path.join(DATA_DIR, fname)
    print(f"processed: {fname}")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = splitter.split_text(text)
    print(f"  -> {len(chunks)} Chunks created")

    for i, chunk in enumerate(chunks):
        vector = model.encode(chunk).tolist()
        pt = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "page_content": chunk,
                "metadata": {
                    "filename": fname,
                    "chunk_index": i,
                    "num_chunks": len(chunks)
                }
            }
        )
        client.upsert(collection_name=COLLECTION_NAME, points=[pt])
    print(f"  -> {len(chunks)} Chunks for {fname} in Qdrant stored")

print("Ingestion finished.")
