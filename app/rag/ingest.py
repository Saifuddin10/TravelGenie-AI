import json

from sentence_transformers import SentenceTransformer

from app.rag.chroma_client import collection


model = SentenceTransformer("all-MiniLM-L6-v2")


with open("app/data/attractions.json", "r", encoding="utf-8") as f:
    data = json.load(f)


# Remove existing embeddings
existing = collection.get()

if existing["ids"]:
    print("Removing existing embeddings...")
    collection.delete(ids=existing["ids"])


print("Ingesting new data...")


for idx, item in enumerate(data):

    text = f"""
Destination: {item.get('destination', '')}
Place: {item.get('place', '')}
Description: {item.get('description', '')}
Category: {item.get('category', '')}
Type: {item.get('type', '')}
Timings: {item.get('timings', '')}
Best Time: {item.get('best_time', '')}
Visit Duration: {item.get('visit_duration', '')}
Entry Fee: {item.get('entry_fee', '')}
Ideal Weather: {', '.join(item.get('ideal_weather', []))}
Family Friendly: {item.get('family_friendly', '')}
Nearby Places: {', '.join(item.get('nearby_places', []))}
""".strip()

    embedding = model.encode(text).tolist()

    # Copy metadata so we don't modify the original dataset
    metadata = item.copy()

    # ChromaDB does not accept empty lists as metadata values
    if not metadata.get("nearby_places"):
        metadata["nearby_places"] = "None"

    if not metadata.get("ideal_weather"):
        metadata["ideal_weather"] = "None"

    collection.add(
        ids=[str(idx)],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


print("Successfully ingested data into ChromaDB.")