import asyncio
import json
import logging
import os
from urllib.parse import urljoin, urlparse

import httpx
import redis
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from app.services.sql_service import generate_sql_and_execute
from app.services.classifier_service import classify_question_type

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
    def build_api_prompt(user_query: str) -> str:
        return f"""
Translate the user's question into a GET API call using only these endpoints:

1. /api/dashboard/pass-fail-trend
2. /api/dashboard/executions-per-project
3. /api/dashboard/average-execution-durations-trend
4. /api/dashboard/test-cases

Rules:
- Always include from_date, to_date, project_name
- Use format YYYY-MM-DD for dates
- Only return the GET line. Nothing else.

Question:
{user_query}
"""

    @staticmethod
    def process_question(task_id: str, question: str):
        try:
            # Classify the question
            question_type = classify_question_type(question)
            logger.info(f"🔍 Detected question type: {question_type}")

            if question_type == "aggregation":
                logger.info(f"💡 Aggregation question detected. Generating SQL for task_id={task_id}")
                result = generate_sql_and_execute(question)
                result["task_id"] = task_id
                result["status"] = "done" if "error" not in result else "error"
                r.set(task_id, json.dumps(result))
                QueryService.push_result(task_id, result)
                return

            # If not aggregation, fall back to API mode
            prompt = QueryService.build_api_prompt(question)
            logger.info(f"📥 Sending prompt to LLM for task_id={task_id}\nPrompt: {prompt.strip()}")
            response = llm.invoke(prompt)

            lines = response.content.strip().splitlines()
            api_line = next((line.strip() for line in lines if line.lower().startswith("get ")), None)

            if not api_line:
                result = {"status": "error", "error": "Invalid LLM response", "task_id": task_id}
                r.set(task_id, json.dumps(result))
                QueryService.push_result(task_id, result)
                return

            try:
                _, path = api_line.split(" ", 1)
            except ValueError:
                result = {"status": "error", "error": "Malformed GET line", "task_id": task_id}
                r.set(task_id, json.dumps(result))
                QueryService.push_result(task_id, result)
                return

            full_url = urljoin(BASE_URL, path.strip())

            if not urlparse(full_url).path.startswith("/api/dashboard"):
                result = {"status": "error", "error": "Invalid endpoint", "task_id": task_id}
                r.set(task_id, json.dumps(result))
                QueryService.push_result(task_id, result)
                return

            with httpx.Client() as client:
                resp = client.get(full_url, timeout=10.0)

            try:
                content_type = resp.headers.get("content-type", "")
                results = resp.json() if content_type.startswith("application/json") else resp.text
            except Exception as e:
                results = f"⚠️ Failed to parse API response: {str(e)}"

            result = {
                "status": "done",
                "task_id": task_id,
                "api_call": api_line,
                "status_code": resp.status_code,
                "results": results
            }
            r.set(task_id, json.dumps(result))

            logger.info("🕒 Waiting briefly to ensure WebSocket registration...")
            asyncio.run(asyncio.sleep(1))  # simple race condition fix

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
