#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复依赖版本问题
"""
import subprocess
import sys

def fix_huggingface_hub():
    """修复 huggingface_hub 版本"""
    print("修复 huggingface_hub 版本...")
    print("="*70)
    
    try:
        # 卸载新版本
        print("1. 卸载当前 huggingface_hub...")
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "huggingface_hub"],
            text=True
        )
        
        # 安装兼容版本
        print("2. 安装兼容版本 huggingface_hub==0.16.4...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface_hub==0.16.4"],
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


def verify_fix():
    """验证修复"""
    print("\n验证修复...")
    print("="*70)
    
    try:
        from huggingface_hub import cached_download
        print("✅ cached_download 可以正常导入")
        return True
    except ImportError as e:
        print(f"❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    print("="*70)
    print("依赖修复脚本")
    print("="*70)
    print()
    
    if fix_huggingface_hub():
        if verify_fix():
            print("\n" + "="*70)
            print("✅ 依赖修复成功！")
            print("="*70)
            print("\n可以运行以下命令验证:")
            print("  python3 test_startup.py")
            return 0
        else:
            print("\n⚠️  修复完成但验证失败，请手动检查")
            return 1
    else:
        print("\n❌ 依赖修复失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())


