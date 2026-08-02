"""全局配置：路径 / API Key / 检索参数"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------- 路径 ----------
# 项目根目录（onlyup-rag-agent/）
BASE_DIR = Path(__file__).resolve().parent.parent
# 原始文档目录（放 onlyup_design.txt 等）
DATA_DIR = BASE_DIR / "data"
# ChromaDB 持久化目录（运行时生成）
CHROMA_DIR = BASE_DIR / "chroma_db_onlyup"

# ---------- LLM（DeepSeek，OpenAI 兼容协议） ----------
# 注意：DeepSeek 目前没有 Embedding API（见 PITFALLS.md），
#       向量化用本地 ONNX 模型，只有生成/ReRank 走 DeepSeek。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# ---------- 检索参数 ----------
CHUNK_SIZE = 300        # OnlyUp 文档较长，块稍大
CHUNK_OVERLAP = 80      # 块重叠
BM25_TOP_K = 5          # BM25 关键词召回
SEMANTIC_TOP_K = 5      # 语义向量召回
FINAL_TOP_K = 3         # ReRank 后最终返回给 LLM 的块数
RRF_K = 60              # RRF 平滑参数（score = Σ 1/(k+rank)）
