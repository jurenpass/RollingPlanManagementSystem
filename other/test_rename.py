import furnace_order_manager
import tkinter as tk

# 创建Tkinter根窗口
root = tk.Tk()
root.withdraw()  # 隐藏窗口

# 创建应用实例
app = furnace_order_manager.FurnaceOrderManager(root)

# 测试文件重命名功能
print("开始测试文件重命名功能...")
app.scan_and_rename_plan_files()
print("测试完成")

# 退出
root.destroy()