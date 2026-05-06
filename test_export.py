import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    print("开始测试导出功能...")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 刷新计划号列表
    print("刷新计划号列表...")
    window.refresh_plan_list()
    
    # 查看无文件计划号
    no_file_plans = [item['plan_no'] for item in window.plan_data if item['status'] == '无文件']
    print(f"无文件计划号: {no_file_plans}")
    
    # 测试导出无文件计划号明细
    print("\n测试导出无文件计划号明细...")
    if no_file_plans:
        print(f"准备导出 {len(no_file_plans)} 个无文件计划号")
        for plan_no in no_file_plans:
            print(f"导出计划号: {plan_no}")
            # 获取导出计划明细按钮坐标
            plan_detail_export_btn = window.coordinates.get("plan_detail_export")
            if not plan_detail_export_btn:
                plan_detail_export_btn = [79, 859]  # 使用默认坐标
            print(f"导出计划明细按钮坐标: {plan_detail_export_btn}")
            # 测试导出
            # 注意：这里我们只测试逻辑，不实际执行导出操作
            print(f"模拟导出计划号 {plan_no}")
    else:
        print("没有无文件计划号需要导出")
    
    # 测试auto_export函数
    print("\n测试auto_export函数...")
    # 启用调试模式
    window.coordinates["debug_mode"] = True
    # 运行自动导出
    window.auto_export(from_main_window=False)
    
    # 进入事件循环，等待导出完成
    print("进入事件循环，等待导出完成...")
    app.exec_()
    
    print("\n测试完成")