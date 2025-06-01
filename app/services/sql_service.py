import logging
import os

from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from sqlalchemy import text, inspect

from app.database import engine, table_names

logger = logging.getLogger(__name__)
llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

# Restrict LLM to only the tables you want
db = SQLDatabase(engine=engine, include_tables=table_names)

def get_table_and_column_info():
    inspector = inspect(engine)
    info = ""
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        column_names = [col["name"] for col in columns]
        info += f"Table: {table_name}\nColumns: {', '.join(column_names)}\n\n"
    return info.strip()

def generate_sql_and_execute(user_query: str) -> dict:
    try:
        schema_info = get_table_and_column_info()

        prompt = f"""
You are an expert PostgreSQL query generator.

Use ONLY the following schema and the examples below to answer the user query. DO NOT use JOINs unless absolutely required. Prefer subqueries with `IN` or `=` when dealing with foreign keys.

### Schema:

Table: projects
- id (int)
- name (string)

Table: executions
- id (int)
- project_id (int) → references projects.id
- executed_at (datetime)
- triggered_by (string)

Table: test_cases
- id (int)
- execution_id (int) → references executions.id
- name (string)
- status (string: 'passed' or 'failed')
- duration_seconds (float)
- error_message (text)

### Examples:

Q: How many test cases failed last week in Project Alpha?
SQL:
SELECT COUNT(*) AS failed_count
FROM test_cases
WHERE status = 'failed'
  AND execution_id IN (
    SELECT id FROM executions
    WHERE project_id = (
      SELECT id FROM projects WHERE name = 'Project Alpha'
    )
    AND executed_at >= CURRENT_DATE - INTERVAL '7 days'
  );

---

Q: What is the average duration of passed test cases in the last execution of Project Alpha?
SQL:
SELECT AVG(duration_seconds) AS avg_duration
FROM test_cases
WHERE status = 'passed'
  AND execution_id = (
    SELECT id FROM executions
    WHERE project_id = (SELECT id FROM projects WHERE name = 'Project Alpha')
    ORDER BY executed_at DESC
    LIMIT 1
  );

---

Q: Give the total number of executions in the last 30 days for Project Beta.
SQL:
SELECT COUNT(*) AS execution_count
FROM executions
WHERE project_id = (
    SELECT id FROM projects WHERE name = 'Project Beta'
)
AND executed_at >= CURRENT_DATE - INTERVAL '30 days';

---

Q: List the top 5 failed test cases from the most recent execution of Project Alpha.
SQL:
SELECT name, error_message, duration_seconds
FROM test_cases
WHERE status = 'failed'
  AND execution_id = (
    SELECT id FROM executions
    WHERE project_id = (SELECT id FROM projects WHERE name = 'Project Alpha')
    ORDER BY executed_at DESC
    LIMIT 1
  )
ORDER BY duration_seconds DESC
LIMIT 5;

---

User Question:
{user_query}

Respond with only the SQL query. Do not add any comments or explanations.
"""

        logger.info("📥 Sending SQL prompt to LLM")
        response = llm.invoke(prompt)
        generated_sql = response.content.strip()
        logger.info(f"🧠 Generated SQL:\n{generated_sql}")

        with engine.connect() as conn:
            result = conn.execute(text(generated_sql))
            rows = [dict(row._mapping) for row in result]
            return {"sql": generated_sql, "results": rows}

    except Exception as e:
        logger.error(f"❌ SQLService error: {e}")
        return {"error": str(e)}
