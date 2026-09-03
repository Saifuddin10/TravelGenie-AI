import json

from sentence_transformers import SentenceTransformer
from app.food_rag.chroma_client import collection

model = SentenceTransformer("all-MiniLM-L6-v2")

existing = collection.get()

if existing["ids"]:
    print("Removing existing food embeddings...")
    collection.delete(ids=existing["ids"])

print("Ingesting Food data...")

with open("app/data/food.json", "r", encoding="utf-8") as f:
    foods = json.load(f)

for idx, food in enumerate(foods):

    text = f"""
Destination: {food['destination']}
Dish: {food['dish']}
Restaurant: {food['restaurant']}
Cataegory: {food['category']}
Price: {food['price']}
Desription: {food['description']}
"""

    embeddings = model.encode(text).tolist()

    collection.add(
        ids=[str(idx)],
        documents=[text],
        embeddings=[embeddings],
        metadatas=[food] 
    )

print("Food data ingested successfully.")