from fastapi import APIRouter
from core.history import check_db_connection

router = APIRouter(tags = ['Health'])

@router.get('/health')
async def health_check():
  db_ok, db_detail = check_db_connection()
  return {
    'status': 'ok' if db_ok else 'degraded',
    'service': 'laptop-chatbot',
    'supabase_history': {'ok': db_ok, 'detail': db_detail},
  }