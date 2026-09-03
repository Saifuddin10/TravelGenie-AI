from sentence_transformers import SentenceTransformer
from app.rag.chroma_client import collection

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_places(destination: str, top_k: int = 50):

    embedding = model.encode(destination).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    places = []

    for metadata in results["metadatas"][0]:
        places.append(metadata)

    return places