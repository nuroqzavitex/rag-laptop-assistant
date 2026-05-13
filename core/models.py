from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
  id: str
  name: str
  brand: str
  price: int
  currency: str = "VNĐ"
  category: list[str] = Field(default_factory=list) #mỗi sản phẩm có một list riêng 
  specs: dict[str, str] = Field(default_factory=dict) #mỗi sản phẩm có một dict riêng
  stock: int = 0
  image_url: str = ""
  product_url: str = ""
  description: str = ""

  @field_validator('brand')
  @classmethod
  def sanitize_brand(cls, v: str) -> str:
    # Chuẩn hóa tên brand
    canonical = {
      'hp': 'HP',
      'msi': 'MSI',
      'thinkpad': 'ThinkPad',
      "thinkbook": "ThinkBook",
      "imac": "iMac",
      "macbook": "MacBook"
    }
    v_lower = v.strip().lower()
    return canonical.get(v_lower, v_lower.title())

class RetrievedDoc(BaseModel):
  text: str
  metadata: dict[str, Any]
  score: float = 0.0 #điểm tương đồng vector hoặc điểm BM25 tùy theo ngữ cảnh
  source_type: str = "product" #hoặc "company"

class ChatResponse(BaseModel):
  answer: str
  products: list[dict[str, Any]] = Field(default_factory=list)
  docs: list[RetrievedDoc] = Field(default_factory=list)
  route: str = 'product' # chitchat | company
  retrieval_time_ms: float = 0.0
