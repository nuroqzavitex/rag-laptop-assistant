import os 
from supabase import create_client, Client

API_URL: str = os.getenv('API_URL', 'http://localhost:8000')

SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY: str = os.getenv('SUPABASE_KEY', '')

supabase: Client | None = (
  create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
)
