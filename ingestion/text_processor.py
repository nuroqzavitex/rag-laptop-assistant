from core.schema import Product
from ingestion.helpers.map_category import map_category

class TextProcessor:
  def product_to_text(self, product: Product) -> str:
    price_formatted = f'{int(product.price):,}'.replace(',', '.')
    category_mapped = map_category(product.category)

    lines = [
      f'Tên sản phẩm: {product.name}',
      f'Thương hiệu: {product.brand}',
      f'Danh mục: {category_mapped}',
      f'Giá: {price_formatted} VNĐ',
      '',
      'Cấu hình:',
      f'  - Bộ xử lí (CPU): {product.specs.cpu}',
      f'  - RAM: {product.specs.ram}',
      f'  - Màn hình: {product.specs.screen}',
      f'  - Card đồ họa (GPU): {product.specs.gpu}'
      f'  - Ổ cứng: {product.specs.storage}',
      '',
      f'Tồn kho: {'Còn hàng (' +str(product.stock) + ' sản phẩm)' if product.is_in_stock else "Hết hàng"}',
      f'Mô tả: {product.description}',
      f'Link sản phẩm: {product.product_url}'
    ]

    return '\n'.join(lines)
  
  def product_to_metadata(self, product: Product) -> dict:
    return {
      'product_id': product.id, 
      'name': product.name,
      'brand': product.brand.lower(),
      'category': product.category.lower(),
      'price': float(product.price),
      'price_range': product.price_range,
      'stock': product.stock,
      'in_stock': product.is_in_stock,
      'cpu': product.specs.cpu.lower(),
      'ram': product.specs.ram.lower(),
      'product_url': product.product_url,
      'image_url': product.image_url
    }
  
  def process_all(self, products: list[Product]) -> tuple[list[str], list[dict], list[str]]:
    texts: list[str] = []
    metadata: list[dict] = []
    ids: list[str] = []

    for product in products:
      texts.append(self.product_to_text(product))
      metadata.append(self.product_to_metadata(product))
      ids.append(product.id)

    return texts, metadata, ids
  
  
  



