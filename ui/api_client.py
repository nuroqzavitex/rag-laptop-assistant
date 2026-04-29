import requests
from ui.config import API_URL
import streamlit as st

def post_chat(session_id: str, message: str, token: str) -> dict:
  # Gửi tin nhắn đến API và nhận phản hồi
  headers = {'Authorization': f'Bearer {token}'}
  resp = requests.post(
    f'{API_URL}/chat',
    json={'message': message, 'session_id': session_id},
    headers = headers,
    timeout=60
  )
  resp.raise_for_status()
  return resp.json()

def post_reset(session_id: str, token: str) -> dict:
  # Gọi API để reset session
  try:
    headers = {'Authorization': f'Bearer {token}'}
    requests.post(
      f'{API_URL}/reset',
      json = {'session_id': session_id},
      headers = headers,
      timeout = 5
    )
  except Exception:
    pass # Không làm gián đoạn trải nghiệm người dùng nếu reset thất bại

def get_stats() -> dict:
  # Lấy thống kê từ API
  try:
    resp = requests.get(f'{API_URL}/stats', timeout=3)
    return resp.json()
  except Exception:
    return None # Trả về None nếu không lấy được stats

def get_history(session_id: str, token: str) -> dict:
  # Lấy lịch sử chat từ API
  try:
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(
      f'{API_URL}/history',
      params={'session_id': session_id},
      headers = headers,
      timeout = 10
    )
    resp.raise_for_status()
    return resp.json().get('history', [])
  except Exception as e:
    st.error(f'Lỗi khi lấy lịch sử: {e}')
    return []