#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有依赖库是否安装
"""

import sys
import subprocess

def check_module(module_name, import_name=None):
    """检查模块是否可导入"""
    if import_name is None:
        import_name = module_name

    try:
        __import__(import_name)
        print(f"OK {module_name}")
        return True
    except ImportError:
        print(f"MISSING {module_name}")
        return False

print("=" * 60)
print("检查依赖库安装状态")
print("=" * 60)

# GUI相关
check_module("PyQt5", "PyQt5")

# Excel相关
check_module("xlrd")
check_module("xlwt")
check_module("xlutils")

# 数据处理
check_module("pandas")
check_module("numpy")

# 自动化相关
check_module("pyautogui")
check_module("pyperclip")
check_module("pymsgbox")
check_module("pyscreeze")
check_module("Pillow", "PIL")

# Windows API
check_module("pywin32")

print("=" * 60)
print("检查完成")
print("=" * 60)

# 尝试使用 pip list 显示所有已安装的包
print("\n已安装的相关包:")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    lines = result.stdout.split('\n')
    keywords = ['PyQt', 'xlrd', 'xlwt', 'xlutils', 'pandas', 'numpy',
                'pyautogui', 'pyperclip', 'pymsgbox', 'pyscreeze', 
                'Pillow', 'pywin32', 'PIL']
    for line in lines:
        for kw in keywords:
            if kw.lower() in line.lower():
                print(line)
                break
except Exception as e:
    print(f"获取包列表失败: {e}")