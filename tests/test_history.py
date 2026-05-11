import pytest
from unittest.mock import MagicMock, patch
from core.history import get_history, add_to_history, reset_history

@pytest.fixture
def mock_supabase_client():
  with patch('core.history._get_supabase') as mock_get_supabase:
    mock_client = MagicMock()
    mock_get_supabase.return_value = mock_client

    mock_client.table.return_value = mock_client
    mock_client.select.return_value = mock_client
    mock_client.insert.return_value = mock_client
    mock_client.delete.return_value = mock_client
    mock_client.eq.return_value = mock_client
    mock_client.lt.return_value = mock_client
    mock_client.order.return_value = mock_client
    mock_client.limit.return_value = mock_client
    mock_client.offset.return_value = mock_client

    yield mock_client

def test_get_history_success(mock_supabase_client):
  # Chuẩn bị dữ liệu giả cho phản hồi từ Supabase
  mock_response = MagicMock()
  mock_response.data = [
    {"role": "assistant", "content": "I am fine, thank you!"},
    {"role": "user", "content": "How are you?"}
  ]

  mock_supabase_client.execute.return_value = mock_response

  # Gọi hàm get_history với các tham số giả
  history = get_history(user_id = 'user_123', session_id = 'session_abc', limit = 2)

  # Kiểm tra kết quả trả về
  assert len(history) == 2
  assert history[0]['role'] == 'user'
  assert history[1]['role'] == 'assistant'

  # Kiểm tra các phương thức của Supabase được gọi đúng cách
  mock_supabase_client.table.assert_called_with('chat_history')
  mock_supabase_client.select.assert_called_with("role", "content")
  mock_supabase_client.eq.assert_any_call("user_id", "user_123")
  mock_supabase_client.eq.assert_any_call("session_id", "session_abc")
  mock_supabase_client.execute.assert_called()

def test_add_to_history_no_trimming(mock_supabase_client):
  # Chuẩn bị dữ liệu giả cho phản hồi từ Supabase
  mock_trim_response = MagicMock()
  mock_trim_response.data = []
  mock_supabase_client.execute.return_value = mock_trim_response

  # Gọi hàm add_to_history với các tham số giả
  add_to_history(user_id = 'user_1', session_id = 'session_1', role = 'user', content = 'Hello!')

  # Kiểm tra phương thức insert được gọi đúng cách
  mock_supabase_client.insert.assert_called_with({
    "user_id": "user_1",
    "session_id": "sess_1",
    "role": "user",
    "content": "Hello!"
  })

  # Kiểm tra phương thức delete không được gọi
  mock_supabase_client.delete.assert_not_called()

def test_reset_history(mock_supabase_client):
  # Gọi hàm reset_history với các tham số giả
  reset_history('user_1', 'sess_1')

  # Kiểm tra các phương thức của Supabase được gọi đúng cách
  mock_supabase_client.table.assert_called_with("chat_history")
  mock_supabase_client.delete.assert_called_once()
  mock_supabase_client.eq.assert_any_call("user_id", "user_1")
  mock_supabase_client.eq.assert_any_call("session_id", "sess_1")
  mock_supabase_client.execute.assert_called()
