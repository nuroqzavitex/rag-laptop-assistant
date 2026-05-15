from __future__ import annotations
import re
from typing import Any
from core.logger import get_logger

log = get_logger(__name__)

BRAND_MAP = {
    "lenovo": "Lenovo",
    "asus": "Asus",
    "dell": "Dell",
    "hp": "HP",
    "acer": "Acer",
    "msi": "MSI",
    "thinkpad": "ThinkPad",
    "thinkbook": "ThinkBook",
    "macbook": "MacBook",
    "apple": "Apple",
    "imac": "iMac",
    "gigabyte": "Gigabyte",
    "razer": "Razer",
}

CATEGORIES = {
    "gaming": ["gaming", "game", "chơi game"],
    "dohoa": ["đồ họa", "đồ hoạ", "thiết kế", "design", "render", "sáng tạo", "creative"],
    "laptrinh": ["lập trình", "code", "coding", "developer", "programming", "IT"],
    "hoctap_vanphong": ["văn phòng", "học tập", "office", "sinh viên", "học sinh", "nhẹ"],
}

GPU_KEYWORDS = [
    "rtx 5090", "rtx 5080", "rtx 5070ti", "rtx 5070",
    "rtx 5060", "rtx 5050", "rtx 4060", "rtx 4050",
    "rtx 3050", "rtx 3500",
]

CPU_KEYWORDS = [
    "core i9", "core i7", "core i5", "core i3",
    "ultra 9", "ultra 7", "ultra 5",
    "ryzen 9", "ryzen 7", "ryzen 5", "ryzen 3",
    "m4", "m3", "m2", "m1",
    "i9", "i7", "i5", "i3"
]

PRICE_PATTERNS = [
    # "từ 20 đến 30 triệu" / "20-30 triệu"
    (re.compile(r"(?:từ\s*)?(\d+(?:[.,]\d+)?)\s*(?:[-–đến tới]+)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|m)", re.I), "range"),
    # "dưới 30 triệu" / "< 30tr"
    (re.compile(r"(?:dưới|under|<)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|m)", re.I), "max"),
    # "trên 50 triệu" / "> 50tr"
    (re.compile(r"(?:trên|trở lên|above|>)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|m)", re.I), "min"),
    # "tầm 30 triệu" / "khoảng 30 triệu"
    (re.compile(r"(?:tầm|khoảng|around|about)\s*(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|m)", re.I), "around"),
    # Bare mentions: "laptop 30tr" / "dell 15.5m"
    (re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:triệu|tr|m)", re.I), "around"),
]

def _normalize_price(val_str: str) -> int:
  val = float(val_str.replace(',', '.'))
  return int(val * 1_000_000)

RAM_PATTERN = re.compile(r"(\d+)\s*(?:gb|GB)\s*(?:ram|RAM)?", re.I)
STORAGE_PATTERN = re.compile(r"(?:ssd\s*)?(\d+)\s*(?:tb|TB)", re.I)

COMPANY_KEYWORDS = [
  "shop", "cửa hàng", "cua hang", "địa chỉ", "dia chi", "showroom",
  "bảo hành", "bao hanh", "chính sách", "chinh sach",
  "ship", "giao hàng", "giao hang", "vận chuyển", "van chuyen",
  "liên hệ", "lien he", "hotline", "số điện thoại", "so dien thoai",
  "giờ mở cửa", "gio mo cua", "mở cửa", "mo cua",
  "trả góp", "tra gop", "đổi trả", "doi tra",
  "công ty", "cong ty",
]

_PRODUCT_INTENT_KEYS = frozenset({
  "brand", "category", "price_min", "price_max", "gpu", "cpu", "ram_size", "storage_tb",
})

def is_company_query(query: str) -> bool:
  q = query.lower()
  if not any(kw in q for kw in COMPANY_KEYWORDS):
    return False
  intent = parse_intent(query)
  if any(k in intent for k in _PRODUCT_INTENT_KEYS):
    return False
  return True

def parse_intent(query: str) -> dict[str, Any]:
  # Trả về dict chứa các thông tin đã trích xuất được từ user, ví dụ {'brand': 'asus', 'price_max': 2000000}
  q = query.lower()
  intent: dict[str, Any] = {}

  # Brand
  for keyword, canonical in BRAND_MAP.items():
    if keyword in q:
      intent['brand'] = canonical
      break
  
  # Category
  for cat_key, keywords in CATEGORIES.items():
    for kw in keywords:
      if kw in q:
        intent['category'] = cat_key
        break
    if 'category' in intent:
      break

  # Price
  for pattern, ptype in PRICE_PATTERNS:
    match = pattern.search(q)
    # match.group(n) lấy ra phần nằm trong dấu ngoặc () thứ n trong regex, bỏ qua những dấu ngoặc có dạng (?:...)
    if match:
      if ptype == 'max':
        intent['price_max'] = _normalize_price(match.group(1))
      elif ptype == 'min':
        intent['price_min'] = _normalize_price(match.group(1))
      elif ptype == 'range':
        intent['price_min'] = _normalize_price(match.group(1))
        intent['price_max'] = _normalize_price(match.group(2))
      elif ptype == 'around': # user tìm sản phẩm tầm 20tr thì lấy min là 16tr và max là 24tr
        val = _normalize_price(match.group(1))
        intent['price_min'] = int(val*0.8)
        intent['price_max'] = int(val*1.2)
      break

  # GPU
  for gpu in GPU_KEYWORDS:
    if gpu in q:
      intent['gpu'] = gpu.upper()
      break

  # CPU
  for cpu in CPU_KEYWORDS:
    if cpu in q:
      intent['cpu'] = cpu
      break

  # RAM
  ram_match = RAM_PATTERN.search(query)
  if ram_match:
    intent['ram_size'] = int(ram_match.group(1))

  # Storage
  storage_match = STORAGE_PATTERN.search(query)
  if storage_match:
    intent['storage_tb'] = int(storage_match.group(1))

  log.info(f'Parsed intent: {intent}')
  return intent


  
  

