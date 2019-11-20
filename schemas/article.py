from pydantic import BaseModel


class Article(BaseModel):
    title: str
    case: str

    class Config:
        orm_mode = True
