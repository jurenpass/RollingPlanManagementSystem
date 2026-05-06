import sys
from PyQt5.QtWidgets import QApplication
sys.path.append('g:\newplan')
from furnace_order_manager_pyqt5 import MainWindow

if __name__ == "__main__":
    print("开始运行自动导出功能...")
    app = QApplication(sys.argv)
    window = MainWindow()
    print("初始化完成，开始执行自动导出...")
    # 执行自动导出功能，不等待，让它自己运行完成
    window.auto_export(from_main_window=False)
    # 进入事件循环，让程序继续运行
    app.exec_()