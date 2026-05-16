import streamlit as st
from ui.config import supabase, AUTH_REDIRECT_URL

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

  if supabase is None:
    st.error('Chưa cấu hình SUPABASE_URL và SUPABASE_ANON_KEY trong file .env')
    st.stop()

  if auth_mode == 'Đăng ký':
    if st.button('Tạo tài khoản', use_container_width=True):
      try:
        res = supabase.auth.sign_up({
          'email': email,
          'password': password,
          'options': {'email_redirect_to': AUTH_REDIRECT_URL},
        })
        if res.session:
          st.session_state.auth_token = res.session.access_token
          st.session_state.user_email = email
          st.success('Đăng ký thành công!')
          st.rerun()
        elif res.user:
          # Nếu user.identities rỗng, nghĩa là email đã tồn tại 
          # (do tính năng Email Enumeration Protection của Supabase)
          if res.user.identities is not None and len(res.user.identities) == 0:
            st.error('Email này đã được đăng ký. Vui lòng đăng nhập hoặc sử dụng email khác.')
          else:
            st.success(
              f'Đã gửi email xác nhận tới **{email}**. '
              'Sau khi bấm link trong email, quay lại đây để đăng nhập. '
            )
        else:
          st.warning('Đăng ký chưa hoàn tất. Kiểm tra lại email hoặc thử lại.')
      except Exception as e:
        st.error(f'Lỗi: {e}')
  else:
    if st.button('Đăng nhập', use_container_width=True):
      try:
        res = supabase.auth.sign_in_with_password({'email': email, 'password': password})
        st.session_state.auth_token = res.session.access_token
        st.session_state.user_email = email
        st.rerun() # reload lại để hiển thị giao diện chat
      except Exception as e:
        msg = str(e).lower()
        if 'not confirmed' in msg or 'email not confirmed' in msg:
          st.error('Email chưa được xác nhận. Hãy bấm link trong email trước khi đăng nhập.')
        else:
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