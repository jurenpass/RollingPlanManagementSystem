


import sys
import os
import time
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    print("开始测试自动导出功能...")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 刷新计划号列表
    print("刷新计划号列表...")
    window.refresh_plan_list()
    
    # 查看无文件计划号
    no_file_plans = [item['plan_no'] for item in window.plan_data if item['status'] == '无文件']
    print(f"无文件计划号: {no_file_plans}")
    
    # 测试自动导出
    if no_file_plans:
        print(f"\n发现 {len(no_file_plans)} 个无文件计划号，开始自动导出...")
        
        # 调用自动导出函数
        print("\n开始执行自动导出操作...")
        window.auto_export()
        
        # 等待导出完成
        print("\n等待导出完成...")
        # 等待10秒让导出过程完成
        time.sleep(10)
    else:
        print("没有无文件计划号需要导出")
    
    print("\n测试完成")
    # 等待用户输入
    input("按回车键退出...")