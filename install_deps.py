#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动安装依赖脚本
"""
import subprocess
import sys
import os

def install_requirements():
    """安装 requirements.txt 中的依赖"""
    print("正在安装依赖...")
    print("="*70)
    
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    if not os.path.exists(requirements_file):
        print(f"❌ 找不到 requirements.txt: {requirements_file}")
        return False
    
    try:
        # 先安装 huggingface-hub 兼容版本（必须在 sentence-transformers 之前）
        print("1. 安装 huggingface-hub==0.16.4（兼容版本）...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface-hub==0.16.4"],
            text=True
        )
        
        # 使用 pip 安装，显示输出
        print("\n2. 安装其他依赖包（这可能需要几分钟）...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 依赖安装成功！")
            return True
        else:
            print(f"⚠️  依赖安装返回码: {result.returncode}")
            # 尝试单独安装 sentence_transformers
            print("\n尝试单独安装 sentence-transformers...")
            result2 = subprocess.run(
                [sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"],
                text=True
            )
            if result2.returncode == 0:
                print("✅ sentence-transformers 安装成功！")
                return True
            return False
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        # 尝试单独安装 sentence_transformers
        try:
            print("\n尝试单独安装 sentence_transformers...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"],
                text=True
            )
        except:
            pass
        return False

def check_imports():
    """检查关键模块是否可以导入"""
    print("\n检查关键模块...")
    print("="*70)
    
    modules = [
        "fastapi",
        "openai",
        "clickhouse_driver",
        "pandas",
        "matplotlib",
        "sentence_transformers",
        "faiss"
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ❌ {module} (未安装)")
            failed.append(module)
    
    if failed:
        print(f"\n❌ 以下模块未安装: {', '.join(failed)}")
        
        # 如果 sentence_transformers 未安装，尝试单独安装
        if "sentence_transformers" in failed:
            print("\n尝试单独安装 sentence-transformers...")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"],
                    text=True
                )
                if result.returncode == 0:
                    print("✅ sentence-transformers 安装成功！")
                    # 再次检查
                    try:
                        __import__("sentence_transformers")
                        print("✅ sentence-transformers 验证成功")
                        failed.remove("sentence_transformers")
                    except ImportError:
                        pass
            except Exception as e:
                print(f"⚠️  单独安装失败: {e}")
        
        if failed:
            print(f"\n仍有未安装的模块: {', '.join(failed)}")
            print("请手动运行: pip install -r requirements.txt")
            return False
        else:
            print("\n✅ 所有关键模块已安装")
            return True
    else:
        print("\n✅ 所有关键模块已安装")
        return True

if __name__ == "__main__":
    print("="*70)
    print("依赖安装脚本")
    print("="*70)
    print()
    
    # 安装依赖
    if not install_requirements():
        sys.exit(1)
    
    # 检查导入
    if not check_imports():
        print("\n⚠️  部分模块未安装，请手动运行:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("✅ 所有依赖已安装完成！")
    print("="*70)
    
    # 检查是否有 huggingface_hub 版本问题
    try:
        from huggingface_hub import cached_download
        print("\n✅ huggingface_hub 版本正常")
    except ImportError:
        print("\n⚠️  检测到 huggingface_hub 版本问题")
        print("   运行以下命令修复:")
        print("   python3 fix_dependencies.py")
    
    print("\n可以运行以下命令进行测试:")
    print("  python3 verify.py      # 验证代码")
    print("  python3 cli.py          # 运行 CLI 测试")

