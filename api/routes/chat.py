from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
import json
from chatbot import chatbot
from api.schemas import ChatRequest, ChatResponseModel, ResetRequest
from api.auth import get_current_user
from core.logger import get_logger

router = APIRouter(tags = ['Chat'])
log = get_logger(__name__)

@router.post('/chat', response_model=ChatResponseModel)
async def chat_endpoint(req: ChatRequest, user_id: str = Depends(get_current_user)):
  log.info(f"User {user_id} chat request: '{req.message}' (session: {req.session_id})")
  try:
    response = await run_in_threadpool(chatbot.chat, req.message, user_id, req.session_id)
    return ChatResponseModel(
      answer=response.answer,
      products=response.products,
      route=response.route,
      retrieval_time_ms=response.retrieval_time_ms
    )
  except Exception as e:
    log.error(f'Chat error: {e}')
    raise HTTPException(status_code=500, detail=str(e))

@router.post('/chat/stream')
def chat_stream_endpoint(req: ChatRequest, user_id: str = Depends(get_current_user)):
  log.info(f"User {user_id} chat stream request: '{req.message}' (session: {req.session_id})")
  
  def event_generator():
    try:
      for event in chatbot.chat_stream(req.message, user_id, req.session_id):
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    except Exception as e:
      log.error(f'Chat stream error: {e}')
      yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

  return StreamingResponse(
    event_generator(),
    media_type="text/event-stream",
    headers={
      "Cache-Control": "no-cache",
      "Connection": "keep-alive",
      "X-Accel-Buffering": "no"
    }
  )
  
@router.post('/reset')
async def reset_session(req: ResetRequest, user_id: str = Depends(get_current_user)):
  chatbot.reset_history(user_id, req.session_id)
  return {'status': 'ok', 'message': f"Session '{req.session_id}' reset for user {user_id}."}

@router.get('/history')
async def get_chat_history(session_id: str = 'default', user_id: str = Depends(get_current_user)):
  history = chatbot._get_history(user_id, session_id)
  return {'history': history}