# 项目启动检查清单

## 快速验证步骤

### 1. 检查依赖
```bash
python3 test_startup.py
```

### 2. 验证代码
```bash
python3 verify.py
```

### 3. 测试 CLI 启动
```bash
python3 cli.py --help
```

### 4. 测试服务启动（不实际运行）
```bash
python3 -c "from app import app; print('FastAPI 应用导入成功')"
```

## 常见问题修复

### 问题 1: sentence-transformers 未安装
```bash
python3 fix_sentence_transformers.py
```

### 问题 2: 依赖缺失
```bash
python3 install_deps.py
```

### 问题 3: 导入错误
运行 `python3 test_startup.py` 查看具体错误信息

## 启动方式

### CLI 模式（推荐用于测试）
```bash
python3 cli.py -q "你的问题"
```

### 服务模式
```bash
python3 app.py
# 或
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 验证成功标志

✅ 所有模块可以正常导入
✅ 所有模块可以正常初始化
✅ FastAPI 应用可以正常导入
✅ CLI 工具可以正常导入
✅ 可以运行 `python3 cli.py --help` 看到帮助信息


