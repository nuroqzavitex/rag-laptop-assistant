from __future__ import annotations
from typing import Any, Optional
from core.logger import get_logger
import re

log = get_logger(__name__)

def build_where_clause(intent: dict[str, Any]) -> Optional[dict[str, Any]]:
  """
  Nhận intent từ intent_parser
  -> tạo json như ví dụ {"$and": [{"brand": {"$eq": "MacBook"}}, {"price": {"$lte": 30000000}}]} 
  -> đưa vào store/filters.py -> dịch sang dạng filter của Qdrant 
  """
  conditions: list[dict[str, Any]] = []

  # Brand
  if 'brand' in intent:
    conditions.append({'brand': {'$eq': intent['brand']}})
  
  # Category
  if 'category' in intent:
    conditions.append({
      'category': {'$contains': intent['category']}
    })

  # Price filters
  if 'price_min' in intent:
    conditions.append({'price': {'$gte': intent['price_min']}})
  if 'price_max' in intent:
    conditions.append({'price': {'$lte': intent['price_max']}})
  
  if not conditions:
    return None
  
  if len(conditions) == 1:
    return conditions[0]
  
  return {'$and': conditions} 
  
def build_metadata_filter(intent: dict[str, Any]) -> dict[str, Any]:
  # Tạo metadata filter từ intent về gpu, ram, storage
  filters = {}
  if 'gpu' in intent:
    filters['gpu_keyword'] = intent['gpu']
  if 'cpu' in intent:
    filters['cpu_keyword'] = intent['cpu']
  if 'ram_size' in intent:
    filters['ram_size'] = intent['ram_size']
  if 'storage_tb' in intent:
    filters['storage_tb'] = intent['storage_tb']
  return filters

def post_filter_results(results: list[dict[str, Any]], meta_filter: dict[str, Any]) -> list[dict[str, Any]]:
  # results gồm các sản phẩm sau khi search từ qdrant db (qua qdrant_filter và top_k), meta_filter gồm filter về gpu, ram, storage -> kiểm tra các sản phẩm trong results đã khớp meta_filter -> trả về sản phẩm khớp
  if not meta_filter:
    return results
  
  filtered = []
  for r in results:
    meta = r.get('metadata', {})
    match = True

    if 'gpu_keyword' in meta_filter:
      gpu = meta.get('gpu', '').upper()
      if meta_filter['gpu_keyword'] not in gpu:
        match = False
    
    if 'cpu_keyword' in meta_filter:
      cpu = meta.get('cpu', '').lower()
      if meta_filter['cpu_keyword'] not in cpu:
        match = False
 
    if 'ram_size' in meta_filter:
      ram_str = meta.get('ram', '')
      ram_nums = re.findall(r'(\d+)\s*GB', ram_str, re.I)
      if ram_nums:
        if int(ram_nums[0]) < meta_filter['ram_size']:
          match = False

    if 'storage_tb' in meta_filter:
      storage_str = meta.get('storage', '')
      target_gb = meta_filter['storage_tb'] * 1024
      
      prod_gb = None
      tb_match = re.search(r'(\d+(?:\.\d+)?)\s*TB', storage_str, re.I)
      if tb_match:
        prod_gb = int(float(tb_match.group(1)) * 1024)
      else:
        gb_match = re.search(r'(\d+)\s*GB', storage_str, re.I)
        if gb_match:
          prod_gb = int(gb_match.group(1))
          
      if prod_gb is not None:
        if prod_gb < target_gb:
          match = False
    
    if match:
      filtered.append(r)
    
  log.info(f'Post-filter: {len(results)} -> {len(filtered)} results')
  return filtered if filtered else results





   