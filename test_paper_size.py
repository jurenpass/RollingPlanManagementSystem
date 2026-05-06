import sys
import os
import time
sys.path.append('g:\\newplan')
from furnace_order_manager import FurnaceOrderManager
import tkinter as tk

# 创建一个简单的测试
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

manager = FurnaceOrderManager(root)

# 测试处理一个计划文件
plan_file = 'G:\\newplan\\计划号\\D5147.xls'
print(f'测试处理文件: {plan_file}')

if os.path.exists(plan_file):
    start_time = time.time()
    manager.run_excel_macro_with_pandas(plan_file)
    end_time = time.time()
    print(f'处理时间: {end_time - start_time:.2f}秒')
else:
    print(f'文件不存在: {plan_file}')

root.destroy()
