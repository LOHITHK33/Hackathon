from typing import TypedDict


class AgentState(TypedDict):
    query: str
    agents: list
    findings: list
    debate: list
    memo: str