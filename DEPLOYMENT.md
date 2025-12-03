# 网络探测数据 AI 分析 Agent - 部署指南

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd wk-ai-test

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入实际的配置值
# 重要：必须设置 OPENAI_API_KEY 和 CLICKHOUSE_PASSWORD
```

### 3. 启动应用

#### Web 模式
```bash
python3 app.py --host 0.0.0.0 --port 8000
```

#### CLI 模式
```bash
# 直接提问
python3 app.py -q "统计近1h的网络质量"

# 运行自测
python3 self_check.py
```

## 📋 生产环境部署

### 1. 使用 Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python3", "app.py", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建和运行
docker build -t wk-ai-agent .
docker run -d --env-file .env -p 8000:8000 wk-ai-agent
```

### 2. 使用 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./static:/app/static
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped
```

### 3. 系统服务配置

```ini
# /etc/systemd/system/wk-ai-agent.service
[Unit]
Description=WK AI Agent Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/wk-ai-agent
Environment=PATH=/opt/wk-ai-agent/venv/bin
ExecStart=/opt/wk-ai-agent/venv/bin/python app.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用和启动服务
sudo systemctl enable wk-ai-agent
sudo systemctl start wk-ai-agent
```

## 🔧 开发环境配置

### 1. 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

### 2. 代码质量检查

```bash
# 代码格式化
black .

# 导入排序
isort .

# 类型检查
mypy agent/ config/ db/ utils/

# 安全检查
bandit -r .

# 代码风格检查
flake8 .
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=agent --cov-report=html

# 运行特定测试
pytest tests/test_agent/test_planner.py -v
```

### 4. Pre-commit 钩子

```bash
# 安装 pre-commit 钩子
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

## 📊 监控和日志

### 1. 日志配置

```bash
# 日志级别通过环境变量设置
export LOG_LEVEL=INFO

# 日志文件位置
logs/app.log          # 应用日志
logs/access.log       # 访问日志（如果启用）
```

### 2. 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 预期响应
{"status": "healthy", "clickhouse": "connected"}
```

### 3. 性能监控

建议集成以下监控工具：
- Prometheus + Grafana：指标监控
- ELK Stack：日志分析
- Sentry：错误追踪

## 🔒 安全注意事项

### 1. 环境变量管理

- ✅ **不要**将 `.env` 文件提交到版本控制
- ✅ **使用** 密钥管理服务（AWS Secrets Manager、HashiCorp Vault）
- ✅ **定期轮换** API 密钥和数据库密码

### 2. 网络安全

- ✅ **使用** HTTPS（在生产环境）
- ✅ **配置** 防火墙规则
- ✅ **启用** 访问日志和监控

### 3. 数据安全

- ✅ **定期备份** ClickHouse 数据
- ✅ **实现** 访问控制和权限管理
- ✅ **监控** 异常查询行为

## 🚨 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查 ClickHouse 连接
   curl -X POST "http://localhost:8000/health"
   ```

2. **LLM API 调用失败**
   ```bash
   # 检查环境变量
   env | grep OPENAI
   
   # 测试 API 连接
   python3 -c "from agent.llm import get_llm_client; print(get_llm_client())"
   ```

3. **权限问题**
   ```bash
   # 检查文件权限
   ls -la static/
   chmod 755 static/
   ```

### 日志分析

```bash
# 查看最新日志
tail -f logs/app.log

# 搜索错误
grep -i error logs/app.log

# 分析查询性能
grep "SQL" logs/app.log | tail -10
```

## 📈 性能优化建议

1. **数据库优化**
   - 添加适当的索引
   - 配置查询缓存
   - 优化查询语句

2. **应用优化**
   - 启用异步处理
   - 实现结果缓存
   - 使用连接池

3. **资源管理**
   - 配置合适的内存限制
   - 监控 CPU 和内存使用
   - 实现自动扩缩容

## 📞 支持和联系

- 项目文档：[项目 Wiki]
- 问题反馈：[GitHub Issues]
- 技术支持：[联系邮箱]