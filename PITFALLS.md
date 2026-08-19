# RAG 程序踩坑记录 🕳️

## 坑 1：chromadb 不自动带 Embedding 模型依赖

**现象：**
```
ValueError: The sentence_transformers python package is not installed.
```

**原因：** `pip install chromadb` 不会自动安装 `sentence-transformers`，需要手动装。

**解决：**
```bash
pip install sentence-transformers
```

---

## 坑 2：DeepSeek 没有公开的 Embedding API

**现象：** 原计划使用 DeepSeek API 做向量化，但 DeepSeek 目前没有提供 Embedding 端点。

**解决：** 改用本地模型：
- `sentence-transformers` 的 `all-MiniLM-L6-v2`（Python 库，384 维）
- ChromaDB 内置的 `ONNXMiniLM_L6_V2`（ONNX 运行时，更轻量 ~23MB）

---

## 坑 3：HuggingFace 模型下载巨慢（国内）

**现象：** 首次运行卡在下载 `all-MiniLM-L6-v2`（~80MB），十几分钟无进度。

**原因：** HuggingFace 服务器在国外，直接下载非常慢甚至超时。

**解决方案（按推荐度排序）：**
1. ✅ **用 ChromaDB 内置 ONNX 模型**（`ONNXMiniLM_L6_V2`），文件更小 ~23MB，且走 ChromaDB 的 CDN
2. 设置 HuggingFace 镜像：`$env:HF_ENDPOINT="https://hf-mirror.com"`
3. 手动下载模型放到 `~/.cache/huggingface/` 目录

---

## 坑 4：模型放到模块顶层导致 import 时就卡住

**现象：** 程序一启动就卡在模型下载，看不到任何输出。

**原因：** `embedding_fn = SentenceTransformerEmbeddingFunction(...)` 写在模块顶层（全局），import 时就触发下载。

**改进：** 改成 try/except 懒加载 + 加 print 提示，让用户知道在干嘛：
```python
try:
    embedding_fn = embedding_functions.ONNXMiniLM_L6_V2()
    print("   ✅ 使用 ONNX 嵌入模型")
except Exception:
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    print("   ⚠️ 回退到默认嵌入模型")
```

---

## 坑 5：ChromaDB Collection 重复创建报错

**现象：** 第二次运行时报 `Collection already exists`。

**解决：** 加判断——如果本地 `chroma_db/` 目录已存在就跳过创建，直接加载。

---

## 坑 6：langchain 1.x 不自带 ChatOpenAI

**现象：** `from langchain_openai import ChatOpenAI` 报 ModuleNotFoundError。

**原因：** `create_agent` 是 langchain 核心 API，但 LLM 接入包 `langchain-openai` 需单独安装（DeepSeek 走 OpenAI 兼容协议）。

**解决：**
```bash
pip install "langchain-openai>=0.3.0"
```
并加入 `requirements.txt`（要求全 ASCII，避免 Windows GBK 下 pip 报错）。

---

## 坑 7：PowerShell 发中文 JSON 给 API 变 `???`

**现象：** 用 `Invoke-RestMethod` 测 `/ask`，服务端日志显示 `收到问题：??????????`，模型答非所问。

**原因：** PowerShell 5.1 默认用 GBK 编码序列化中文，POST 体里的中文变乱码。

**解决：** 测试中文接口用 Python / curl（UTF-8），或在 PowerShell 里先 `[Console]::OutputEncoding` / 显式指定 UTF-8 编码。

---

## 坑 8：英文 embedding 处理中文文档，语义召回弱

**现象：** 用 `ONNXMiniLM_L6_V2`（英文 ONNX 模型）做中文 GDD 文档的语义检索，命中率低——很多 gold 块只靠 BM25 关键词召回，语义路基本"猜不中"。

**原因：** `all-MiniLM` / `ONNXMiniLM_L6_V2` 面向英文训练，对中文语义理解弱，中文问题与中文块的向量相似度区分度差。

**验证（量化）：** 20 问命中率评估，英文 ONNX 基线 Hit@3=85%、Hit@5=95%；换成中文 `BAAI/bge-small-zh-v1.5` 后 **Hit@3=95%、Hit@5=100%、MRR 0.631→0.771**。

**解决：**
- 中文语料 → 用中文 embedding（`bge-small-zh-v1.5` / `text2vec-base-chinese`）
- 本项目已支持 `EMBEDDING_MODEL=bge`（`app/config.py` + `app/rag.py`），bge 用独立 Chroma 目录 `chroma_db_onlyup_bge/`（维度 512 vs onnx 384，避免冲突）
- bge 需要 `sentence-transformers` + `torch`，生产默认仍用轻量 onnx，评估/中文场景切 bge

---

## 坑 9：LLM ReRank 在小语料上是负优化

**现象：** 走 `retrieve()`（含 LLM ReRank）后，命中率反而下降：BGE 下 @3 95%→85%、@5 100%→85%，MRR 0.771→0.667。个别题（如「角色冲刺速度」）RRF 已把 gold 排第 1，ReRank 却把它挤出 Top-5。

**原因：**
- RRF 融合（BM25 排名 + 语义排名）是**稳定统计信号**，在小语料（13 块）下 Top-3 已近乎完美；
- LLM 对"最相关块"的判断带噪声，块内容高度同主题时易猜错；`temperature=0` 只能降低、不能消除；
- 候选池小，ReRank 每选错一个编号就丢一个正确答案，容错空间几乎为零。

**结论 / 设计权衡：** ReRank 适合**大语料、候选池大、块差异明显**的场景（帮从噪声中挑最准的）；小语料场景属于过度设计。专业做法是**按候选池大小自适应**——`len(fused)` 超过阈值（如 >8）才触发 ReRank，否则信任 RRF。

---

## 总结：RAG 最小可行链路

```
txt 文档 → 切块（300字/块，重叠80字）
    → 向量化（ONNX 英文 或 bge 中文，按 EMBEDDING_MODEL）
    → 存 ChromaDB（持久化到 chroma_db* 目录）
    → 用户提问向量化 → BM25 + 语义双路召回 → RRF 融合 → （可选 ReRank）Top-K
    → 拼入 Prompt → DeepSeek API 生成答案
```
