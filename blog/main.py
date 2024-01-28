from fastapi import FastAPI, Depends, Response, HTTPException
from blog import schemas
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from typing import List
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(engine) # This will create the database if it doesn't exist 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/", status_code=201, tags=["root"])
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/blog", status_code=200, response_model=List[schemas.ShowBlog], tags=["blogs"])
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@app.delete("/blog/{id}", status_code=204, tags=["blogs"])
def destroy(id, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return "done"

@app.get("/blog/{id}", status_code=200, response_model=schemas.ShowBlog, tags=["blogs"])
def show(id, response: Response ,db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail=f"Blog with id {id} not found")
    return blog

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post('/user', tags=["users"])
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    hashed_password = pwd_cxt.hash(request.password)
    new_user = models.User(name=request.name, email=request.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}', response_model=schemas.ShowUser, tags=["users"])
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    return user