from __future__ import annotations
import enum
import time
from openai import OpenAI
from config.settings import cfg
from core.logger import get_logger
from core.models import RetrievedDoc

log = get_logger(__name__)

_client: OpenAI | None = None

def _get_client() -> OpenAI:
  global _client
  if _client is None:
    _client = OpenAI(api_key = cfg.openai.api_key)
  return _client

SYSTEM_PROMPT = """Bạn là trợ lý tư vấn bán laptop chuyên nghiệp của cửa hàng Hùng Nhữ Computer.

QUY TẮC:
1. Trả lời bằng tiếng Việt, thân thiện, chuyên nghiệp.
2. CHỈ tư vấn dựa trên thông tin sản phẩm được cung cấp trong context. KHÔNG bịa thông tin.
3. Luôn hiển thị GIÁ và TÌNH TRẠNG KHO (còn hàng/hết hàng) cho mỗi sản phẩm.
4. Nếu sản phẩm hết hàng (stock = 0), thông báo rõ và gợi ý sản phẩm tương tự còn hàng.
5. Format giá tiền theo kiểu Việt Nam (ví dụ: 29.490.000 VNĐ).
6. Khi so sánh sản phẩm, dùng bảng hoặc danh sách rõ ràng.
7. Nếu không tìm thấy sản phẩm phù hợp, nói rõ và hỏi thêm thông tin.
8. Có thể gợi ý thêm sản phẩm nếu phù hợp với nhu cầu người dùng.

FORMAT TRẢ LỜI:
- Dùng emoji phù hợp 💻 🎯 ✅ ❌ 💰
- Hiển thị tên sản phẩm in đậm
- Luôn kèm link sản phẩm nếu có
"""

CONTEXTUALIZE_PROMPT = """Dựa trên lịch sử hội thoại và câu hỏi mới nhất của người dùng, 
vui lòng tạo một câu hỏi ĐỘC LẬP (standalone) có thể hiểu được mà không cần xem lịch sử.

QUY TẮC:
1. KHÔNG trả lời câu hỏi, chỉ viết lại câu hỏi.
2. Nếu câu hỏi đã đủ ý, hãy giữ nguyên.
3. Nếu câu hỏi có các đại từ thay thế (nó, cái này, đó, shop...), hãy thay bằng tên sản phẩm hoặc thực thể tương ứng trong lịch sử.
4. Chỉ liên quan đến laptop hoặc thông tin cửa hàng.

Ví dụ:
Lịch sử: User: "Laptop Asus nào tầm 20tr?" | Assistant: "Có mẫu Vivobook X15..."
Câu hỏi mới: "Nó có card rời không?"
Standalone: "Laptop Asus Vivobook X15 tầm 20tr có card đồ họa rời không?"
"""

def _format_knowledge_context(docs: list[RetrievedDoc]) -> str:
  # format tài liệu tìm được để LLM đọc
  if not docs:
    return 'Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu'
  
  parts = []
  for i, doc in enumerate(docs, 1):
    doc_type = doc.metadata.get('type', 'unknown')

    if doc_type == 'product':
      meta = doc.metadata
      price = meta.get('price', 0)
      stock = meta.get('stock', 0)
      name = meta.get('name', 'N/A')
      price_str = f"{price:,.0f}".replace(',', '.') + ' VNĐ'
      stock_str = f"Còn {stock} sản phẩm" if stock > 0 else "❌ Hết hàng"

      part = f"""
[Sản phẩm {i}]
Tên: {name}
Giá: {price_str} | Tồn kho: {stock_str}
Thông số: CPU {meta.get('cpu', 'N/A')}, RAM {meta.get('ram', 'N/A')}, GPU {meta.get('gpu', 'N/A')}, SSD {meta.get('storage', 'N/A')}
Link: {meta.get('product_url', '')}
"""

    else:
      part = f"""
[Thông tin cửa hàng/Chính sách {i}]
Nội dung: {doc.text}
"""
      
    parts.append(part.strip())
  
  return '\n\n'.join(parts)

