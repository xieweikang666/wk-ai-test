# CLAUDE.md - 网络探测数据AI分析平台

> 🚀 **项目总结与技术文档** - 为AI助手提供的完整项目理解指南

## 🎯 项目核心定位

**网络探测数据AI分析平台**是一个企业级的智能分析系统，专门用于网络质量监控、故障诊断和性能优化。该项目通过融合大语言模型（LLM）、时序数据库和自然语言处理技术，实现了从自然语言查询到专业分析报告的端到端解决方案。

### 核心价值主张
- **自然语言交互**：用户无需编写复杂SQL，用日常语言即可查询网络数据
- **智能质量分析**：自动识别网络问题，提供具体的设备/节点优化建议  
- **精准洞察输出**：结构化分析报告，包含TOP排名、对比数据和可操作建议
- **企业级安全**：完善的权限控制、SQL注入防护和数据安全机制

## 🏗️ 技术架构概览

### 系统架构图
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

### 核心技术栈
- **后端框架**: FastAPI 0.104.1 (高性能异步API框架)
- **数据库**: ClickHouse 22.8+ (时序数据库，专为网络探测数据优化)
- **AI模型**: GPT-4o-mini (通过国内API接入)
- **数据处理**: Pandas 2.1.3 + NumPy 1.26.2
- **可视化**: Matplotlib 3.8.2
- **语言处理**: LangChain 0.0.350 + Sentence Transformers 2.2.2
- **向量检索**: FAISS 1.7.4

## 📁 项目结构详解

### 核心模块架构
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
│   ├── 🔧 intelligent_query_engine.py     # 智能查询引擎
│   └── 📚 simple_analyzer.py     # 简化分析器
├── 📁 db/                       # 数据库层
│   ├── 🗃️ clickhouse_client.py   # ClickHouse安全客户端
│   └── 📄 schema.md              # 数据库结构文档
├── 📁 config/                   # 配置管理
│   └── ⚙️ settings.py            # 环境变量配置 (支持智能引擎开关)
├── 📁 utils/                    # 工具函数
│   ├── 📊 chart.py               # 图表生成器
│   └── ⏰ time_utils.py           # 时间处理工具
├── 📁 static/                   # 前端资源
│   ├── 📄 index.html             # ChatGPT风格交互界面
│   └── 🎨 markdown-test.html     # Markdown渲染测试页
├── 🚀 app.py                     # FastAPI主入口 (增强版API)
├── 🧪 self_check.py              # 质量保证系统
└── 📋 requirements*.txt          # 依赖管理
```

## 🔧 核心功能模块

### 1. 查询规划器 (SimpleQueryPlanner)
**文件**: `agent/simple_planner.py`

**功能**: 将自然语言查询转换为结构化的QueryPlan
- 支持8种查询模式：设备质量、目标节点、地区覆盖、运营商对比等
- 智能时间解析：近1h、近3h、近24h等
- 多维度过滤：运营商、省份、任务类型等
- 自动聚合策略：GROUP BY、COUNT、AVG等

### 2. 查询执行器 (QueryExecutor)
**文件**: `agent/functions.py`

**功能**: 执行QueryPlan并返回结果数据
- 动态SQL生成：基于查询计划生成安全SQL
- 多聚合模式：支持不同的GROUP BY和聚合函数
- 性能优化：自动LIMIT限制、索引建议
- 安全防护：SQL注入防护、只允许SELECT查询

### 3. 智能分析器 (IntelligentAnalyzer)
**文件**: `agent/analyzer.py` + `agent/intelligent_analyzer.py`

**功能**: 对查询结果进行深度分析并生成自然语言报告
- 结构化数据分析：自动识别数据模式和异常
- TOP排名生成：质量最好/最差的设备节点列表
- 可操作建议：基于数据的具体优化措施
- 多维度洞察：从不同角度分析网络性能

### 4. 智能引擎系统 (2024.12重大升级)
**文件**: `agent/intelligent_*.py`

**功能**: 从规则驱动升级为AI驱动的智能分析
- **智能SQL生成器**：LLM理解查询意图，动态生成高质量SQL
- **智能分析器**：深度意图理解，多维度数据洞察
- **质量保障系统**：4维质量检查（复杂度、性能、语义、执行）
- **统一引擎**：向后兼容，支持引擎切换

## 📊 数据库Schema

### 核心表结构
```sql
-- 主表：detect.detect_ping_log
CREATE TABLE detect.detect_ping_log (
    timestamp Int64,           -- Unix时间戳(秒)，必须用于时间过滤
    task_name String,          -- 探测任务名称，如 edge_l1_detect
    src_isp String,            -- 源运营商 (chinatelecom/chinamobile等)
    src_province String,       -- 源省份 (zhejiang/jiangsu/beijing等)
    hostname String,           -- 探测设备主机名
    target_node String,        -- 目标节点标识
    avg_rtt Float64,           -- 平均延迟(ms)，核心性能指标
    avg_lost Float64,          -- 平均丢包率(0-1)，核心质量指标
    packet_loss Int64,         -- 丢包数量
    packet_total Int64         -- 总包数量
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, task_name, src_isp, src_province);
```

### 查询特性
- **时序优化**：按时间分区，支持高效时间范围查询
- **索引策略**：(timestamp, task_name, src_isp, src_province)复合索引
- **安全限制**：强制LIMIT限制，只允许SELECT查询
- **性能监控**：查询执行时间统计和优化建议

## 🚀 API接口设计

### 核心API端点
```python
# 主要聊天接口
POST /chat
{
    "message": "统计近1h各运营商的探测设备数量"
}
# 响应
{
    "answer": "🎯 **核心结论**：...",
    "chart_url": "/static/chart_xxx.png",
    "sql": "生成的SQL语句",
    "quality_summary": "🟢 查询质量：优秀 (85.2/100)"  # 智能引擎新增
}

