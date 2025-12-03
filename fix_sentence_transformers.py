#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单独安装 sentence-transformers
"""
import subprocess
import sys

def install_sentence_transformers():
    """安装 sentence-transformers"""
    print("正在安装 sentence-transformers...")
    print("="*70)
    
    try:
        # 尝试安装
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"],
            text=True
        )
        
        if result.returncode == 0:
            print("✅ sentence-transformers 安装成功！")
            
            # 验证安装
            try:
                import sentence_transformers
                print(f"✅ 验证成功，版本: {sentence_transformers.__version__}")
                return True
            except ImportError:
                print("⚠️  安装完成但导入失败，可能需要重启 Python")
                return False
        else:
            print("❌ 安装失败")
            print("\n尝试使用其他方法安装...")
            
            # 尝试不指定版本
            result2 = subprocess.run(
                [sys.executable, "-m", "pip", "install", "sentence-transformers"],
                text=True
            )
            
            if result2.returncode == 0:
                print("✅ sentence-transformers 安装成功（未指定版本）！")
                return True
            else:
                print("❌ 所有安装方法都失败了")
                print("\n请手动运行:")
                print("  pip install sentence-transformers")
                return False
                
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if install_sentence_transformers():
        print("\n" + "="*70)
        print("✅ 安装完成！可以运行 python3 verify.py 验证")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ 安装失败，请手动安装:")
        print("  pip install sentence-transformers")
        print("="*70)
        sys.exit(1)

