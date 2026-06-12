from ..llm import get_llm

PROMPT = """You are the lead synthesizer for a decision-intelligence swarm.
The decision under review: {query}

Specialist findings:
{findings}

Cross-examination between agents:
{debate}

Write a concise decision memo with these sections, each on its own line:
Recommendation: a clear stance with one or two sentences of justification.
Key findings: the strongest evidence, attributed to the relevant analysts.
Open risks: unresolved tensions from the cross-examination.
Confidence: overall confidence as high, medium, or low, and what would raise it.

Be specific and use numbers where the findings provide them.
"""


def _format_findings(findings):
    blocks = []
    for f in findings:
        src = ", ".join(f.get("sources", [])[:3])
        blocks.append(f"{f['role']} (focus: {f['focus']}):\n{f['summary']}\nSources: {src}")
    return "\n\n".join(blocks)


def _format_debate(debate):
    if not debate:
        return "No major contradictions were raised."
    lines = []
    for d in debate:
        target = d.get("target", "")
        head = f"{d['challenger']} vs {target}" if target else d["challenger"]
        lines.append(f"{head}: {d['point']}")
    return "\n".join(lines)


async def synthesize(query, findings, debate, emit=None):
    llm = get_llm(temperature=0.3)
    prompt = PROMPT.format(
        query=query,
        findings=_format_findings(findings),
        debate=_format_debate(debate),
    )
    memo = ""
    async for chunk in llm.astream(prompt):
        text = getattr(chunk, "content", "") or ""
        if text:
            memo += text
            if emit:
                await emit("memo", {"text": text})
    if emit:
        await emit("memo_done", {"memo": memo})
    return memo