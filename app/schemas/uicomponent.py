from pydantic import BaseModel

class UIComponentBase(BaseModel):
    name: str
    is_visible: bool

class UIComponentCreate(UIComponentBase):
    pass

class UIComponent(UIComponentBase):
    id: int

    class Config:
        from_attributes = True
