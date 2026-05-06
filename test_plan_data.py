import sys
import os
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    print("开始测试计划数据...")
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # 刷新计划号列表
    print("刷新计划号列表...")
    window.refresh_plan_list()
    
    # 查看计划数据
    print("\n计划数据:")
    for item in window.plan_data:
        print(f"计划号: {item['plan_no']}, 状态: {item['status']}")
    
    # 查看无文件计划号
    no_file_plans = [item['plan_no'] for item in window.plan_data if item['status'] == '无文件']
    print(f"\n无文件计划号: {no_file_plans}")
    
    # 检查H5182的状态
    h5182_status = None
    for item in window.plan_data:
        if item['plan_no'] == 'H5182':
            h5182_status = item['status']
            break
    print(f"\nH5182的状态: {h5182_status}")
    
    # 检查计划号文件夹中的文件
    print(f"\n计划号文件夹: {window.plan_dir}")
    if os.path.exists(window.plan_dir):
        files = os.listdir(window.plan_dir)
        print(f"文件夹中的文件: {files}")
        # 检查是否存在H5182.xls文件
        h5182_file = os.path.join(window.plan_dir, "H5182.xls")
        if os.path.exists(h5182_file):
            print("H5182.xls文件存在")
        else:
            print("H5182.xls文件不存在")
    else:
        print("计划号文件夹不存在")
    
    print("\n测试完成")