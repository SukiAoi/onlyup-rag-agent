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

## 总结：RAG 最小可行链路

```
txt 文档 → 切块（200字/块，重叠50字）
    → ONNX 向量化（本地，无需 API Key）
    → 存 ChromaDB（持久化到 chroma_db/ 目录）
    → 用户提问向量化 → 检索 Top-3 相似块
    → 拼入 Prompt → DeepSeek API 生成答案
```
