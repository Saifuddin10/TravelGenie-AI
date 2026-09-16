from functools import lru_cache
from app.rag.chroma_client import collection

@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_places(destination: str, top_k: int = 50):

    model = get_model()

    embedding = model.encode(destination).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    places = []

    for metadata in results["metadatas"][0]:
        places.append(metadata)

    return places