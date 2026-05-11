import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Phải mock supabase.create_client trước khi import app vì api.auth khởi tạo supabase ngay khi module được load
with patch("supabase.create_client"):
  from api.main import app

from api.auth import get_current_user

# Mock authentication dependency
app.dependency_overrides[get_current_user] = lambda: "test_user_id"

client = TestClient(app)

def test_api_health_check():
  # Kiểm tra health endpoint  
  response = client.get("/health") 
  assert response.status_code == 200

@patch("chatbot.chatbot.chat")
def test_post_chat_endpoint(mock_chat):
  # Setup mock response
  mock_chat.return_value = MagicMock(
    answer="Chào bạn, tôi có thể giúp gì?",
    products=[],
    route="chitchat",
    retrieval_time_ms=10.5
  )
  
  payload = {
    "message": "Hello chatbot",
    "session_id": "test_sess"
  }
  
  response = client.post("/chat", json=payload)

  assert response.status_code == 200
  data = response.json()
  assert "answer" in data
  assert data["answer"] == "Chào bạn, tôi có thể giúp gì?"
