from __future__ import annotations
from typing import Optional
from supabase import create_client, Client
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

_supabase: Optional[Client] = None
_db_ok: bool | None = None

def check_db_connection() -> tuple[bool, str]:
  """Verify service key can read/write chat_history."""
  global _db_ok
  client = _get_supabase()
  if not client:
    _db_ok = False
    return False, 'SUPABASE_URL hoặc SUPABASE_SERVICE_KEY chưa được cấu hình'
  try:
    probe_id = '__connection_probe__'
    client.table('chat_history').insert({
      'user_id': probe_id,
      'session_id': 'probe',
      'role': 'user',
      'content': 'probe',
    }).execute()
    client.table('chat_history').delete().eq('user_id', probe_id).execute()
    _db_ok = True
    return True, 'ok'
  except Exception as e:
    _db_ok = False
    msg = str(e)
    if 'Invalid API key' in msg:
      return False, (
        'SUPABASE_SERVICE_KEY không hợp lệ. '
        'Vào Supabase Dashboard → Project Settings → API → copy lại service_role key.'
      )
    return False, msg

def _get_supabase() -> Optional[Client]:
  global _supabase
  if _supabase is None:
    url = cfg.supabase.url
    key = cfg.supabase.key 
    if not url or not key:
      log.warning('Supabase URL or Key not set. History functionality will be disabled.')
      return None
    try:
      _supabase = create_client(url, key)
      log.info('Supabase client initialized successfully.')
    except Exception as e:
      log.error(f'Error initializing Supabase client: {e}')
      return None
  return _supabase

MAX_STORE_MESSAGES = 20 # Số lượng message tối đa được lưu trong lịch sử. Khi vượt quá sẽ xóa bớt message cũ nhất để giữ lại những message gần đây nhất.
DEFAULT_SESSION_ID = 6 # Số lượng message lấy để lấy context

def get_history(user_id: str, session_id: str, limit: int = DEFAULT_SESSION_ID) -> list[dict[str, str]]:
  # Lấy lịch sử chat từ Supabase dựa trên user_id và session_id, giới hạn số lượng message trả về bằng limit
  client = _get_supabase()
  if not client:
    return []
  
  try:
    response = client.table('chat_history') \
      .select('role', 'content') \
      .eq('user_id', user_id) \
      .eq('session_id', session_id) \
      .order('created_at', desc=True) \
      .limit(limit) \
      .execute() # chỉ lấy role và content lọc theo user_id và session_id, sắp xếp theo created_at giảm dần, giới hạn số lượng
    
    messages = response.data[::-1] # đảo lại để có thứ tự thời gian tăng dần
    log.debug(f'Fetched {len(messages)} messages from history for user_id={user_id}, session_id={session_id}')
    return messages
  except Exception as e:
    log.error(f'Error fetching history from Supabase: {e}')
    return []
  
def add_to_history(user_id: str, session_id: str, role: str, content: str) -> None:
  # Thêm message vào Supabase và xóa những tin nhắn cũ
  client = _get_supabase()
  if not client:
    return 
  
  try:
    # 1. Thêm tin nhắn mới
    client.table('chat_history').insert({
      'user_id': user_id,
      'session_id': session_id,
      'role': role,
      'content': content
    }).execute()
    log.debug(f'Saved {role} message to session {session_id}')

    # 2. Xóa tin nhắn cũ nếu vượt quá MAX_STORE_MESSAGES
    response = client.table('chat_history')\
      .select('created_at')\
      .eq('user_id', user_id)\
      .eq('session_id', session_id)\
      .order('created_at', desc=True)\
      .limit(1)\
      .offset(MAX_STORE_MESSAGES - 1)\
      .execute()
    
    if response.data:
      threshold_time = response.data[0]['created_at']
      client.table('chat_history')\
        .delete()\
        .eq('user_id', user_id)\
        .eq('session_id', session_id)\
        .lt('created_at', threshold_time)\
        .execute()
      log.debug(f'Cleaned up old messages in session {session_id} created before {threshold_time}')
  
  except Exception as e:
    global _db_ok
    _db_ok = False
    log.error(f'Không lưu được lịch sử chat vào Supabase: {e}')


def reset_history(user_id: str, session_id: str) -> None:
  # Xóa tất cả message của session_id trong Supabase
  client = _get_supabase()
  if not client:
    return
  
  try:
    client.table('chat_history').delete() \
      .eq('user_id', user_id) \
      .eq('session_id', session_id) \
      .execute()
    log.info(f'Reset history for user_id={user_id}, session_id={session_id}')
  except Exception as e:
    log.error(f'Error resetting history in Supabase: {e}')

  
  
