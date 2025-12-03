# 网络探测数据 AI 分析 Agent

> 🚀 **企业级网络探测数据智能分析平台** - 基于大语言模型的网络质量分析与决策支持系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![ClickHouse](https://img.shields.io/badge/ClickHouse-22.8+-yellow.svg)](https://clickhouse.com)
[![LLM](https://img.shields.io/badge/LLM-GPT--4o--mini-purple.svg)](https://openai.com)

## 🎯 项目概述

本项目是一个**智能化的网络探测数据分析平台**，专为网络质量监控、故障诊断和性能优化而设计。通过融合大语言模型（LLM）、时序数据库和自然语言处理技术，实现了从自然语言查询到专业分析报告的端到端解决方案。

### 核心价值

- **🤖 自然语言交互**：无需编写复杂SQL，用日常语言即可查询网络数据
- **📊 智能质量分析**：自动识别网络问题，提供具体的设备/节点优化建议  
- **🎯 精准洞察输出**：结构化分析报告，包含TOP排名、对比数据和可操作建议
- **🛡️ 企业级安全**：完善的权限控制、SQL注入防护和数据安全机制

## ✨ 功能特性

### 🔍 智能查询分析
- **多维度分析**：支持探测设备、目标节点、地区覆盖等多角度分析
- **质量排名**：自动识别质量最好/最差的设备节点，提供具体性能指标
- **趋势分析**：网络质量变化趋势识别和异常检测
- **对比分析**：不同运营商、地区、时间段的性能对比

### 📊 数据可视化
- **自动图表生成**：根据查询类型自动生成折线图、柱状图等
- **实时数据展示**：支持网络质量实时监控和告警
- **多格式输出**：支持表格、图表、文字报告等多种展示形式

### 🏗️ 技术架构

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   自然语言查询   │───▶│   LLM 理解    │───▶│   查询规划器     │
│                 │    │              │    │                 │
│ "哪些设备质量差?"│    │  意图识别     │    │  QueryPlan     │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   智能分析报告   │◀───│  结构化数据   │◀───│  SQL 执行引擎   │
│                 │    │              │    │                 │
│ TOP排名+建议    │    │ 数据摘要+统计 │    │ ClickHouse      │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### 🔧 核心模块

| 模块 | 功能 | 关键特性 |
|------|------|----------|
| **agent/simple_planner.py** | 查询规划器 | 自然语言→QueryPlan，支持复杂查询逻辑 |
| **agent/functions.py** | 查询执行器 | SQL生成、执行、结果处理，多聚合模式支持 |
| **agent/analyzer.py** | 智能分析器 | 结构化数据分析，TOP排名，可操作建议生成 |
| **db/clickhouse_client.py** | 数据库客户端 | 安全查询，注入防护，性能优化 |
| **utils/chart.py** | 可视化工具 | 自动图表生成，多图表类型支持 |
| **self_check.py** | 质量保证 | 自动化测试，分析质量评估，回归检测 |

### 📋 环境要求

- **Python 3.9+** (推荐 3.11)
- **ClickHouse 22.8+** (时序数据库)
- **8GB+ RAM** (推荐用于大模型处理)
- **Docker & Docker Compose** (可选，用于容器化部署)

### 🛠️ 安装配置

#### 1. 克隆项目
```bash
git clone <repository-url>
cd wk-ai-test
```

#### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

#### 3. 安装依赖
```bash
# 生产环境
pip install -r requirements.txt

# 开发环境（包含测试工具）
pip install -r requirements-dev.txt
```

#### 4. 配置环境变量
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（必须设置）
# OPENAI_API_KEY=your_api_key_here
# CLICKHOUSE_PASSWORD=your_password_here
```

### 🚀 快速启动

#### ⭐ 一键启动（推荐）

**开发模式** - 前后端独立运行，支持热重载：
```bash
./start-dev.sh
```
- 🔧 后端：http://localhost:8000
- 🎨 前端：http://localhost:3000 (React + Ant Design)
- 📝 日志：`logs/backend.log`, `logs/frontend.log`

**生产模式** - 单端口部署：
```bash
./build-prod.sh && ./start-prod.sh
```
- 🌐 统一访问：http://localhost:8000
- 📦 React构建文件，无需前端服务器

#### 🛠️ 传统启动方式

**Web API 模式**：
```bash
# 开发模式（React前端需单独启动）
python3 app.py --host 0.0.0.0 --port 8000

# 生产模式（自动服务React构建文件）
python3 app.py --host 0.0.0.0 --port 8000 --prod
```

**命令行模式**：
```bash
# 直接查询
python3 app.py -q "统计近1h各运营商的探测设备数量"

# 运行质量自测
python3 self_check.py
```

**Docker 容器化**：
```bash
# Docker Compose 部署
docker-compose up -d
```

### 🌐 服务访问

| 模式 | 前端地址 | 后端API | 适用场景 |
|------|----------|---------|----------|
| **开发模式** | http://localhost:3000 | http://localhost:8000 | 日常开发调试 |
| **生产模式** | http://localhost:8000 | http://localhost:8000 | 生产部署 |
| **API文档** | - | http://localhost:8000/docs | 接口文档 |
| **健康检查** | - | http://localhost:8000/health | 状态检查 |

### 🎨 前端界面

#### React + Ant Design 现代化界面（推荐）
- **ChatGPT风格** 对话界面
- **专业表格** 展示，自动数值对齐
- **SQL语法高亮** 显示
- **图表预览和下载** 功能
- **响应式设计**，移动端友好

#### 原始HTML界面（开发模式备用）
- **基础Markdown渲染**
- **表格优化显示**
- **简单图表展示**

## 💡 使用示例

### 🔥 核心查询场景

#### 1. 探测设备质量分析
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
  }'
```

**预期输出**：
- 质量最好的TOP3设备（含hostname和具体指标）
- 质量最差的TOP3设备及优化建议
- 整体设备质量分布分析

#### 2. 目标节点性能评估
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "统计近1h的探测目标节点(target_node)丢包情况，区分不同的任务(task_name）统计"
  }'
```

**预期输出**：
- 按丢包率排序的目标节点列表
- 不同探测任务的性能对比
- 目标节点选择建议

#### 3. 地区覆盖质量分析
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "统计近1h，各个目标节点(target_node)覆盖浙江电信(chinatelecom)浙江(zhejiang)的丢包情况"
  }'
```

**预期输出**：
- 浙江电信覆盖的目标节点排名
- TOP3优质节点推荐
- 具体网络质量指标

### 📊 响应格式
```json
{
  "answer": "🎯 **核心结论**：在近1小时内，质量最好的探测设备为 AMCDN1YZ1P6001156（丢包率0.75%）...",
  "chart_url": "/static/chart_20251203_120000.png",
  "sql": "SELECT hostname, task_name, AVG(avg_lost) as avg_lost, AVG(avg_rtt) as avg_rtt, COUNT(*) as count..."
}
```

### 🎯 更多查询示例

- `"查看电信、移动、联通三大运营商的网络质量对比"`
- `"分析过去3小时网络延迟的变化趋势"`
- `"识别丢包率最高的目标节点"`
- `"评估各个省份的网络覆盖情况"`
- `"按任务类型统计探测结果"`

## 🛡️ 安全机制

| 安全特性 | 实现方式 | 保护级别 |
|----------|----------|----------|
| **SQL注入防护** | QueryPlan生成机制，不直接执行用户SQL | 🔒🔒🔒🔒🔒 |
| **查询限制** | 自动注入LIMIT 1000000 | 🔒🔒🔒 |
| **操作限制** | 只允许SELECT查询 | 🔒🔒🔒🔒 |
| **时间范围强制** | 必须包含time_range参数 | 🔒🔒🔒 |
| **敏感信息保护** | 环境变量管理，日志脱敏 | 🔒🔒🔒🔒 |
| **权限控制** | 可配置的访问控制机制 | 🔒🔒 |

## 🏗️ 项目架构

```
wk-ai-test/
├── 📁 agent/                    # AI分析核心模块
│   ├── 🧠 analyzer.py           # 智能分析器 (结构化分析+TOP排名)
│   ├── 🎯 simple_planner.py      # 查询规划器 (自然语言→QueryPlan)
│   ├── ⚙️ functions.py           # 查询执行器 (SQL生成+多聚合模式)
│   ├── 🤖 llm.py                 # LLM模型调用封装
│   ├── 🚀 intelligent_sql_generator.py    # 智能SQL生成器
│   ├── 🧠 intelligent_analyzer.py         # 智能数据分析器
│   ├── 🛡️ query_quality_guard.py          # 查询质量保障系统
│   └── 🚀 intelligent_query_engine.py     # 智能查询引擎
├── 📁 frontend/                  # React前端 (新增)
│   ├── src/components/           # React组件
│   ├── package.json              # 前端依赖配置
│   ├── start.sh                  # 前端启动脚本
│   └── README.md                 # 前端详细说明
├── 📁 db/                       # 数据库层
│   ├── 🗃️ clickhouse_client.py   # ClickHouse安全客户端
│   └── 📄 schema.md              # 数据库结构文档
├── 📁 config/                   # 配置管理
│   └── ⚙️ settings.py            # 环境变量配置
├── 📁 utils/                    # 工具函数
│   ├── 📊 chart.py               # 图表生成器
│   └── ⏰ time_utils.py           # 时间处理工具(支持中文自然语言)
├── 📁 static/                   # 静态文件
│   └── index.html                # 原始HTML界面(备用)
├── 📁 tests/                     # 测试框架
├── 📁 logs/                      # 日志文件
├── 📁 reports/                   # 自测报告
├── 🚀 app.py                     # FastAPI主入口(支持--prod模式)
├── 🚀 start-dev.sh              # 一键开发启动脚本
├── 🏗️ build-prod.sh             # 一键构建脚本
├── 🧪 self_check.py              # 质量保证系统
├── 📖 STARTUP_GUIDE.md           # 启动脚本使用指南
└── 📋 requirements*.txt          # 依赖管理
```

## 📊 项目统计

| 指标 | 数值 | 说明 |
|------|------|------|
| **核心代码行数** | 3,500+行 | agent/ + config/ + db/ + utils/ + frontend/ |
| **模块文件数** | 28个 | 核心业务模块（含智能引擎+React前端） |
| **React组件数** | 3个 | ChatInterface, DataTable, ChartDisplay |
| **一键脚本** | 3个 | start-dev.sh, build-prod.sh, start-prod.sh |
| **API接口** | 6个 | /chat, /health, /engine/*, /docs |
| **查询模式** | 动态生成 | 从8种固定模式升级为LLM动态生成 |
| **前端框架** | React 18 + Ant Design 5 | 现代化UI，替代传统HTML |

## 📋 核心升级 (2024.12)

### 🎨 前端架构升级
- **React + Ant Design** 替代传统HTML界面
- **组件化架构**，易于维护和扩展
- **专业表格组件**，自动数值识别和对齐
- **响应式设计**，完美适配移动端
- **SQL语法高亮**，提升代码可读性

### 🛠️ 时间解析增强
- **中文自然语言** 支持：昨天、今天、晚高峰等
- **复杂时间表达** 解析：19-23点、上午8-12点等
- **智能时间范围** 转换，精确到秒级时间戳

### 🚀 部署方案优化
- **一键开发启动**：`./start-dev.sh`
- **一键生产构建**：`./build-prod.sh && ./start-prod.sh`
- **双端口开发** / **单端口生产** 灵活切换
- **日志管理** 和 **优雅停止** 机制

## 🚀 智能引擎升级 (2024.12)

### ✨ 重大更新
项目已完成**智能查询引擎**重大升级，从硬编码规则系统升级为LLM驱动的智能分析平台：

#### 🤖 SQL生成优化
- **之前**：8种固定聚合模式，硬编码关键词匹配
- **现在**：LLM理解查询意图，动态生成高质量SQL
- **效果**：支持复杂查询，自动优化性能，语义匹配更准确

#### 🧠 结果分析优化  
- **之前**：4种固定分析模板，回答格式死板
- **现在**：深度意图理解，多维度数据洞察，个性化回答
- **效果**：智能分析，异常检测，可操作建议

#### 🛡️ 质量保障系统
- SQL复杂度、性能、语义匹配度检查
- 数据完整性、一致性、分布合理性评估
- 实时质量评分（0-100分）

#### 🎨 Markdown渲染支持
- 完整的Markdown格式渲染：表格、标题、列表、代码块
- 专业的分析报告展示效果
- 支持SQL语法高亮和数据可视化

### 🔧 智能引擎配置
```bash
# .env 文件配置
ENABLE_INTELLIGENT_ENGINE=true          # 启用智能引擎
ENABLE_QUALITY_CHECK=true              # 启用质量检查  
INTELLIGENT_ENGINE_FALLBACK=true       # 启用回退机制
```

### 📈 新增API接口
- `GET /engine/status` - 查看当前引擎状态
- `POST /engine/switch` - 切换引擎模式
- `GET /engine/quality` - 获取质量指标

**详细升级文档**：[INTELLIGENT_ENGINE_UPGRADE.md](./INTELLIGENT_ENGINE_UPGRADE.md)

## 🧪 质量保证

### 自动化测试
```bash
# 运行质量自测
python3 self_check.py

# 运行单元测试
pytest tests/ -v

# 代码质量检查
black . && isort . && flake8 .
```

### 自测覆盖场景
- ✅ 探测设备质量分析 (hostname + task_name)
- ✅ 目标节点性能评估 (target_node + task_name)  
- ✅ 地区覆盖质量分析 (target_node + src_isp + src_province)

## 🔧 开发指南

### 代码规范
- **卫语句设计**：提前返回，减少嵌套层级
- **类型注解**：完整的函数签名和返回值类型
- **错误处理**：完善的异常捕获和日志记录
- **安全性**：输入验证和SQL注入防护

### 扩展开发
1. **新增查询模式**：修改 `simple_planner.py` 添加新的聚合规则
2. **优化分析逻辑**：增强 `analyzer.py` 的分析深度和准确性
3. **图表类型扩展**：在 `chart.py` 中添加新的可视化类型
4. **测试用例扩展**：在 `tests/` 中添加更多测试场景

## 📈 性能优化

- **查询优化**：智能索引建议和查询缓存
- **内存管理**：大数据集的流式处理
- **并发处理**：异步查询和结果处理
- **缓存机制**：频繁查询的结果缓存

## 🚀 部署指南

详细部署文档请参考：[DEPLOYMENT.md](./DEPLOYMENT.md)

### 快速部署
```bash
# Docker Compose (推荐)
docker-compose up -d

# 手动部署
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置
python3 app.py --host 0.0.0.0 --port 8000
```

## 📞 技术支持与文档

### 📖 相关文档
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 详细部署指南
- **[STARTUP_GUIDE.md](./STARTUP_GUIDE.md)** - 启动脚本使用指南
- **[FRONTEND_OPTIMIZATION_REPORT.md](./FRONTEND_OPTIMIZATION_REPORT.md)** - 前端优化报告

### 🔧 帮助与支持
- 🐛 **问题反馈**：[GitHub Issues](https://github.com/your-repo/issues)
- 💬 **技术交流**：项目讨论区
- 📧 **技术支持**：项目维护团队

### 🚀 快速参考
```bash
# 常用命令快速参考
./start-dev.sh           # 开发模式启动
./build-prod.sh          # 生产构建
./start-prod.sh          # 生产模式启动
python3 self_check.py    # 质量检查
python3 app.py --prod    # 直接生产启动
```

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

> 🌟 **如果这个项目对您有帮助，请给我们一个 Star！**
> 
> 💡 **提示**：推荐使用React前端界面，提供更专业和现代化的用户体验！

