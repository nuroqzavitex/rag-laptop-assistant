from __future__ import annotations
import os
from qdrant_client import QdrantClient
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

_qdrant_client: QdrantClient | None = None

def _get_client() -> QdrantClient: #singleton pattern để đảm bảo chỉ có một instance QdrantClient được tạo ra trong toàn bộ ứng dụng
  global _qdrant_client
  if _qdrant_client is None:
    if cfg.qdrant.host != 'localhost' or os.getenv('DOCKER_ENV'):
      # Nếu đang chạy trong Docker hoặc trỏ tới server khác thì dùng cấu hình host/port
      _qdrant_client = QdrantClient(host = cfg.qdrant.host, port = cfg.qdrant.port)
      log.info(f'Qdrant client initialized with host: {cfg.qdrant.host}, port: {cfg.qdrant.port}')
    else:
      # Nếu chạy test ở máy cá nhân thì dùng cấu hình ở file local_path
      _qdrant_client = QdrantClient(path = cfg.qdrant.local_path)
      log.info(f'Qdrant client initialized with local path: {cfg.qdrant.local_path}')
  return _qdrant_client