import os 
from supabase import create_client, Client

API_URL: str = os.getenv('API_URL', 'http://localhost:8000')
AUTH_REDIRECT_URL: str = os.getenv('AUTH_REDIRECT_URL', 'http://localhost:8000/auth/confirm')

SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
# UI auth: anon key. Fallback SUPABASE_KEY for backward compatibility.
SUPABASE_KEY: str = os.getenv(
  'SUPABASE_ANON_KEY',
  os.getenv('SUPABASE_KEY', ''),
)

supabase: Client | None = (
  create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
)
