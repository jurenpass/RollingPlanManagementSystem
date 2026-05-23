import sys
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi

class MainFrame(QFrame):
    def __init__(self):
        super().__init__()
        # 加载UI文件
        loadUi('untitled.ui', self)
        
        # 设置窗口标题
        self.setWindowTitle("自适应窗口 - 1920x1080")
        
        # 让窗口自动最大化
        self.showMaximized()
        
        # 确保布局能够自适应窗口大小
        self.setAutoFillBackground(True)
        
        # 可以在这里添加更多自定义功能
        self.setupButtons()
    
    def setupButtons(self):
        """给按钮添加点击事件（可选）"""
        # 示例：给所有按钮添加点击事件
        for child in self.findChildren(QPushButton):
            child.clicked.connect(lambda: print(f"按钮被点击: {self.sender().objectName()}"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建窗口
    window = MainFrame()
    window.show()
    
    # 进入主循环
    sys.exit(app.exec_())