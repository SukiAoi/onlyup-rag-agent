# 演示问答 / Demo Q&A（v1.1 工具调用）

运行 `demo_tools.py` 或调用 `POST /ask`，观察 Agent 如何**自己决定**用哪个工具。

## 用例 1：文档问题 → `query_onlyup_docs`

> 问：攀爬系统有几个状态？

```
🛠️  用：['query_onlyup_docs']
💬 答：根据 OnlyUp! 游戏设计文档（来源：onlyup_design.txt），
攀爬系统采用有限状态机（FSM），共有 6 个状态：
Idle（待机）、Running（跑动）、Jumping（跳跃）、
Hanging（悬挂）、Climbing（攀爬）……（第 6 个状态文档未完整定义）
```

## 用例 2：数学问题 → `calculator`

> 问：2 ** 10 + 5 * 3 等于多少？

```
🛠️  用：['calculator']
      · 调用 calculator(expression=2 ** 10 + 5 * 3)
        → 2 ** 10 + 5 * 3 = 1039
💬 答：计算结果为 1039。
```

## 用例 3：闲聊 → 不调用工具

> 问：你好，今天天气怎么样？

```
🛠️  用：（无）
💬 答：我是 OnlyUp! 游戏设计文档助手……我没有实时天气数据，
但如果你对游戏设计、攀爬跳跃机制感兴趣，我很乐意解答！
```

## 用例 4：组合/改造类问题 → 多次调用 `query_onlyup_docs`

> 问：把跳跃高度从 3 改成 5 会影响什么？

```
🛠️  用：['query_onlyup_docs', 'query_onlyup_docs', 'query_onlyup_docs']
💬 答：文档未直接记录跳跃高度数值参数；文档建议优先调节
平台宽度、平台间距、障碍物速度、检查点密度来控制难度曲线……
```

> 说明：LLM 工具选择带一定随机性（temperature=0.3），个别问题可能换一种工具路线，属正常现象。
