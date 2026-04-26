from __future__ import annotations
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)
security = HTTPBearer()

_supabase: Client = create_client(cfg.supabase.url, cfg.supabase.key)

async def get_current_user(auth: HTTPAuthorizationCredentials = Security(security)) -> str:
  token = auth.credentials
  try:
    user_res = _supabase.auth.get_user(token)
    if not user_res or not user_res.user:
      raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    return str(user_res.user.id)
  except Exception as e:
    log.error(f'Auth error: {e}')
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")