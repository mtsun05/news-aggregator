from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.news import router as news_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}
