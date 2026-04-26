from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
  message: str = Field(..., min_length=1, max_length=1000, description='User message')
  session_id: str = Field(default='default', description='Session ID for chat history')

class ChatResponseModel(BaseModel):
  answer: str
  products: list[dict[str, Any]] = []
  route: str
  retrieval_time_ms: float

class ResetRequest(BaseModel):
  session_id: str = 'default'

class UpdatePriceRequest(BaseModel):
  product_id: str = Field(..., description='Product ID, e.g. PROD_001')
  new_price: float = Field(..., gt=0, description='New price in VNĐ')

class UpdateStockRequest(BaseModel):
  product_id: str = Field(..., description='Product ID, e.g. PROD_001')
  new_stock: int = Field(..., ge=0, description='New stock quantity')

class BatchUpdatePriceRequest(BaseModel):
  updates: dict[str, int] = Field(..., description='Mapping of product_id -> new_price')

class BatchUpdateStockRequest(BaseModel):
  updates: dict[str, int] = Field(..., description='Mapping of product_id -> new_stock')

class AddProductRequest(BaseModel):
  id: Optional[str] = Field(None, description='Product ID, e.g. PROD_001. If not provided, will auto-generate')
  name: str = Field(..., description='Product name')
  brand: str = Field(..., description='Brand name')
  price: int = Field(..., gt=0, description='Price in VNĐ')
  currency: str = Field(default='VNĐ')
  category: list[str] = Field(default_factory=list, description='Category list')
  specs: dict[str, str] = Field(default_factory=dict, description='Product specs')
  stock: int = Field(default=0, ge=0)
  image_url: str = Field(default='')
  product_url: str = Field(default='')
  description: str = Field(default='')