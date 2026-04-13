from __future__ import annotations
import re
from pathlib import Path
from typing import Any
import pdfplumber
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

# Nhận diện được các đề mục được đánh số la mã như I Giới thiệu chung, II Tầm nhìn và sứ mệnh
_ROMAN_HEADING = re.compile(
  r"^(I{1,3}V?|V?I{0,3}|VI{1,3})\s+[A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴa-zđ]",
  re.MULTILINE
)

# Nhận diện các đề mục được đánh số như 1 Laptop Gaming, 2 Laptop Học tập - Văn phòng
_NUM_HEADING = re.compile(
  r"^(\d+)\s+[A-ZĐÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ]",
  re.MULTILINE
)

# Nhận diện số trang xuất hiện độc nhất 1 dòng
_PAGE_NUMBER = re.compile(r'^\d{1, 3}$')

# Các cụm không phải section
_SKIP_HEADINGS = [
  'CÔNG TY TNHH CÔNG NGHỆ',
  'HÙNG NHỮ'
]

def _classify_line(line: str) -> str | None:
  # Xác định 1 dòng bất kì có phải heading không
  stripped = line.strip()
  if not stripped:
    return None
  
  # Trả về None nếu nó nằm trong _SKIP_HEADINGS
  if stripped in _SKIP_HEADINGS:
    return None
  
  # Trả về None nếu nó được nhận diện là số trang
  if _PAGE_NUMBER.match(stripped):
    return None
  
  # Trả về chính nó nếu là đề mục được đánh bằng số la mã
  if _ROMAN_HEADING.match(stripped):
    return ('roman', stripped)
  
  # Trả về chính nó nếu là đề mục được đánh bằng số
  if _NUM_HEADING.match(stripped):
    return ('number', stripped)
  
  return None

def load_pdf_chunk(pdf_path: Path | None = None, max_chunk_size: int = 800)-> list[dict[str, Any]]:
  # Trả về danh sách có dạng {"text": ..., "metadata": {"source": ..., "section": ...}}

  path = pdf_path or cfg.paths.pdf_path
  log.info(f'Loading PDF from {path}')

  pages_text: list[str] = [] # list gồm các trang pdf
  with pdfplumber.open(path) as pdf:
    for page in pdf.pages:
      text = page.extract_text() or ""
      pages_text.append(text)

  full_text = '\n\n'.join(pages_text)
  lines = full_text.split('\n')

  chunks: list[dict[str, Any]] = []
  parent_section = 'Thông tin chung'
  current_section = 'Thông tin chung'
  current_lines: list[str] = []
  current_h_type = 'roman'

  def _flush():
    if not current_lines:
      return
    
    text = '\n'.join(current_lines).strip()
    if text:
      chunks.append({
        'text': text,
        'metadata': {
          'source': path.name,
          'parent_section': parent_section,
          'section': current_section,
          'source_type': 'company'
        }
      })
  
  for line in lines:
    heading_info = _classify_line(line)

    if heading_info is not None: 
      # Nếu có tiêu đề mới thì hoàn thiện chunk trước đó, tạo chunk mới có section mới là heading
      _flush() 
      current_h_type, heading = heading_info
      if current_h_type == 'roman':
        parent_section = heading
        current_section = heading
        current_lines = [heading]
      else: # 'number'
        current_section = heading
        if parent_section != current_section:
          current_lines = [f'{parent_section} - {heading}']
        else:
          current_lines = [heading]
    else:
      # Nếu không phải tiêu đề thì thêm dòng này vào chunk hiện tại
      current_lines.append(line)

    chunk_text = '\n'.join(current_lines)
    if len(chunk_text) > max_chunk_size:
      _flush()
      if current_h_type == 'number' and parent_section != current_section:
        current_lines = [f'{parent_section} - {current_section}']
      else:
        current_lines = [current_section]
 
  _flush() # Lưu lại chunk cuối cùng

  log.info(f'Extracted {len(chunks)} chunks from PDF')
  for c in chunks:
    log.debug(f'Section = {c['metadata']['section']!r} | len = {len(c['text'])}')
  return chunks