from pydantic import BaseModel

class PackingItem(BaseModel):
    item: str
    reason: str