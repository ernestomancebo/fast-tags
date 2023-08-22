from sqlalchemy.orm import Session

import api.schemas as schemas
from api import models


class UserService:
    """
    Service layer for User model
    """

    def __init__(self):
        pass

    def get_user(self, db: Session, user_id: int):
        return db.query(models.User).filter(models.User._id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, user: schemas.UserCreate):
        not_hashed_password = f'{user.password}SOME_HASH'
        db_user = models.User(
            email=user.email,
            hashed_password=not_hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user


class TaggedLinkService:
    """
    Service layer for TaggedLink model
    """

    def get_tagged_links(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.TaggedLink).offset(skip).limit(limit).all()

    def get_tagged_link_by_id(self, db: Session, tagged_link_id: int):
        return db.query(models.TaggedLink).get(models.TaggedLink._id == tagged_link_id)

    def create_user_tagged_link(self, db: Session,
                                tagged_link: schemas.TaggedLinkCreate,
                                user_id: int):
        db_tagged_link = models.TaggedLink(
            **tagged_link.dict(), owner_id=user_id)
        db.add(db_tagged_link)
        db.commit()
        db.refresh(db_tagged_link)

        return db_tagged_link

    def update_user_tagged_link(self, db: Session,
                                tagged_link: schemas.TaggedLinkUpdate):
        db_tagged_link = db.query(models.TaggedLink).get(
            models.TaggedLink._id == tagged_link._id)
        if db_tagged_link is None:
            return None

        db_tagged_link.tags = tagged_link.tags
        db.commit()
        db.refresh(db_tagged_link)

        return db_tagged_link

    def delete_user_tagged_link(self, db: Session,
                                tagged_link_id: int):
        deleted_count = db.query(models.TaggedLink).filter(
            models.TaggedLink._id == tagged_link_id).delete()
        db.commit()

        return bool(deleted_count)
