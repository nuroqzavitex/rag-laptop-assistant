def map_category(category: str)->str:
  mapping = {
    'hoctap_vanphong': 'Học tập / Văn phòng',
    'gaming': 'Gaming', 
    'dohoa': 'Đồ họa',
    'laptrinh': 'Lập trình'
  }
  return mapping.get(category.lower(), category)