# 系统状态接口
GET /health                    # 健康检查
GET /engine/status            # 智能引擎状态
POST /engine/switch           # 切换引擎模式
GET /engine/quality           # 质量指标
```

### 响应格式特性
- **Markdown支持**：完整的Markdown格式渲染
- **智能分析**：结构化的分析报告
- **可视化图表**：自动生成的数据图表
- **质量评分**：查询结果质量评估

## ⚙️ 配置管理

### 环境变量配置
```python
# config/settings.py
class Settings(BaseSettings):
    # LLM 配置
    OPENAI_API_KEY: str        # API密钥
    OPENAI_API_BASE: str       # API地址 (国内优化)
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # ClickHouse 配置
    CLICKHOUSE_ENABLE: bool = True
    CLICKHOUSE_DATABASE: str = "detect"
    CLICKHOUSE_USERNAME: str = "zcdn"
    CLICKHOUSE_PASSWORD: str   # 数据库密码
    CLICKHOUSE_ADDRESSES: List[str]  # 集群地址
    
    # 智能引擎配置 (2024.12新增)
    ENABLE_INTELLIGENT_ENGINE: bool = False      # 智能引擎开关
    ENABLE_QUALITY_CHECK: bool = True           # 质量检查开关
    INTELLIGENT_ENGINE_FALLBACK: bool = True    # 回退机制
```

## 🎨 前端界面特性

### ChatGPT风格交互界面
**文件**: `static/index.html`

**核心特性**:
- 现代化ChatGPT风格界面设计
- 实时Markdown渲染：表格、标题、列表、代码块
- 智能建议提示：常用查询场景快速选择
- 响应式设计：支持移动端和桌面端
- 无刷新交互：WebSocket风格的流畅体验

### Markdown渲染功能
```javascript
// 支持的Markdown格式
- 表格渲染 | 自动对齐 | 悬停效果
- 标题层级 # ## ### ####
- 粗体斜体 **text** *text*
- 列表支持 1. 有序 - 无序
- 代码块 ```sql ```python
- 引用 > 重要提示
- 分割线 ---
```

## 🛡️ 安全机制

### 多层安全防护
1. **SQL注入防护**: QueryPlan机制，不直接执行用户SQL
2. **查询限制**: 自动注入LIMIT 1000000
3. **操作限制**: 只允许SELECT查询
4. **时间范围强制**: 必须包含time_range参数
5. **敏感信息保护**: 环境变量管理，日志脱敏
6. **权限控制**: 可配置的访问控制机制

### 安全级别评估
| 安全特性 | 实现方式 | 保护级别 |
|----------|----------|----------|
| SQL注入防护 | QueryPlan生成机制 | 🔒🔒🔒🔒🔒 |
| 查询限制 | 自动注入LIMIT | 🔒🔒🔒 |
| 操作限制 | 只允许SELECT查询 | 🔒🔒🔒🔒 |
| 时间范围强制 | 必须包含time_range | 🔒🔒🔒 |
| 敏感信息保护 | 环境变量管理 | 🔒🔒🔒🔒 |

## 📈 性能优化

### 查询性能优化
- **智能索引建议**: 基于查询模式推荐最优索引
- **查询缓存**: 频繁查询的结果缓存
- **批量处理**: 大数据集的流式处理
- **异步执行**: FastAPI异步查询处理

### 系统性能监控
- 查询执行时间统计
- 数据库连接池监控
- 内存使用情况跟踪
- API响应时间分析

## 🧪 质量保证

### 自动化测试体系
```python
# self_check.py - 质量保证系统
def main():
    test_cases = [
        "探测设备质量分析测试",
        "目标节点性能评估测试", 
        "地区覆盖质量分析测试"
    ]
    # 自动化执行测试用例
    # 生成质量评估报告
    # 异常检测和回归测试
