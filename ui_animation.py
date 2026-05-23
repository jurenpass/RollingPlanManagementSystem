#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5 UI动画示例 - 钢卷生产流程动画
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QFrame, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem
)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QBrush, QColor, QFont, QPen


class AnimationWindow(QMainWindow):
    """带动画效果的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 UI动画示例 - 钢卷生产流程")
        self.resize(800, 600)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # 创建动画演示区域
        self.create_animation_area()
        
        # 创建控制按钮
        self.create_controls()
        
        # 初始化动画定时器
        self.init_animation_timer()
    
    def create_animation_area(self):
        """创建动画演示区域"""
        # 动画场景
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 760, 400)
        
        # 背景
        self.scene.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # 轨道路径
        path = self.scene.addRect(50, 350, 660, 20, QPen(Qt.NoPen), QBrush(QColor(192, 192, 192)))
        
        # 加热炉
        furnace = self.scene.addRect(280, 250, 120, 100, QPen(Qt.black), QBrush(QColor(255, 100, 100)))
        
        # 轧机
        mill = self.scene.addRect(450, 280, 80, 70, QPen(Qt.black), QBrush(QColor(100, 150, 255)))
        
        # 钢卷（带动画的对象）
        self.coil = QGraphicsRectItem(50, 320, 40, 30)
        self.coil.setPen(QPen(Qt.black))
        self.coil.setBrush(QBrush(QColor(0, 100, 200)))
        self.scene.addItem(self.coil)
        
        # 视图
        self.view = QGraphicsView(self.scene)
        self.view.setFixedHeight(420)
        self.layout.addWidget(self.view)
    
    def create_controls(self):
        """创建控制按钮"""
        self.start_btn = QPushButton("开始动画")
        self.start_btn.clicked.connect(self.start_animation)
        
        self.pause_btn = QPushButton("暂停动画")
        self.pause_btn.clicked.connect(self.pause_animation)
        
        self.reset_btn = QPushButton("重置动画")
        self.reset_btn.clicked.connect(self.reset_animation)
        
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        
        self.layout.addLayout(btn_layout)
    
    def init_animation_timer(self):
        """初始化动画定时器"""
        self.timer = QTimer()
        self.timer.setInterval(30)  # 30ms 间隔
        self.timer.timeout.connect(self.update_animation)
        
        # 动画状态
        self.animation_running = False
        self.animation_progress = 0.0
    
    def update_animation(self):
        """更新动画"""
        self.animation_progress += 0.01
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 0.0
        
        # 根据进度计算钢卷位置
        progress = self.animation_progress
        
        if progress < 0.3:
            # 从起点移动到加热炉
            x = 50 + progress / 0.3 * 230
            y = 320 - progress / 0.3 * 70
        elif progress < 0.6:
            # 在加热炉中
            x = 280 + (progress - 0.3) / 0.3 * 170
            y = 250 + (progress - 0.3) / 0.3 * 30
        else:
            # 从轧机移动到终点
            x = 450 + (progress - 0.6) / 0.4 * 220
            y = 280 + (progress - 0.6) / 0.4 * 40
        
        self.coil.setPos(x, y)
    
    def start_animation(self):
        """开始动画"""
        if not self.animation_running:
            self.timer.start()
            self.animation_running = True
            print("动画开始")
    
    def pause_animation(self):
        """暂停动画"""
        if self.animation_running:
            self.timer.stop()
            self.animation_running = False
            print("动画暂停")
    
    def reset_animation(self):
        """重置动画"""
        self.timer.stop()
        self.animation_running = False
        self.animation_progress = 0.0
        self.coil.setPos(50, 320)
        print("动画重置")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimationWindow()
    window.show()
    sys.exit(app.exec_())
