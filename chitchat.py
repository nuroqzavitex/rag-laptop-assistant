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

CHITCHAT_SYSTEM = """Bạn là một trợ lý ảo thông minh, thân thiện và hài hước của cửa hàng Hùng Nhữ Computer.

QUY TẮC:
1. Trò chuyện một cách tự nhiên, gần gũi, thoải mái như một người bạn. Không cần lúc nào cũng cứng nhắc nhắc lại mình là "bot tư vấn".
2. Nếu người dùng chỉ muốn trò chuyện vui vẻ, hỏi thăm hay nói chuyện phiếm, hãy đáp lại nhiệt tình và duyên dáng.
3. Chỉ khéo léo giới thiệu rằng bạn có thể hỗ trợ tư vấn laptop (gaming, đồ họa, lập trình, văn phòng...) khi ngữ cảnh phù hợp, KHÔNG ép buộc mọi câu chuyện đều phải lập tức xoay quanh laptop.
4. Trả lời ngắn gọn, súc tích, có thể dùng emoji để thêm phần sinh động 😊✨.
5. Luôn phản hồi bằng tiếng Việt.
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