```

### 测试覆盖场景
- ✅ 探测设备质量分析 (hostname + task_name)
- ✅ 目标节点性能评估 (target_node + task_name)  
- ✅ 地区覆盖质量分析 (target_node + src_isp + src_province)
- ✅ 智能引擎质量检查 (SQL生成 + 分析质量)

## 🚀 智能引擎升级 (2024.12)

### 升级前后对比
| 维度 | 升级前 | 升级后 |
|------|--------|--------|
| **SQL生成** | 8种固定聚合模式 | LLM动态生成，支持复杂查询 |
| **结果分析** | 4种固定模板 | 深度理解，个性化分析 |
| **质量保障** | 基础验证 | 4维质量评分系统 |
| **用户体验** | 格式化输出 | Markdown渲染，专业报告 |

### 新增核心模块
1. **IntelligentSQLGenerator**: 基于LLM的SQL生成器
2. **IntelligentAnalyzer**: 多维度数据洞察分析器
3. **QueryQualityGuard**: 查询质量保障系统
4. **IntelligentQueryEngine**: 统一的智能查询执行引擎

### 配置部署
```bash
# 渐进式部署策略
ENABLE_INTELLIGENT_ENGINE=false    # 兼容模式（默认）
ENABLE_INTELLIGENT_ENGINE=true     # 智能引擎启用
INTELLIGENT_ENGINE_FALLBACK=false  # 完全智能模式
```

## 📋 使用场景示例

### 核心查询场景
1. **探测设备质量分析**
   ```
   输入: "统计近1h，发起探测的探测设备(hostname)区分不同的任务(task_name）统计，分析这些设备的平均丢包和rtt情况"
   输出: 质量最好/最差的TOP3设备 + 性能指标 + 优化建议
   ```

2. **目标节点性能评估**
   ```
   输入: "统计近1h的探测目标节点(target_node)丢包情况，区分不同的任务(task_name）统计"
   输出: 按丢包率排序的节点列表 + 任务对比 + 选择建议
   ```

3. **地区覆盖质量分析**
   ```
   输入: "统计近1h，各个目标节点(target_node)覆盖浙江电信(chinatelecom)浙江(zhejiang)的丢包情况"
   输出: 浙江电信覆盖排名 + TOP3优质节点 + 质量指标
   ```

## 🔧 开发指南

### 代码规范
- **卫语句设计**: 提前返回，减少嵌套层级
- **类型注解**: 完整的函数签名和返回值类型
- **错误处理**: 完善的异常捕获和日志记录
- **安全性**: 输入验证和SQL注入防护

### 扩展开发
1. **新增查询模式**: 修改 `simple_planner.py` 添加新的聚合规则
2. **优化分析逻辑**: 增强 `analyzer.py` 的分析深度和准确性
3. **图表类型扩展**: 在 `chart.py` 中添加新的可视化类型
4. **测试用例扩展**: 在 `tests/` 中添加更多测试场景

## 📞 项目信息

### 项目统计
- **核心代码行数**: 2,800+行
- **模块文件数**: 22个核心业务模块
- **API接口**: 6个REST接口
- **查询模式**: 从8种固定升级为动态生成
- **升级时间**: 2024年12月 - 智能引擎重大升级

### 技术支持
- **详细文档**: README.md, DEPLOYMENT.md, INTELLIGENT_ENGINE_UPGRADE.md
- **质量保证**: 自动化测试 + 质量评估系统
- **监控体系**: 性能监控 + 异常检测

---

> 💡 **给AI助手的提示**: 这个项目已经过完整的智能引擎升级，从传统的规则驱动系统升级为AI驱动的智能分析平台。在提供技术支持时，请注意项目的双重引擎特性（传统引擎 + 智能引擎），以及完善的配置管理和安全机制。