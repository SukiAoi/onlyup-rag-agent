# OnlyUp! RAG Agent 🕹️

基于 **FastAPI + LangGraph + ChromaDB** 的 RAG 问答 Agent，回答 OnlyUp! 游戏设计文档相关问题。

A RAG Q&A agent built with **FastAPI + LangGraph + ChromaDB** that answers questions from the OnlyUp! game design document.

## 特性 / Features

- 🔍 **混合检索** Hybrid Retrieval：BM25 关键词召回 + ChromaDB 语义向量召回
- 🔀 **RRF 融合** Reciprocal Rank Fusion：合并两路结果、去重
- 🧠 **LLM ReRank**：用 DeepSeek 对候选块重排序，只留 Top-K
- 🤖 **LangGraph 编排**：检索 → 生成 做成可扩展的图
- ⚡ **FastAPI**：`POST /ask` 接口 + 交互式文档

## 目录结构 / Structure

```
onlyup-rag-agent/
├── app/
│   ├── main.py      # FastAPI 入口（/health, /ask）
│   ├── agent.py     # LangGraph 图编排
│   ├── rag.py       # 混合检索引擎（Chroma + BM25 + RRF + ReRank）
│   └── config.py    # 配置（API Key、路径、检索参数）
├── data/            # 原始文档（onlyup_design.txt）
├── chroma_db_onlyup/  # ChromaDB 持久化（运行时生成）
├── requirements.txt
└── .env.example     # 环境变量模板
```

## 快速开始 / Quick Start

```bash
# 1. 创建虚拟环境（Windows）
python -m venv .venv
.venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key
copy .env.example .env        # 填入 DEEPSEEK_API_KEY

# 4. 启动服务
uvicorn app.main:app --reload

# 5. 测试
curl -X POST http://127.0.0.1:8000/ask ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"攀爬系统有几个状态？\"}"
```

API 交互式文档：<http://127.0.0.1:8000/docs>

## 效果示例 / Demo

浏览器打开 <http://127.0.0.1:8000/docs>，在 Swagger 界面直接提问：

![Swagger UI 截图](docs/swagger.png)

**示例问答**（实际输出见 docs/demo_qa.md）：

> 问：攀爬系统有几个状态？
> 答：见 docs/demo_qa.md

## 说明 / Notes

- DeepSeek 目前**没有 Embedding API**，向量化使用 ChromaDB 内置的本地 ONNX 模型（`ONNXMiniLM_L6_V2`），生成与 ReRank 走 DeepSeek。
- 模型首次运行会下载（~23MB），之后缓存在本地。
- 踩坑记录见 [PITFALLS.md](PITFALLS.md)。

## Roadmap / 计划

- [ ] `create_agent` 接入工具调用（如计算器）—— 按 v3.2 计划 8/17 完成（v1.1）
- [ ] 更多游戏文档入库
- [ ] 检索质量评估：不同 chunk_size / Top-K 的命中率对比
