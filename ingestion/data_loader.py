import json
import logging
from pathlib import Path
from core.schema import Product

logger = logging.getLogger('ingestion')

class DataLoader:
  def __init__(self, data_path: str):
    self.data_path = Path(data_path)
    
  def load(self) -> list[Product]:
    if not self.data_path.exists():
      logger.error(f'File not found: {self.data_path}')
      return []
    
    with open(self.data_path, 'r', encoding='utf-8') as f:
      try:
        raw: list[dict] = json.load(f)
      except json.JSONDecodeError as e:
        logger.error(f'Error decoding JSON: {e}')
        return []
      except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return []
      
    products: list[Product] = []
    errors: list[str] = []

    for idx, item in enumerate(raw):
      try:
        product = Product(**item)
        products.append(product)
      except Exception as e:
        error_msg = f'Error parsing item at index {idx}: {e}'
        logger.warning(error_msg)
        errors.append(error_msg)

    if errors:
      logger.info(f'Skipping {len(errors)} items with errors')
      for error in errors:
        logger.debug(error)

    logger.info(f'Successfully loaded {len(products)} products')
    return products
  
  def load_in_stock_only(self) -> list[Product]:
    all_products = self.load()
    in_stock = [product for product in all_products if product.is_in_stock]
    logger.info(f'Filtered to {len(in_stock)}/{len(all_products)} in-stock products')
    return in_stock


