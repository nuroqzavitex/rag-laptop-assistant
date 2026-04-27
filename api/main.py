from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, health, products
from retriever.semantic_router import init_router
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_router()
  yield

app = FastAPI(
  title = "Hùng Nhữ Laptop Chatbot API",
  description = "RAG-powered chatbot for laptop sales consulting",
  version = '1.0.0',
  lifespan=lifespan
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(products.router)

if __name__ == "__main__":
  uvicorn.run('api.main:app', host='0.0.0.0', port=8000, reload=True)

