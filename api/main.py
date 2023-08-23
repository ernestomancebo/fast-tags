from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

# Init environment before anything else!
load_dotenv('.env')

from api import service
from api.database import session_local
import api.schemas as schemas

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
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User], status_code=200)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               user_service: service.UserService = Depends(get_user_service)):
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, status_code=200)
def read_user(user_id: int, db: Session = Depends(get_db),
              user_service: service.UserService = Depends(get_user_service)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
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


# if __name__ == "__main__":
#     uvicorn.run(app, host='0.0.0.0', port=environ.get(
#         'APP_UVICORN_PORT', 9090))
