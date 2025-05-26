## Qdrant + Ingestion Client: Dockerized Setup

This single-file README provides everything you need to build and run a Qdrant vector database and a Python ingestion client with Docker. The client reads .txt files from a host-mounted folder, embeds them, and uploads them to Qdrant.

### Project Structure

```
.
├── Dockerfile.qdrant         # Qdrant server Dockerfile
├── Dockerfile.ingest         # Ingestion client Dockerfile
├── ingest_texts.py           # Python script to ingest .txt files into Qdrant
├── requirements.txt          # Python requirements for ingestion client
└── data/                     # Your text files here (e.g. file1.txt, file2.txt)
```


---

### Included Example Text File

The `data/` folder contains an example text file: **story.txt**.

- **File:** `story.txt`
- **Description:** A humorous, original story about Reginald Thistlewhiskers, an adventurous rabbit, and his friends in Willowbrook Valley. The story is rich with character names, places, lore, and events, making it useful for vector search, retrieval-augmented generation, and QA demos.
- **Authorship:** This story was generated with the assistance of OpenAI's ChatGPT for demonstration and testing purposes. You are free to use, modify, and redistribute this text as needed.

---


## 1. Prerequisites

* Docker installed ([https://www.docker.com/get-started](https://www.docker.com/get-started))
* Any folder with .txt files (e.g. ./my\_texts)

---

## 2. Qdrant Server

Build (optional) and run Qdrant:

```bash
docker build -t qdrant-server -f Dockerfile.qdrant .
docker run -d --name qdrant-server -p 6333:6333 qdrant-server
```

Qdrant listens on port 6333.

---

The Qdrant Dashboard can be accessed at:[http://localhost:6333/dashboard#/welcome](http://localhost:6333/dashboard#/welcome)


## 3. Ingestion Client

Build the ingestion client Docker image:

```bash
docker build -t qdrant-ingest -f Dockerfile.ingest .
```

Run the client, mounting your local text folder:

```bash
docker run --rm \
  --name qdrant-ingest \
  --network host \
  -e DATA_DIR=/data \
  -v "$(pwd)/data:/data" \
  qdrant-ingest
```

* `--rm` auto-removes the container after finish
* `--network host` lets the client talk to Qdrant at localhost:6333
* `-v "$(pwd)/my_texts:/data"` mounts your host folder as /data in the container

---

## 4. Verify

After ingestion, check Qdrant:

```bash
curl http://localhost:6333/collections/rag/
```

---

## 5. Customization

* To change collection name: Edit `COLL` in `ingest_texts.py`
* To use a different embedding model: Change the model name in `ingest_texts.py`
* For Docker bridge network (alternative to host):

```bash
docker network create qdrant-net
docker run -d --name qdrant-server --network qdrant-net -p 6333:6333 qdrant-server
docker run --rm --name qdrant-ingest --network qdrant-net -e DATA_DIR=/data -v "$(pwd)/my_texts:/data" qdrant-ingest
```

