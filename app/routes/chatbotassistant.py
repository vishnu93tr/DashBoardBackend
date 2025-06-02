import json
import logging as logger
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.chatbotassistant_service import QueryService, r, task_to_socket, pending_results

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
def submit_question(request: QuestionRequest, background_tasks: BackgroundTasks):
    print("🚀 /ask endpoint triggered")
    task_id = str(uuid.uuid4())
    r.set(task_id, json.dumps({"task_id": task_id, "status": "in_progress"}))  # ✅ FIXED
    background_tasks.add_task(QueryService.process_question, task_id, request.question)
    return {"task_id": task_id, "status": "queued"}

@router.get("/result/{task_id}")
def get_result(task_id: str):
    result = r.get(task_id)
    print("🚨 Redis raw result:", result)
    if not result:
        # Task is not yet known to Redis
        return {"task_id": task_id, "status": "in_progress"}

    try:
        parsed_result = json.loads(result)

        # Defensive check if Redis value is malformed
        if not isinstance(parsed_result, dict) or "status" not in parsed_result:
            return {"task_id": task_id, "status": "failed", "error": "Corrupted or invalid result"}

        return parsed_result

    except json.JSONDecodeError:
        # Redis contained a non-JSON string (shouldn’t happen now)
        return {"task_id": task_id, "status": "failed", "error": "Corrupted result"}

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     logger.info(f"🔌 WebSocket accepted from {websocket.client.host}:{websocket.client.port}")
#
#     registered_task_ids = set()
#
#     try:
#         while True:
#             msg = await websocket.receive_json()
#             logger.info(f"📨 Received message: {msg}")
#             task_id = msg.get("task_id")
#
#             if task_id:
#                 # Register the WebSocket for this task ID
#                 task_to_socket[task_id] = websocket
#                 registered_task_ids.add(task_id)
#                 logger.info(f"✅ Subscribed task_id={task_id}")
#
#                 # Check for pending results
#                 if task_id in pending_results:
#                     logger.info(f"🚀 Delivering cached result for task_id={task_id}")
#                     await websocket.send_json(pending_results.pop(task_id))
#
#     except WebSocketDisconnect:
#         logger.warning("❌ WebSocket disconnected")
#         for tid in registered_task_ids:
#             if task_to_socket.get(tid) == websocket:
#                 task_to_socket.pop(tid, None)
#



