from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import chat, health, products, auth_callback
from retriever.semantic_router import init_router
from core.history import check_db_connection
from core.logger import get_logger
import uvicorn
import os

log = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
  init_router()
  db_ok, db_detail = check_db_connection()
  if db_ok:
    log.info('Supabase chat_history: connected')
  else:
    log.warning(f'Supabase chat_history unavailable: {db_detail}')
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
app.include_router(auth_callback.router)

if __name__ == "__main__":
  port = int(os.getenv("PORT", 8000))
  uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)

