from __future__ import annotations
import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=['Auth'])

_STREAMLIT_URL = os.getenv('STREAMLIT_URL', 'http://localhost:8501')

_CONFIRM_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Email đã xác nhận</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 32rem; margin: 4rem auto; padding: 0 1rem; }}
    h1 {{ color: #2e7d32; }}
    a {{ color: #1565c0; }}
  </style>
</head>
<body>
  <h1>Email đã được xác nhận</h1>
  <p>Tài khoản của bạn đã kích hoạt. Quay lại ứng dụng chatbot để đăng nhập.</p>
  <p><a href="{streamlit_url}">Mở ứng dụng chatbot →</a></p>
</body>
</html>
"""

@router.get('/auth/confirm', response_class=HTMLResponse)
async def email_confirm_callback() -> HTMLResponse:
  return HTMLResponse(
    _CONFIRM_HTML.format(streamlit_url=_STREAMLIT_URL)
  )
