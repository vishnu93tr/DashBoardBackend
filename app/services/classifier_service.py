import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
logger = logging.getLogger(__name__)
llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

AGGREGATION_KEYWORDS = [
    "how many", "count", "average", "sum", "total", "maximum", "minimum", "min", "max", "aggregate", "aggregation"
]
TREND_KEYWORDS = [
    "trend", "over time", "per day", "daily", "weekly", "monthly", "timeline"
]
LISTING_KEYWORDS = [
    "list", "show", "display", "latest", "recent", "top", "failed test cases"
]

def classify_question_type(question: str) -> str:
    question_clean = question.strip()
    logger.info(f"🧠 Classifying question: {question_clean}")

    prompt = f"""
You are a classifier that determines the type of question based on its intent.

Classify the following question into one of these categories:
- aggregation → For questions about counts, averages, totals, min/max, pass rates, percentages, etc.
- trend → For time-based trends like daily, weekly, monthly changes, charts over time, etc.
- listing → For showing raw data like latest test cases, top failed runs, etc.

Respond with only one word: aggregation, trend, or listing.

Question: "{question_clean}"
"""
    try:
        response = llm.invoke(prompt)
        answer = response.content.strip().lower()
        logger.info(f"🤖 LLM classified as: {answer}")
        if answer in {"aggregation", "trend", "listing"}:
            return answer
    except Exception as e:
        logger.warning(f"⚠️ LLM classification failed: {e}")

    q = question_clean.lower()
    if any(kw in q for kw in AGGREGATION_KEYWORDS):
        logger.info("📚 Fallback classification: aggregation (keywords)")
        return "aggregation"
    if any(kw in q for kw in TREND_KEYWORDS):
        logger.info("📚 Fallback classification: trend (keywords)")
        return "trend"
    if any(kw in q for kw in LISTING_KEYWORDS):
        logger.info("📚 Fallback classification: listing (keywords)")
        return "listing"

    logger.info("❓ Fallback classification: unknown")
    return "unknown"
