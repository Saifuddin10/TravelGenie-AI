import chromadb

client = chromadb.PersistentClient(path="travel_db")

collection = client.get_or_create_collection(name="travel_places") 