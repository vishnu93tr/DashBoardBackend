import asyncio
import json
import logging
import os

import redis
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from app.services.sql_service import generate_sql_and_execute

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
task_to_socket = {}  # Maps task_id to websocket
pending_results = {}

class QueryService:
    @staticmethod
    def process_question(task_id: str, question: str):
        try:
             # Generate SQL for all types now
            logger.info(f"💡 Generating SQL for task_id={task_id}")
            result = generate_sql_and_execute(question)
            result["task_id"] = task_id
            result["status"] = "done" if "error" not in result else "error"

            r.set(task_id, json.dumps(result))
            QueryService.push_result(task_id, result)

        except Exception as e:
            result = {"status": "error", "task_id": task_id, "error": str(e)}
            r.set(task_id, json.dumps(result))
            QueryService.push_result(task_id, result)

    @staticmethod
    def push_result(task_id: str, result: dict):
        websocket = task_to_socket.get(task_id)
        logger.info(f"🛰 push_result called for task_id={task_id}")
        logger.info(f"🧠 Is socket present: {'yes' if websocket else 'no'}")

        if websocket:
            try:
                logger.info(f"🔔 Pushing result to WebSocket for task_id={task_id}")
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(websocket.send_json(result))
                else:
                    loop.run_until_complete(websocket.send_json(result))
                task_to_socket.pop(task_id, None)
            except Exception as e:
                logger.error(f"❌ Failed to send result over WebSocket for task_id={task_id}: {e}")
        else:
            logger.info(f"📦 No socket yet, storing pending result for task_id={task_id}")
            pending_results[task_id] = result
