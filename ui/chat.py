import streamlit as st
from ui.api_client import post_chat
import requests as _req

def get_route_badge(route: str) -> str:
  # Trả về badge tương ứng với route
  badges = {
    "rag":      '<span class="route-badge route-product"> Tìm kiếm</span>',
    "product":  '<span class="route-badge route-product"> Sản phẩm</span>',
    "chitchat": '<span class="route-badge route-chitchat"> Chitchat</span>',
    "company":  '<span class="route-badge route-company"> Công ty</span>',
  }
  return badges.get(route, '')

def render_product_card(prod: dict) -> None:
  # Tạo card hiển thị thông tin sản phẩm gồm ảnh, tên, giá, tồn kho và link
  col1, col2 = st.columns([1, 3]) # chia thành 2 cột với tỉ lệ 1:3
  with col1: # nếu có ảnh thì hiển thị, nếu không có thì để trống
    if prod.get('image_url'):
      st.image(prod['image_url'], width = 120)
  with col2: # hiển thị tên sản phẩm, giá và tồn kho
    price = prod.get('price', 0)
    price_str = f'{price:,.0f}'.replace(',', '.') + 'VNĐ'
    stock = prod.get('stock', 0)
    stock_str = f'Còn {stock} sản phẩm' if stock > 0 else 'Hết hàng'

    st.markdown(f'**{prod.get('name', 'N/A')}**')
    st.markdown(f'{price_str} | {stock_str}')
    if prod.get('product_url'):
      st.markdown(f'[Xem chi tiết]({prod['product_url']})')
  st.divider() # Tạo đường kẻ ngang để phân cách giữa các sản phẩm

def render_message_history() -> None:
  # Hiển thị lịch sử tin nhắn đã lưu trong session_state.messages
  for msg in st.session_state.messages:
    with st.chat_message(msg['role']): # phân biệt tin nhắn của user và assistant để căn lề trái phải
      if msg['role'] == 'assistant' and 'route' in msg: # nếu là tin nhắn của assistant và có route thì hiển thị badge
        st.markdown(get_route_badge(msg['route']), unsafe_allow_html = True)
      st.markdown(msg['content'])

      if msg['role'] == 'assistant' and msg.get('products'): # nếu tin nhắn có chứa sản phẩm thì hiển thị phần mở rộng để xem chi tiết sản phẩm
        with st.expander(
          f'Xem {len(msg['products'])} sản phẩm tìm được', expanded = False
        ):
          for prod in msg['products']:
            render_product_card(prod)

def render_chat_input() -> None:
  # Xử lí chat input, gọi API và lưu tin nhắn vào session_state
  if prompt := st.chat_input('Nhập câu hỏi về laptop...'):
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
      st.markdown(prompt)
    
    with st.chat_message('assistant'):
      with st.spinner('Đang tư vấn...'):
        try:
          resp = post_chat(
            session_id=st.session_state.session_id,
            message=prompt,
            token = st.session_state.token
          )

          route = resp.get('route', 'product')
          answer = resp.get('answer', 'Xin lỗi, tôi không có câu trả lời cho câu hỏi này.')
          products = resp.get('products', [])
          elapsed = resp.get('retrieval_time_ms', 0)

          st.markdown(get_route_badge(route), unsafe_allow_html=True)
          st.markdown(answer)

          if products:
            with st.expander(
              f'Xem {len(products)} sản phẩm tìm được', expanded = False
            ):
              for prod in products:
                render_product_card(prod)
          st.caption(f'{elapsed:.0f} ms | Route: {route}')

          st.session_state.messages.append(
            {
              'role': 'assistant',
              'content': answer,
              'route': route,
              'products': products
            }
          )
        
        except Exception as e:
          if isinstance(e, _req.exceptions.ConnectionError):
            st.error('Không thể kết nối đến API. Hãy chạy API server trước')
            st.code('uvicorn api.main:app --reload')
          else:
            st.error(f'Lỗi: {e}')