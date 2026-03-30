
"""
LLM integration for docstring content generation.

Responsibilities:
- Generate semantic docstring content ONLY
- Return structured JSON
- Never format docstrings
"""

import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()


def generate_docstring_content(fn: dict) -> dict:
    """
    Generate structured docstring content using LLM.

    Returns dict:
    {
        "summary": str,
        "args": {arg_name: description},
        "returns": str,
        "raises": {ExceptionName: description}
    }
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    llm = ChatGroq(
        model="llama-3.1-8b-instant", # openai/gpt-oss-120b, llama-3.1-8b-instant
        temperature=0.3,
        api_key=api_key
    )

    arg_names = [a["name"] for a in fn.get("args", [])]
    raises = fn.get("raises", [])

    prompt = f"""
Return ONLY valid JSON in this exact format:

{{
  "summary": "1–2 line description of what the function does",
  "args": {{
    "arg_name": "description"
  }},
  "returns": "description of the return value",
  "raises": {{
    "ExceptionName": "reason"
  }}
}}

Rules:
- The summary MUST be written in imperative mood
- Start with the base verb (e.g., Add, Calculate, Normalize, Convert, Fetch, Validate)
- Must and should End with a period.
- Do NOT use third-person verbs (no Adds, Calculates, Returns)
- If the summary violates this rule, rewrite it internally before responding
- Include "raises" ONLY if exceptions actually occur
- If no exceptions occur, return "raises": {{}}
- Do NOT invent exceptions
- Do NOT include markdown
- Do NOT include triple quotes
- JSON must be strictly valid
- Be concise and professional


Function name: {fn["name"]}
Arguments: {arg_names}
Return type: {fn.get("returns")}
Known raises: {raises}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        # 🔒 Safe fallback (single place only)
        return {
            "summary": f"Short description of `{fn['name']}`.",
            "args": {a: "DESCRIPTION" for a in arg_names},
            "returns": "DESCRIPTION",
            "raises": {}
        }

