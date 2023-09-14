import logging
import random

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
from sqlalchemy.orm import Session

# Init environment before anything else!
load_dotenv('.env')

import api.schemas as schemas
from api import service
from api.database import session_local

# Setup
random.seed(42)
logger= logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


@app.get("/ping")
def ping():
    return {"ping": "pong pong"}


@app.post("/users/", response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                user_service: service.UserService = Depends(get_user_service)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        logger.info(f"Email '{user.email}' already registered", exc_info=True)
        exception = HTTPException(status_code=400, detail=f"Email '{user.email}' already registered")

        span = trace.get_current_span()
        span.record_exception(exception)
        span.set_attributes({'est': True})
        span.set_status(Status(StatusCode.ERROR, f"Email '{user.email}' already registered"))
        
        raise exception 
    return user_service.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User], status_code=200)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               user_service: service.UserService = Depends(get_user_service)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, status_code=200)
def read_user(user_id: int, db: Session = Depends(get_db),
              user_service: service.UserService = Depends(get_user_service)):
    logger.info(f"Reading user. ID: '{user_id}'", exc_info=True)

    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        logger.info("User does not exists", exc_info=True)
        exception = HTTPException(status_code=404, detail="User not found")

        span = trace.get_current_span()
        span.record_exception(exception)
        span.set_attributes({'est': True})
        span.set_status(Status(StatusCode.ERROR, "User does not exists"))
        raise exception
    return db_user


@app.post("/users/{user_id}/links/", response_model=schemas.TaggedLink, status_code=201)
def create_item_for_user(
        user_id: int, tagged_link: schemas.TaggedLinkCreate,
        db: Session = Depends(get_db),
        tagged_links_service: service.TaggedLinkService = Depends(
            get_tagged_link_service)
):
    return tagged_links_service. \
        create_user_tagged_link(db=db, tagged_link=tagged_link,
                                user_id=user_id)


@app.put("/links/{link_id}", response_model=schemas.TaggedLink, status_code=200)
def update_item(link_id: int, tagged_link: schemas.TaggedLinkUpdate,
                db: Session = Depends(get_db),
                tagged_links_service: service.TaggedLinkService = Depends(
                    get_tagged_link_service)):
    db_tagged_link = tagged_links_service.update_user_tagged_link(db=db,
                                                                  tagged_link=tagged_link)
    if db_tagged_link is None:
        raise HTTPException(status_code=404, detail="Tagged link not found")
    return db_tagged_link


@app.delete("/links/{link_id}", status_code=204)
def delete_item(link_id: int, db: Session = Depends(get_db),
                tagged_links_service: service.TaggedLinkService = Depends(
                    get_tagged_link_service)):
    db_tagged_link = tagged_links_service.delete_user_tagged_link(db=db,
                                                                  tagged_link_id=link_id)
    if not db_tagged_link:
        raise HTTPException(status_code=404, detail="Tagged link not found")
    
    # 204 is OK + No Content
    return

@app.get("/links/", response_model=list[schemas.TaggedLink], status_code=200)
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               tagged_links_service: service.TaggedLinkService = Depends(
                   get_tagged_link_service)):
    items = tagged_links_service.get_tagged_links(db, skip=skip, limit=limit)
    return items

@app.get("/external-api", status_code=200)
def external_api():
    seconds = random.uniform(0, 3)
    response = requests.get(f"https://httpbin.org/delay/{seconds}")
    response.close()
    return {"message": "ok"}

# if __name__ == "__main__":
#     uvicorn.run(app, host='0.0.0.0', port=environ.get(
#         'APP_UVICORN_PORT', 9090))
