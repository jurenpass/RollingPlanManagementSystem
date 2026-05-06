import sys
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    print('=== 开始测试无文件计划号明细导出 ===')
    print(f'无文件计划号: {[item["plan_no"] for item in window.plan_data if item["status"] == "无文件"]}')
    print(f'plan_detail_export 坐标: {window.coordinates.get("plan_detail_export")}')
    print('=== 测试完成 ===')
    app.quit()
