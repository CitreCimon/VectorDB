import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Connect to Qdrant (container hostname qdrant-server)
client = QdrantClient(host="localhost", port=6333)  # pip install qdrant-client :contentReference[oaicite:2]{index=2}

COLL = "rag"
VEC_SIZE = 384

# Create collection if missing
if COLL not in [c.name for c in client.get_collections().collections]:
    client.create_collection(
        collection_name=COLL,
        vectors_config=VectorParams(size=VEC_SIZE, distance=Distance.COSINE),
    )

model = SentenceTransformer("all-MiniLM-L6-v2")  # pip install sentence-transformers

# Read from env or default mount
DATA_DIR = os.getenv("DATA_DIR", "/data")

for fname in os.listdir(DATA_DIR):
    if fname.endswith(".txt"):
        text = open(os.path.join(DATA_DIR, fname), encoding="utf-8").read()
        vec = model.encode(text).tolist()
        pt = PointStruct(id=str(uuid.uuid4()), vector=vec,
                         payload={"filename": fname, "text": text})
        client.upsert(collection_name=COLL, points=[pt])

print("Ingestion complete, exiting.")