def generate_response(query: str, docs: list[RetrievedDoc], chat_history: list[dict[str, str]] | None = None) -> str:
  # Tạo câu trả lời kèm ngữ cảnh 
  client = _get_client()
  context = _format_knowledge_context(docs)

  user_msg = f"""Câu hỏi của khách hàng: {query}

Dữ liệu tìm được (bao gồm sản phẩm và thông tin cửa hàng):
{context}

YÊU CẦU:
1. Trả lời trực tiếp vào nội dung khách hỏi.
2. Nếu chỉ hỏi về sản phẩm, hãy tập trung vào sản phẩm.
3. Nếu chỉ hỏi về shop/chính sách, hãy tập trung vào thông tin đó.
4. Nếu hỏi cả hai hoặc câu hỏi mở, hãy khéo léo kết hợp thông tin một cách tự nhiên.
5. Luôn giữ phong cách thân thiện của Hùng Nhữ Computer.
"""

  # Tạo lịch sử tin nhắn
  messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

  if chat_history:
    for msg in chat_history: 
      messages.append({'role': msg['role'], 'content': msg['content']})
  
  messages.append({'role': 'user', 'content': user_msg})

  # Retry logic
  max_retries = 3
  base_delay = 2

  for attempt in range(max_retries):
    try:
      response = client.chat.completions.create(
        model = cfg.openai.generation_model,
        messages = messages,
        temperature=cfg.openai.temperature,
        max_tokens=cfg.openai.max_tokens
      )
      return response.choices[0].message.content or 'Xin lỗi, tôi không thể tạo câu trả lời lúc này'
    
    except Exception as e:
      error_str = str(e).lower()
      if '429' in error_str or 'rate_limit' in error_str or 'insufficient_quota' in error_str:
        if 'insufficient_quota' in error_str:
          return "Tài khoản OpenAI của bạn hết số dư. Vui lòng nạp thêm tiền để tiếp tục"
        
        if attempt < max_retries - 1:
          delay = base_delay * (2**attempt)
          log.warning(f'OpenAI Rate limit (429). Retrying in {delay}s...(Attempt {attempt+1}/{max_retries})')
          time.sleep(delay)
          continue
      log.error(f'OpenAI Generation error: {e}')
      return f'Xin lỗi, đã có lỗi xảy ra khi tạo câu trả lời qua OpenAI: {e}'
    
  return "Hệ thống OpenAI đang quá tải. Vui lòng thử lại sau giây lát."

def contextualize_query(query: str, chat_history: list[dict[str, str]]) -> str:
  # Viết lại câu hỏi của user cho rõ nghĩa trước khi retrieve, không đưa ra câu trả lời
  if not chat_history:
    return query
  
  client = _get_client()

  history_text = '\n'.join([
    f"{'User' if m['role'] == 'user' else 'Bot'}: {m['content']}"
    for m in chat_history
  ])      

  prompt = f"""Lịch sử hội thoại:
{history_text}

Câu hỏi mới nhất: {query}

Nhiệm vụ: {CONTEXTUALIZE_PROMPT}
"""
  
  # Retry logic
  max_retries = 3
  base_delay = 2

  for attempt in range(max_retries):
    try: 
      response = client.chat.completions.create(
        model = cfg.openai.generation_model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.0,
        max_tokens=256
      )
      standalone = (response.choices[0].message.content or '').strip()
      if standalone:
        log.info(f"Contextualized by OpenAI: '{query}' -> '{standalone}'")
        return standalone
      return query
    
    except Exception as e:
      error_str = str(e).lower()
      if '429' in error_str or 'rate_limit' in error_str:
        if attempt < max_retries - 1:
          delay = base_delay * (2 ** attempt)
          log.warning(f"OpenAI Rate limit in contextualization. Retrying in {delay}s... ({attempt + 1}/{max_retries})")
          time.sleep(delay)
          continue
      log.error(f'OpenAI Contextualization error: {e}')
      return query
  return query