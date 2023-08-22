from pydantic import BaseModel, Field


# Tagged Link's section
class TaggedLinkBase(BaseModel):
    url: str
    tags: list[str]


class TaggedLinkCreate(TaggedLinkBase):
    pass


class TaggedLink(TaggedLinkBase):
    id: int = Field(alias="_id")
    owner_id: int

    class Config:
        orm_mode = True


# Users' section
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int = Field(alias="_id")
    is_active: bool
    links: list[TaggedLink] = []

    class Config:
        orm_mode = True
