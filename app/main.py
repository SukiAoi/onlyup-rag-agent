"""
FastAPI 入口
------------
启动：  uvicorn app.main:app --reload
文档：   http://127.0.0.1:8000/docs
测试：   curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"攀爬系统有几个状态？\"}"
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from .agent import build_agent
from .rag import RAGEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

rag = RAGEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时预热：构建/加载知识库（幂等），避免首请求卡顿"""
    logger.info("⏳ 预热：构建 / 加载知识库...")
    rag.build()
    logger.info("✅ 知识库就绪，agent 已编译")
    yield
    logger.info("👋 应用关闭")


app = FastAPI(title="OnlyUp! RAG Agent", version="0.1.0", lifespan=lifespan)
agent = build_agent(rag)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "kb_chunks": len(rag.all_documents)}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    logger.info("❓ 收到问题：%s", req.question)
    result = agent.invoke({"question": req.question})
    logger.info("✅ 来源：%s", result["sources"])
    return AskResponse(answer=result["answer"], sources=result["sources"])
