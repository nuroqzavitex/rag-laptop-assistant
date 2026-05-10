from __future__ import annotations
import os
from pathlib import Path
import yaml
from typing import Any
from dotenv import load_dotenv

_BASE_DIR = Path(__file__).parent.parent
_CONFIG_DIR = Path(__file__).resolve().parent / 'settings.yaml'

load_dotenv(_BASE_DIR / '.env')

def _load_yaml() -> dict[str, Any]:
  with open(_CONFIG_DIR, 'r', encoding='utf-8') as f:
    return yaml.safe_load(f)
  
class _Paths:
  def __init__(self, d: dict):
    self.data_dir: Path = (_BASE_DIR / d['data_dir']).resolve()
    self.json_file: str = d['json_file']
    self.pdf_file: str = d['pdf_file']

  @property
  def json_path(self) -> Path:
    return self.data_dir / self.json_file
  
  @property
  def pdf_path(self) -> Path:
    return self.data_dir / self.pdf_file
  
class _Qdrant:
  def __init__(self, d: dict):
    self.host = os.getenv('QDRANT_HOST', d.get('host', 'localhost'))
    self.port = int(os.getenv('QDRANT_PORT', d.get('port', 6333)))
    self.local_path = str((_BASE_DIR / d.get('local_path', './qdrant_data')).resolve())
    self.knowledge_collection = d.get('knowledge_collection', 'laptop_knowledge_base')
    self.product_collection = d.get('product_collection', '')
    self.company_collection = d.get('company_collection', '')
    self.vector_size = d.get('vector_size', 3072)

class _Gemini:
  def __init__(self, d:dict):
    self.api_key = os.getenv('GEMINI_API_KEY', '')
    self.embedding_model = d['embedding_model']
    self.generation_model = d['generation_model']
    self.temperature = d['temperature']
    self.max_output_tokens = d['max_output_tokens']

class _OpenAI:
  def __init__(self, d:dict):
    self.api_key = os.getenv('OPENAI_API_KEY', '')
    self.embedding_model = d['embedding_model']
    self.generation_model = d['generation_model']
    self.temperature = d['temperature']
    self.max_tokens = d['max_tokens']

class _Retrieval: 
  def __init__(self, d:dict):
    self.top_k = d.get('top_k', 10)
    self.final_top_k = d.get('final_top_k', 5)
    self.similarity_threshold = d.get('similarity_threshold', 0.3)
    self.hybrid_alpha = d.get('hybrid_alpha', 0.6)

class _Server:
  def __init__(self, d:dict):
    self.host = d.get('host', '0.0.0.0')
    self.port = d.get('port', 8000)

class _Supabase:
  def __init__(self, d: dict):
    self.url = os.getenv('SUPABASE_URL', d.get('url', ''))
    self.key = os.getenv('SUPABASE_KEY', d.get('key', ''))

class Config:
  def __init__(self):
    raw = _load_yaml()
    self.paths = _Paths(raw["paths"])
    self.qdrant = _Qdrant(raw["qdrant"])
    self.gemini = _Gemini(raw["gemini"])
    self.openai = _OpenAI(raw["openai"])
    self.retrieval = _Retrieval(raw["retrieval"])
    self.server = _Server(raw["server"])
    self.supabase = _Supabase(raw.get("supabase", {}))

cfg = Config()

  
