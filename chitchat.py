from __future__ import annotations
from openai import OpenAI
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

_client: OpenAI | None = None

def _get_client() -> OpenAI:
  global _client
  if _client is None:
    _client = OpenAI(api_key=cfg.openai.api_key)
  return _client

CHITCHAT_SYSTEM = """Bạn là trợ lý tư vấn laptop thân thiện của cửa hàng Trung Trần Computer.

QUY TẮC:
1. Trả lời ngắn gọn, vui vẻ, thân thiện.
2. Luôn hướng cuộc trò chuyện về laptop nếu có thể.
3. Giới thiệu rằng bạn có thể giúp tư vấn laptop gaming, đồ họa, lập trình, văn phòng.
4. Nếu người dùng chào hỏi, chào lại và hỏi họ cần tư vấn laptop gì.
5. Trả lời bằng tiếng Việt.
"""

def handle_chitchat(query: str, chat_history: list[dict[str, str]] | None = None) -> str:
  client = _get_client()

  messages = [{'role': 'system', 'content': CHITCHAT_SYSTEM}]

  if chat_history:
    for msg in chat_history[-4:]: # Lấy 4 tin nhắn gần nhất
      messages.append({'role': msg['role'], 'content': msg['content']})
  
  messages.append({'role': 'user', 'content': query})

  try:
    response = client.chat.completions.create(
      model=cfg.openai.generation_model,
      messages=messages,
      temperature=0.9,
      max_tokens=512
    )
    return response.choices[0].message.content or "Xin chào! Tôi có thể giúp gì cho bạn về laptop?"
  except Exception as e:
    log.error(f'Chitchat error: {e}')
    return 'Xin chào! Bạn cần tư vấn laptop gì ạ?'
