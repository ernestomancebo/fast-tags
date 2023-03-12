from os import environ

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

# Init environment before anything else!
load_dotenv('.env')

import schemas
from api import service
from api.database import session_local

app = FastAPI()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def get_user_service():
    u_service = service.UserService()
    try:
        yield u_service
    finally:
        del u_service


def get_tagged_link_service():
    t_service = service.TaggedLinkService()
    try:
        yield t_service
    finally:
        del t_service


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                user_service: service.UserService = Depends(get_user_service)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               user_service: service.UserService = Depends(get_user_service)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db),
              user_service: service.UserService = Depends(get_user_service)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/links/", response_model=schemas.TaggedLink)
def create_item_for_user(
        user_id: int, tagged_link: schemas.TaggedLinkCreate,
        db: Session = Depends(get_db),
        tagged_links_service: service.TaggedLinkService = Depends(
            get_tagged_link_service)
):
    return tagged_links_service. \
        create_user_tagged_link(db=db, tagged_link=tagged_link,
                                user_id=user_id)


@app.get("/links/", response_model=list[schemas.TaggedLink])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               tagged_links_service: service.TaggedLinkService = Depends(
                   get_tagged_link_service)):
    items = tagged_links_service.get_tagged_links(db, skip=skip, limit=limit)
    return items


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=environ.get(
        'APP_UVICORN_PORT', 9090))
