#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行轧制计划管理系统
"""

import sys
import traceback
import os

# 确保当前目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== 开始测试运行轧制计划管理系统 ===")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")
print(f"文件路径: {os.path.abspath('furnace_order_manager_pyqt5.py')}")
print(f"文件是否存在: {os.path.exists('furnace_order_manager_pyqt5.py')}")

# 尝试导入模块
print("\n=== 尝试导入模块 ===")
try:
    import furnace_order_manager_pyqt5
    print("OK 模块导入成功")
    
    # 尝试创建应用
    print("\n=== 尝试创建应用 ===")
    app = furnace_order_manager_pyqt5.QApplication(sys.argv)
    print("OK 应用创建成功")
    
    # 尝试创建主窗口
    print("\n=== 尝试创建主窗口 ===")
    window = furnace_order_manager_pyqt5.MainWindow()
    print("OK 主窗口创建成功")
    
    # 尝试显示窗口
    print("\n=== 尝试显示窗口 ===")
    window.show()
    print("OK 窗口显示成功")
    
    # 运行应用
    print("\n=== 运行应用 ===")
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"ERROR 错误: {str(e)}")
    print("\n=== 详细错误信息 ===")
    traceback.print_exc()
    
    # 尝试显示错误对话框
    try:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "错误", f"启动程序失败: {str(e)}")
    except Exception as msgbox_error:
        print(f"ERROR 显示错误对话框失败: {str(msgbox_error)}")

print("=== 测试运行结束 ===")
