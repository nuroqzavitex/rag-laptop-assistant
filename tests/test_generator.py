import pytest
from core.models import RetrievedDoc
from llm.generator import _format_knowledge_context

def test_format_knowledge_context_empty():
    assert "Không tìm thấy thông tin phù hợp" in _format_knowledge_context([])

def test_format_knowledge_context_product():
  docs = [
    RetrievedDoc(
      text="Laptop Dell XPS",
      metadata={
        "type": "product",
        "name": "Dell XPS 13",
        "price": 25000000,
        "stock": 5,
        "cpu": "i5",
        "ram": "16GB",
        "gpu": "Iris Xe",
        "storage": "512GB",
        "product_url": "http://example.com"
      }
    )
  ]
    
  context = _format_knowledge_context(docs)
  assert "[Sản phẩm 1]" in context
  assert "Dell XPS 13" in context
  assert "25.000.000 VNĐ" in context
  assert "Còn 5 sản phẩm" in context

def test_format_knowledge_context_mixed():
  docs = [
    RetrievedDoc(
      text="Info về shop",
      metadata={"type": "company"}
    ),
    RetrievedDoc(
      text="Product info",
      metadata={"type": "product", "name": "Macbook", "price": 30000000}
    )
  ]
    
  context = _format_knowledge_context(docs)
  assert "[Thông tin cửa hàng/Chính sách 1]" in context
  assert "[Sản phẩm 2]" in context
  assert "Macbook" in context
