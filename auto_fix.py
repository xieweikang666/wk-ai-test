#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复所有依赖问题
"""
import subprocess
import sys
import os

def fix_huggingface_hub():
    """修复 huggingface_hub 版本"""
    print("="*70)
    print("修复 huggingface_hub 版本...")
    print("="*70)
    
    try:
        # 检查当前版本
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "huggingface-hub"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # 检查版本
            version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
            if version_line:
                version = version_line[0].split(':')[1].strip()
                if version == "0.16.4":
                    print(f"✅ huggingface_hub 版本正确: {version}")
                    return True
        
        # 卸载并重新安装
        print("1. 卸载当前 huggingface_hub...")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "huggingface-hub"],
            capture_output=True,
            text=True
        )
        
        print("2. 安装兼容版本 huggingface_hub==0.16.4...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface-hub==0.16.4", "--no-deps"],
            text=True
        )
        
        if result.returncode == 0:
            print("✅ huggingface_hub 修复成功")
            return True
        else:
            print("❌ huggingface_hub 修复失败")
            return False
    except Exception as e:
        print(f"❌ 修复过程出错: {e}")
        return False


def verify_imports():
    """验证导入"""
    print("\n" + "="*70)
    print("验证修复...")
    print("="*70)
    
    errors = []
    
    # 验证 huggingface_hub
    try:
        from huggingface_hub import cached_download
        print("  ✓ huggingface_hub.cached_download 可以导入")
    except ImportError as e:
        print(f"  ❌ huggingface_hub.cached_download 导入失败: {e}")
        errors.append("huggingface_hub")
    
    # 验证 sentence_transformers
    try:
        from sentence_transformers import SentenceTransformer
        print("  ✓ sentence_transformers 可以导入")
    except ImportError as e:
        print(f"  ❌ sentence_transformers 导入失败: {e}")
        errors.append("sentence_transformers")
    
    # 验证 agent.rag
    try:
        from agent.rag import get_retriever
        print("  ✓ agent.rag 可以导入")
    except ImportError as e:
        print(f"  ❌ agent.rag 导入失败: {e}")
        errors.append("agent.rag")
    
    # 验证 agent.llm
    try:
        from agent.llm import get_llm_client
        llm = get_llm_client()
        print("  ✓ agent.llm 可以初始化和导入")
    except Exception as e:
        print(f"  ❌ agent.llm 初始化失败: {e}")
        print(f"     提示: 这可能是环境变量中的代理设置导致的")
        print(f"     可以尝试: unset HTTP_PROXY HTTPS_PROXY")
        errors.append("agent.llm")
    
    if errors:
        print(f"\n❌ 仍有 {len(errors)} 个模块无法正常导入")
        return False
    else:
        print("\n✅ 所有模块验证通过")
        return True


def main():
    """主函数"""
    print("\n" + "="*70)
    print("自动修复依赖问题")
    print("="*70)
    print()
    
    # 修复 huggingface_hub
    if not fix_huggingface_hub():
        print("\n❌ 修复失败")
        return 1
    
    # 验证修复
    if verify_imports():
        print("\n" + "="*70)
        print("✅ 所有问题已修复！")
        print("="*70)
        print("\n可以运行以下命令验证:")
        print("  python3 test_startup.py")
        return 0
    else:
        print("\n" + "="*70)
        print("⚠️  部分问题已修复，但仍有错误")
        print("="*70)
        print("\n请检查错误信息，或运行:")
        print("  python3 install_deps.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())

