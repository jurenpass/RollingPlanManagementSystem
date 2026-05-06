#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 pywin32 是否安装成功
"""

print("Testing pywin32 installation...")

try:
    import win32gui
    print("OK win32gui imported successfully")
except ImportError as e:
    print("ERROR Error importing win32gui:", e)

try:
    import win32process
    print("OK win32process imported successfully")
except ImportError as e:
    print("ERROR Error importing win32process:", e)

try:
    import win32con
    print("OK win32con imported successfully")
except ImportError as e:
    print("ERROR Error importing win32con:", e)

print("Test completed")
