from app.food_rag.retriever import retrieve_food

foods = retrieve_food("Hyderabad")

for food in foods:
    print(food)