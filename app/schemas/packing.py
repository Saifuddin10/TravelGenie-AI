from pydantic import BaseModel

class PackingItem(BaseModel):
    item: str
    destination: str
    duration: str
    reason: str