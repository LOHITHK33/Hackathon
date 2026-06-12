import asyncio

from ..llm import get_llm
from ..tools.search import format_results, web_search

AGENT_PROMPT = """You are the {role} on a decision-intelligence team.
The decision under review: {query}
Your focus: {focus}

Web search returned the following for your focus:
{research}

Write a tight analysis of 4 to 6 sentences on what these findings mean for the decision.
State concrete facts and numbers where available.
End with one line beginning "Confidence:" rating your confidence as high, medium, or low and why.
"""


async def run_agent(role, focus, query, emit=None):
    if emit:
        await emit("agent_spawned", {"role": role, "focus": focus})
    results = await web_search(focus, max_results=5)
    research = format_results(results)
    llm = get_llm(temperature=0.3)
    msg = await llm.ainvoke(
        AGENT_PROMPT.format(role=role, query=query, focus=focus, research=research)
    )
    summary = (getattr(msg, "content", "") or "").strip()
    sources = [r["url"] for r in results if r.get("url")]
    finding = {"role": role, "focus": focus, "summary": summary, "sources": sources}
    if emit:
        await emit("agent_done", {"role": role, "summary": summary, "sources": sources})
    return finding


async def research(query, agents, emit=None):
    tasks = [run_agent(a["role"], a["focus"], query, emit) for a in agents]
    return await asyncio.gather(*tasks)