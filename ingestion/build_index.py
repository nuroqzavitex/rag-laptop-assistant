from __future__ import annotations
from config.settings import cfg
from core.logger import get_logger
from ingestion.json_loader import load_products
from ingestion.pdf_loader import load_pdf_chunk
from ingestion.processor import process_products
from embedding.embedder import embed_batch
from vector_store import upsert_documents, get_collection_count, delete_collection
import argparse

log = get_logger(__name__)

def build_product_index() -> int:
  # index laptop vào qdrant
  log.info('Building product index')
  products = load_products()
  processed = process_products(products)

  ids = [p[0] for p in processed]
  texts = [p[1] for p in processed]

  metadatas = []
  for p in processed:
    m = p[2]
    m['type'] = 'product'
    metadatas.append(m)
  
  log.info(f'Embedding {len(texts)} product texts')
  embeddings = embed_batch(texts)

  upsert_documents(
    collection_name = cfg.qdrant.knowledge_collection,
    ids = ids,
    texts = texts,
    embeddings=embeddings,
    metadatas=metadatas
  )

  return len(ids)

def build_company_index() -> int:
  # Index pdf vào qdrant
  log.info('Building company info index')
  chunks = load_pdf_chunk()

  if not chunks:
    log.warning('No pdf chunks found, skipping company index')
    return 0
  
  ids = [f'company_{i}' for i in range(len(chunks))]
  texts = [c['text'] for c in chunks]
  metadatas = []

  for c in chunks:
    m = c['metadata']
    m['type'] = 'company'
    metadatas.append(m)

  log.info(f'Embedding {len(texts)} company chunks')  
  embeddings = embed_batch(texts)

  upsert_documents(
    collection_name=cfg.qdrant.knowledge_collection,
    ids = ids,
    texts = texts, 
    embeddings=embeddings,
    metadatas=metadatas
  )

  return len(ids)

def main():
  parser = argparse.ArgumentParser(description='Build Qdrant from json products + PDF company info')
  # Tạo flag --reload để index mới
  parser.add_argument('--reload', action='store_true', help='Delete existing collections before indexing')
  args = parser.parse_args()

  if args.reload:
    log.info('Reload flag detected. Deleting existing collections')
    delete_collection(cfg.qdrant.knowledge_collection)
  else:
    # Kiểm tra collection đã tồn tại chưa, nếu có thì bỏ qua, không cần ingest lại
    existing_count = get_collection_count(cfg.qdrant.knowledge_collection)
    if existing_count > 0:
      log.info(f"Collection '{cfg.qdrant.knowledge_collection}' đã có {existing_count} documents. "
                "Bỏ qua ingestion. Dùng --reload để xây dựng lại từ đầu.")
      return 
  
  log.info('Starting full index build')
  n_products = build_product_index()
  n_company = build_company_index()

  final_count = get_collection_count(cfg.qdrant.knowledge_collection)
  log.info(f"Done! Indexed {n_products} products and {n_company} company chunks. Unified Knowledge Base now has {final_count} documents.")

if __name__ == '__main__':
  main()



