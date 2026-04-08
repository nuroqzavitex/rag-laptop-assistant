from __future__ import annotations
from typing import Any
from core.models import Product
from core.logger import get_logger

log = get_logger(__name__)

CATEGORY_LABELS = {
  'gaming': 'Gaming',
  'dohoa': "Đồ họa / Sáng tạo",
  'laptrinh': "Lập trình",
  'hoctap_vanphong': 'Học tập / Văn phòng'
}

def product_to_text(product: Product) -> str:
  specs = product.specs
  cats = ', '.join(CATEGORY_LABELS.get(c, c) for c in product.category) # map danh mục đã định nghĩa ở trên

  parts = [
    f'Tên: {product.name}',
    f'Hãng: {product.brand}',
    f'CPU: {specs.get('cpu', 'N/A')}',
    f'RAM: {specs.get('ram', 'N/A')}',
    f'GPU: {specs.get('gpu', 'N/A')}',
    f'Màn hình: {specs.get('screen', 'N/A')}',
    f'Ổ cứng: {specs.get('storage', 'N/A')}',
    f'Danh mục: {cats}',
    f'Mô tả: {product.description}'
  ]
  return ' | '.join(parts)

def product_to_metadata(product: Product) -> dict[str, Any]:
  return {
    'product_id': product.id,
    'brand': product.brand,
    'price': product.price,
    'stock': product.stock,
    'category': product.category,
    'cpu': product.specs.get('cpu', ''),
    'ram': product.specs.get('ram', ''),
    'screen': product.specs.get('screen', ''),
    'storage': product.specs.get('storage', ''),
    'image_url': product.image_url,
    'product_url': product.product_url,
    'name': product.name,
    'source_type': 'product'
  }

def process_products(products: list[Product]) -> list[tuple[str, str, dict[str, Any]]]:
  # Mỗi phần tử gồm id: str, text: str, metadata: dict
  results: list[tuple[str, str, dict[str, Any]]] = []
  for p in products:
    text = product_to_text(p)
    meta = product_to_metadata(p)
    results.append(p.id, text, meta)
  
  log.info(f'Processed {len(results)} products to text + metadata')
  return results
