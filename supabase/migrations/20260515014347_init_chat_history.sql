CREATE TABLE chat_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Tạo Index để tăng tốc độ truy vấn khi lịch sử chat dài ra
CREATE INDEX idx_chat_history_session_id ON chat_history (session_id);
CREATE INDEX idx_chat_history_user_id ON chat_history (user_id);
