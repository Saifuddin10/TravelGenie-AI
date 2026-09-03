import chromadb

client = chromadb.PersistentClient(path="food_chroma_db")

collection = client.get_or_create_collection(name="food_collection")