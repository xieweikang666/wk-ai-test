# 测试指南

> 注意：本项目使用 `python3` 命令，不是 `python`

## 快速开始

详细说明请参考 [QUICK_START.md](QUICK_START.md)

### 1. 安装依赖

```bash
python3 install_deps.py
```

### 2. 验证代码

```bash
python3 verify.py
```

### 3. 运行测试（CLI 模式）

```bash
python3 cli.py -q "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
```

## FastAPI 服务模式

### 启动服务

```bash
python3 app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 测试 API

#### 使用 curl

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
  }'
```

#### 使用 Python 脚本

```bash
python3 test_api.py
```

#### 使用浏览器

访问 http://localhost:8000/docs 使用 Swagger UI 测试

## 预期输出

CLI 工具会输出：

1. **QueryPlan**: LLM 生成的查询计划（JSON 格式）
2. **SQL**: 生成的 SQL 语句（用于评估）
3. **查询结果**: 前10行数据预览
4. **图表路径**: 如果生成了图表，会显示路径
5. **分析结果**: LLM 对查询结果的自然语言分析

## 问题排查

1. **导入错误**: 运行 `python3 verify.py` 检查导入
2. **依赖缺失**: 运行 `python3 install_deps.py` 自动安装
3. **sentence-transformers 安装失败**: 运行 `python3 fix_sentence_transformers.py`
4. **数据库连接**: 检查 ClickHouse 配置是否正确
5. **API 密钥**: 确认 LLM API 配置正确

