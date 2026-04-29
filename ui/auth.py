import streamlit as st
from ui.config import supabase

def init_session_state() -> None: 
  # Khởi tạo session state để lưu trữ thông tin đăng nhập, lịch sử tin nhắn và session_id
  if 'session_id' not in st.session_state:
    st.session_state.session_id = 'default'
  if 'messages' not in st.session_state:
    st.session_state.messages = []
  if 'auth_token' not in st.session_state: # Khởi tạo auth_token để lưu token đăng nhập, user_email để lưu email người dùng
    st.session_state.auth_token = None
  if 'user_email' not in st.session_state:
    st.session_state.user_email = None

def render_auth_form() -> None:
  # Hiển thị form đăng nhập hoặc đăng ký nếu chưa có token, ngược lại hiển thị thông tin người dùng và nút đăng xuất
  st.subheader("Đăng nhập") 
  auth_mode = st.radio(
    'Chế độ',
    ['Đăng nhập', 'Đăng ký'],
    horizontal=True,
    label_visibility='collapsed'
  )

  email = st.text_input('Email')
  password = st.text_input('Mật khẩu', type='password')

  if auth_mode == 'Đăng ký':
    if st.button('Tạo tài khoản', use_container_width=True):
      try:
        supabase.auth.sign_up({'email': email, 'password': password})
        st.success('Đã gửi email xác nhận!')
      except Exception as e:
        st.error(f'Lỗi: {e}')
  else:
    if st.button('Đăng nhập', use_container_width=True):
      try:
        res = supabase.auth.sign_in_with_password({'email': email, 'password': password})
        st.session_state.auth_token = res.session.access_token
        st.session_state.user_email = email
        st.rerun() # reload lại để hiển thị giao diện chat
      except Exception:
        st.error('Sai email hoặc mật khẩu')
  st.stop()

def render_user_info() -> None:
  # Hiển thị thông tin người dùng và nút đăng xuất
  st.success(f'Chào, **{st.session_state.user_email}**!')
  if st.button('Đăng xuất', use_container_width=True):
    st.session_state.auth_token = None
    st.session_state.user_email = None
    st.session_state.messages = []
    st.rerun()