# 快速开始指南

## 安装依赖

```bash
# 方式一：自动安装（推荐）
python3 install_deps.py

# 如果 sentence-transformers 安装失败，运行修复脚本
python3 fix_sentence_transformers.py

# 如果遇到 huggingface_hub 版本问题，运行依赖修复脚本
python3 fix_dependencies.py

# 方式二：手动安装
pip3 install -r requirements.txt

# 如果仍有问题，单独安装 sentence-transformers
pip3 install sentence-transformers
```

## CLI 命令行模式（推荐）

### 基本使用

```bash
# 1. 验证代码（检查导入和逻辑）
python3 verify.py

# 2. 运行测试（使用默认问题）
python3 cli.py

# 3. 自定义问题
python3 cli.py -q "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"

# 4. 静默模式（只显示最终结果）
python3 cli.py --quiet

# 5. 测试模式（运行多个测试问题）
python3 cli.py --test
```

### 通过 app.py 使用 CLI 模式

```bash
# app.py 也支持 CLI 参数
python3 app.py -q "你的问题"
```

## FastAPI 服务模式

```bash
# 启动服务
python3 app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

## 测试你的问题

```bash
python3 cli.py -q "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
```

## 输出说明

CLI 工具会输出：
1. QueryPlan（LLM 生成的查询计划）
2. SQL（生成的 SQL 语句，用于评估）
3. 查询结果（前10行数据预览）
4. 图表路径（如果生成了图表）
5. 分析结果（LLM 对结果的解释）

