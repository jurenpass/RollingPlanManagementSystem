# 粗轧主画面窗口 - 使用 Qt Designer 设计的 UI 文件
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QTimer
from PyQt5.Qt import QByteArray
from rm_main_screen_designer_ui import Ui_MainWindow

class RMMainWindow(QMainWindow):
    """粗轧主画面窗口 - 使用 Qt Designer 设计"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 使用 Qt Designer 生成的 UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 设置窗口标题
        self.setWindowTitle("粗轧主画面")

        # 机架列表
        self.stands = [
            self.ui.standRT1,
            self.ui.standRT2,
            self.ui.standRT3,
            self.ui.standRT4,
            self.ui.standRT5,
            self.ui.standRT6,
            self.ui.standRT7,
            self.ui.standRT8
        ]

        # 动画状态
        self.stand_animations = []
        self.animation_timer = None
        self.is_running = False

        # 连接按钮信号
        self.connect_buttons()

        # 启动轧机动画
        self.start_mill_animation()

    def start_mill_animation(self):
        """启动轧机机架运行动画"""
        if self.is_running:
            return

        self.is_running = True

        # 为每个机架创建颜色闪烁动画
        for i, stand in enumerate(self.stands):
            # 创建向上扩展的动画（模拟轧件通过）
            expand_animation = QPropertyAnimation(stand, QByteArray(b"geometry"))
            expand_animation.setDuration(500)
            expand_animation.setEasingCurve(QEasingCurve.InOutQuad)

            # 起始位置和结束位置
            original_geo = stand.geometry()
            expanded_geo = QRect(
                original_geo.x() - 2,
                original_geo.y() - 2,
                original_geo.width() + 4,
                original_geo.height() + 4
            )

            expand_animation.setStartValue(original_geo)
            expand_animation.setKeyValueAt(0.5, expanded_geo)
            expand_animation.setEndValue(original_geo)

            # 设置延迟，让动画依次进行
            delay = i * 100
            QTimer.singleShot(delay, lambda a=expand_animation: a.start())

            self.stand_animations.append(expand_animation)

        # 创建颜色脉冲动画的定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.pulse_stand_colors)
        self.animation_timer.start(2000)

    def pulse_stand_colors(self):
        """机架颜色脉冲效果"""
        for stand in self.stands:
            current_style = stand.styleSheet()
            if "#30b030" in current_style:
                # 变亮
                stand.setStyleSheet("background-color: #50d050; border: 1px solid #008000;")
            else:
                # 恢复正常
                stand.setStyleSheet("background-color: #30b030; border: 1px solid #008000;")

    def stop_mill_animation(self):
        """停止轧机动画"""
        self.is_running = False
        if self.animation_timer:
            self.animation_timer.stop()
        for animation in self.stand_animations:
            animation.stop()
        self.stand_animations.clear()

    def connect_buttons(self):
        """连接按钮的点击信号"""
        self.ui.millModeButton.clicked.connect(self.toggle_mill_animation)

    def toggle_mill_animation(self):
        """切换轧机动画状态"""
        if self.is_running:
            self.stop_mill_animation()
            self.ui.millModeButton.setText("Mill Mode - Stopped")
        else:
            self.start_mill_animation()
            self.ui.millModeButton.setText("Mill Mode - Running")

# 测试代码
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = RMMainWindow()
    window.show()
    sys.exit(app.exec_())