import json

from ..llm import get_llm

PROMPT = """You are the planner for a decision-intelligence swarm.
Given a decision question, choose 3 to 5 specialist agents to investigate it in parallel.
Each agent needs a short role title and one focused sub-question to research.

Return ONLY a JSON array and nothing else, in exactly this shape:
[
  {{"role": "Market Analyst", "focus": "a specific sub-question"}},
  {{"role": "Risk Analyst", "focus": "a specific sub-question"}}
]

Decision question: {query}
"""


def _extract_agents(text):
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except Exception:
        return None
    if not isinstance(data, list):
        return None
    cleaned = []
    for item in data:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip()
        focus = str(item.get("focus", "")).strip()
        if role and focus:
            cleaned.append({"role": role, "focus": focus})
    return cleaned or None


def _fallback(query):
    return [
        {"role": "Research Analyst", "focus": query},
        {"role": "Risk Analyst", "focus": f"key risks and downsides of {query}"},
        {"role": "Opportunity Analyst", "focus": f"key opportunities and upside of {query}"},
    ]


async def plan(query):
    llm = get_llm(temperature=0.2)
    msg = await llm.ainvoke(PROMPT.format(query=query))
    text = getattr(msg, "content", "") or ""
    return _extract_agents(text) or _fallback(query)