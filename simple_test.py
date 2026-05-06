#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import traceback

print("Python version:", sys.version)
print("sys.path:", sys.path)

print("\nTrying to import PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    print("PyQt5 imported successfully")
except Exception as e:
    print("Error importing PyQt5:", e)
    traceback.print_exc()

print("\nTrying to import xlrd...")
try:
    import xlrd
    print("xlrd imported successfully")
except Exception as e:
    print("Error importing xlrd:", e)
    traceback.print_exc()

print("\nTrying to import furnace_order_manager_pyqt5...")
try:
    import furnace_order_manager_pyqt5
    print("furnace_order_manager_pyqt5 imported successfully")
except Exception as e:
    print("Error importing furnace_order_manager_pyqt5:", e)
    traceback.print_exc()

print("\nTest completed")
