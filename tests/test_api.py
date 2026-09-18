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

@patch("chatbot.chatbot.chat_stream")
def test_post_chat_stream_endpoint(mock_chat_stream):
  def fake_stream(*args, **kwargs):
    yield {"type": "meta", "route": "chitchat", "products": [], "retrieval_time_ms": 5.0}
    yield {"type": "token", "content": "Xin"}
    yield {"type": "token", "content": " chào!"}
    yield {"type": "done"}

  mock_chat_stream.side_effect = fake_stream

  payload = {
    "message": "Hello streaming",
    "session_id": "test_sess"
  }

  response = client.post("/chat/stream", json=payload)
  assert response.status_code == 200
  assert "text/event-stream" in response.headers.get("content-type", "")
  lines = [line for line in response.text.split("\n") if line.startswith("data: ")]
  assert len(lines) == 4
  assert "meta" in lines[0]
  assert "Xin" in lines[1]
  assert "chào!" in lines[2]
  assert "done" in lines[3]

