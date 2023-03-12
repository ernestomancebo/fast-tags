from pydantic import BaseModel


# Tagged Link's section
class TaggedLinkBase(BaseModel):
    url: str
    tags: list[str]


class TaggedLinkCreate(TaggedLinkBase):
    pass


class TaggedLink(TaggedLinkBase):
    _id: int
    owner_id: int

    class Config:
        orm_mode = True


# Users' section
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    _id: int
    is_active: bool
    links: list[TaggedLink] = []

    class Config:
        orm_mode = True
