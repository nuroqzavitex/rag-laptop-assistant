-- Cho phép API (service_role) và client đã đăng nhập ghi/đọc lịch sử chat
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.chat_history TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.chat_history TO authenticated;

ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_chat_history"
  ON public.chat_history
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "users_own_chat_history"
  ON public.chat_history
  FOR ALL
  TO authenticated
  USING (auth.uid()::text = user_id)
  WITH CHECK (auth.uid()::text = user_id);
