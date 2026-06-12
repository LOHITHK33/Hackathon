import json

from ..llm import get_llm

PROMPT = """You are the critical reviewer for a decision-intelligence swarm.
The decision under review: {query}

Findings from the specialist agents:
{findings}

Identify the most important tensions, contradictions, or gaps BETWEEN these findings.
For each, name which agent is challenging which, and state the specific point.

Return ONLY a JSON array and nothing else, in exactly this shape:
[
  {{"challenger": "Risk Analyst", "target": "Market Analyst", "point": "the specific contradiction"}}
]
If the findings genuinely do not conflict, return an empty array [].
"""


def _format_findings(findings):
    blocks = []
    for f in findings:
        blocks.append(f"{f['role']} (focus: {f['focus']}):\n{f['summary']}")
    return "\n\n".join(blocks)


def _extract(text):
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
        challenger = str(item.get("challenger", "")).strip()
        target = str(item.get("target", "")).strip()
        point = str(item.get("point", "")).strip()
        if challenger and point:
            cleaned.append({"challenger": challenger, "target": target, "point": point})
    return cleaned


async def debate(query, findings, emit=None):
    llm = get_llm(temperature=0.4)
    msg = await llm.ainvoke(
        PROMPT.format(query=query, findings=_format_findings(findings))
    )
    text = getattr(msg, "content", "") or ""
    points = _extract(text)
    if points is None:
        points = []
    if emit:
        for p in points:
            await emit("debate", p)
    return points