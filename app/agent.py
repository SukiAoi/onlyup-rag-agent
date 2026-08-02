"""
LangGraph Agent 编排
--------------------
把 RAG 流程建成一张可编排的图：

    question → [retrieve] → contexts → [generate] → answer

之后想加工具（如计算器）、加记忆、加条件分支，都在这里扩展。
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from .rag import RAGEngine


class AgentState(TypedDict):
    """在图的节点之间传递的状态"""
    question: str
    contexts: list[dict]   # retrieve 产出的候选块
    answer: str
    sources: list[str]


def build_agent(rag: RAGEngine):
    """构建并编译 LangGraph 图"""

    def retrieve(state: AgentState) -> dict:
        contexts = rag.retrieve(state["question"])
        return {"contexts": contexts}

    def generate(state: AgentState) -> dict:
        answer, sources = rag.answer_with_contexts(state["question"], state["contexts"])
        return {"answer": answer, "sources": sources}

    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()
