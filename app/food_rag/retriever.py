from sentence_transformers import SentenceTransformer
from app.food_rag.chroma_client import collection

model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_food(destination: str, top_k: int = 100):

    embeddings = model.encode(destination).tolist()

    results = collection.query(
        query_embeddings=[embeddings],
        n_results=top_k
    )

    places = []

    if not results.get("metadatas"):
        return places

    for metadata in results["metadatas"][0]:

        if not metadata:
            continue

        if metadata.get("destination", "").lower() != destination.lower():
            continue

        places.append(metadata)

    return places