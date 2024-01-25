from fastapi import FastAPI
from blog import schemas

app = FastAPI()

@app.post("/")
def create(request: schemas.Blog):
    return request
