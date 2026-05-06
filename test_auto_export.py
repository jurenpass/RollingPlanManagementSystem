import sys
import time
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    print("开始运行自动导出功能...")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("初始化完成，开始执行自动导出...")
    window.auto_export(from_main_window=False)
    # 等待自动导出功能完成，最多等待60秒
    print("等待自动导出功能完成...")
    for i in range(60):
        time.sleep(1)
    print("自动导出功能执行完成")
    app.quit()
