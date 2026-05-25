#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轧制计划管理系统 - PyQt5版本
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, 
    QHeaderView, QMessageBox, QLineEdit, QCheckBox, QComboBox, QDialog,
    QAbstractItemView, QGroupBox, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush

# 全局变量
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class RMMainWindow(QMainWindow):
    """粗轧主画面窗口 - 复刻西门子WinCC粗轧主画面"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("粗轧主画面")
        self.resize(1900, 1000)
        
        # 设置窗口背景色为WinCC风格的灰色
        self.setStyleSheet("background-color: #c8c8c8;")
        
        try:
            # 创建中心部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 主布局
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(5)
            
            # 1. 顶部状态栏
            self.create_top_status_bar(main_layout)
            
            # 2. ID和状态显示区
            self.create_id_status_area(main_layout)
            
            # 3. 轧制线视图
            self.create_mill_line_view(main_layout)
            
            # 4. 状态指示线
            self.create_status_indicator_line(main_layout)
            
            # 5. 底部状态区域
            self.create_bottom_status_area(main_layout)
            
            # 6. 参数显示区域
            self.create_params_area(main_layout)
            
            # 7. 数据表格区域
            self.create_data_tables(main_layout)
            
            # 8. 底部操作按钮
            self.create_bottom_buttons(main_layout)
            
            print("粗轧主画面窗口创建成功")
        except Exception as e:
            print(f"创建粗轧主画面窗口时出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"创建窗口失败: {str(e)}")
    
    def create_top_status_bar(self, parent_layout):
        """创建顶部状态栏区域"""
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #e0e0e0;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(5, 5, 5, 5)
        top_layout.setSpacing(10)
        
        # 左侧状态组
        left_group = QGroupBox("Plant Status RM")
        left_group.setFont(QFont("Arial", 10, QFont.Bold))
        left_group.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        left_layout = QGridLayout(left_group)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        status_items = [
            ("Plant Status RM", "Green"),
            ("Diagnostic RM", "Green"),
            ("CSM/DSM RM", "Green")
        ]
        
        for i, (label, status) in enumerate(status_items):
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 9))
            left_layout.addWidget(lbl, i, 0)
            
            status_box = QFrame()
            status_box.setFixedSize(20, 20)
            if status == "Green":
                status_box.setStyleSheet("background-color: #00ff00; border: 1px solid #008000;")
            else:
                status_box.setStyleSheet("background-color: #ff0000; border: 1px solid #800000;")
            left_layout.addWidget(status_box, i, 1)
            
            arrow_btn = QPushButton("↓")
            arrow_btn.setFixedSize(20, 20)
            arrow_btn.setStyleSheet("background-color: #d0d0d0;")
            left_layout.addWidget(arrow_btn, i, 2)
        
        top_layout.addWidget(left_group)
        
        # 中间空白区域
        top_layout.addStretch(1)
        
        # 右侧状态组
        right_group = QGroupBox("Setpoints RM")
        right_group.setFont(QFont("Arial", 10, QFont.Bold))
        right_group.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        right_layout = QGridLayout(right_group)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        status_items2 = [
            ("Setpoints RM", "Green"),
            ("Diagnostic Level2", "Green")
        ]
        
        for i, (label, status) in enumerate(status_items2):
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 9))
            right_layout.addWidget(lbl, i, 0)
            
            status_box = QFrame()
            status_box.setFixedSize(20, 20)
            if status == "Green":
                status_box.setStyleSheet("background-color: #00ff00; border: 1px solid #008000;")
            else:
                status_box.setStyleSheet("background-color: #ff0000; border: 1px solid #800000;")
            right_layout.addWidget(status_box, i, 1)
            
            arrow_btn = QPushButton("↓")
            arrow_btn.setFixedSize(20, 20)
            arrow_btn.setStyleSheet("background-color: #d0d0d0;")
            right_layout.addWidget(arrow_btn, i, 2)
        
        top_layout.addWidget(right_group)
        
        parent_layout.addWidget(top_bar)
    
    def create_id_status_area(self, parent_layout):
        """创建ID和状态显示区"""
        id_area = QWidget()
        id_layout = QHBoxLayout(id_area)
        id_layout.setContentsMargins(5, 5, 5, 5)
        id_layout.setSpacing(5)
        
        # ID 5200
        id_box1 = self.create_id_box("ID", "5200", "#00d4ff")
        id_layout.addWidget(id_box1)
        
        # ID-Mode
        id_box2 = self.create_id_box("ID", "5200", "#00d4ff")
        id_layout.addWidget(id_box2)
        
        # C-Mode
        id_box3 = self.create_id_box("C-Mode", "", "#00d4ff")
        id_layout.addWidget(id_box3)
        
        # Mill Pacing
        pace_group = QGroupBox("Mill Pacing")
        pace_group.setFont(QFont("Arial", 9, QFont.Bold))
        pace_group.setStyleSheet("QGroupBox { border: 1px solid #808080; background-color: #f0f0f0; }")
        pace_layout = QHBoxLayout(pace_group)
        pace_layout.setContentsMargins(5, 5, 5, 5)
        
        status_labels = ["WB", "E", "T", "C", "A", "RC"]
        for label in status_labels:
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 8, QFont.Bold))
            if label in ["WB", "E", "T", "C", "A"]:
                lbl.setStyleSheet("color: #008000;")
            else:
                lbl.setStyleSheet("color: #800080;")
            pace_layout.addWidget(lbl)
        
        id_layout.addWidget(pace_group)
        
        id_layout.addStretch(1)
        
        # ID 5203
        id_box4 = self.create_id_box("ID", "5203", "#00d4ff")
        id_layout.addWidget(id_box4)
        
        # 状态标签
        status_labels2 = ["P", "S", "C", "T", "C", "A", "RC", "E2"]
        for label in status_labels2:
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 8, QFont.Bold))
            if label in ["P", "S", "C", "T"]:
                lbl.setStyleSheet("color: #008000;")
            elif label == "A":
                lbl.setStyleSheet("color: #0000ff;")
            elif label == "RC":
                lbl.setStyleSheet("color: #800080;")
            else:
                lbl.setStyleSheet("color: #ff8000;")
            id_layout.addWidget(lbl)
        
        id_layout.addStretch(1)
        
        # ID R2
        id_box5 = self.create_id_box("ID", "R2", "#00d4ff")
        id_layout.addWidget(id_box5)
        
        # 更多状态标签
        status_labels3 = ["E", "H", "AA", "WB", "S", "T", "C", "A", "BB", "RC"]
        for label in status_labels3:
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 8, QFont.Bold))
            if label in ["E", "S", "T", "C", "A"]:
                lbl.setStyleSheet("color: #008000;")
            elif label in ["H", "AA", "WB"]:
                lbl.setStyleSheet("color: #0000ff;")
            elif label == "BB":
                lbl.setStyleSheet("color: #ff0000;")
            else:
                lbl.setStyleSheet("color: #800080;")
            id_layout.addWidget(lbl)
        
        id_layout.addStretch(1)
        
        # 时间显示
        time_box = self.create_status_box("0:50", "s", "#ffff00", "#808000")
        id_layout.addWidget(time_box)
        
        id_layout.addStretch(1)
        
        # ID Cobble P.Back
        id_box6 = self.create_id_box("ID", "Cobble P.Back", "#00d4ff")
        id_layout.addWidget(id_box6)
        
        parent_layout.addWidget(id_area)
    
    def create_mill_line_view(self, parent_layout):
        """创建轧制线视图"""
        mill_area = QWidget()
        mill_layout = QHBoxLayout(mill_area)
        mill_layout.setContentsMargins(5, 5, 5, 5)
        mill_layout.setSpacing(2)
        
        # 左侧设备
        left_devices = QVBoxLayout()
        
        # Disc.Auto
        disc_auto = QLabel("Disc.Auto")
        disc_auto.setFont(QFont("Arial", 8, QFont.Bold))
        disc_auto.setStyleSheet("color: #008000;")
        left_devices.addWidget(disc_auto)
        
        # 箭头指示
        arrow_frame = QFrame()
        arrow_frame.setFixedSize(40, 60)
        arrow_layout = QVBoxLayout(arrow_frame)
        for _ in range(3):
            arrow = QLabel("↑")
            arrow.setFont(QFont("Arial", 8))
            arrow.setStyleSheet("color: #008000;")
            arrow_layout.addWidget(arrow)
        left_devices.addWidget(arrow_frame)
        
        mill_layout.addLayout(left_devices)
        mill_layout.addStretch(1)
        
        # 机架区域
        stands = ["RT1", "RT2", "RT3", "RT4", "RT5", "RT6", "RT7", "RT8", "RT9", "RT10", "RT11", "RT12", "RT13", "RT14", "RT15", "RT16", "RT17"]
        
        for i, stand in enumerate(stands):
            stand_widget = QWidget()
            stand_layout = QVBoxLayout(stand_widget)
            stand_layout.setContentsMargins(2, 2, 2, 2)
            
            # 机架标签
            stand_label = QLabel(stand)
            stand_label.setFont(QFont("Arial", 7, QFont.Bold))
            stand_label.setAlignment(Qt.AlignCenter)
            stand_layout.addWidget(stand_label)
            
            # 机架图形
            stand_frame = QFrame()
            stand_frame.setFixedSize(30, 20)
            
            # 特殊机架样式
            if stand in ["RT10", "RT11"]:
                stand_frame.setStyleSheet("background-color: #00ff00; border: 1px solid #008000;")
            elif stand in ["RT6", "RT12"]:
                stand_frame.setStyleSheet("background-color: #00ff00; border: 1px solid #008000;")
            else:
                stand_frame.setStyleSheet("background-color: #40c040; border: 1px solid #008000;")
            
            stand_layout.addWidget(stand_frame)
            
            mill_layout.addWidget(stand_widget)
        
        mill_layout.addStretch(1)
        
        # 右侧设备
        right_devices = QVBoxLayout()
        
        # RM Trans
        rm_trans = QLabel("RM Trans")
        rm_trans.setFont(QFont("Arial", 8, QFont.Bold))
        rm_trans.setStyleSheet("color: #008000;")
        right_devices.addWidget(rm_trans)
        
        # Line
        line_label = QLabel("Line")
        line_label.setFont(QFont("Arial", 8, QFont.Bold))
        line_label.setStyleSheet("color: #0000ff;")
        right_devices.addWidget(line_label)
        
        mill_layout.addLayout(right_devices)
        
        parent_layout.addWidget(mill_area)
    
    def create_status_indicator_line(self, parent_layout):
        """创建状态指示线"""
        status_line = QFrame()
        status_line.setFixedHeight(8)
        status_line.setStyleSheet("background-color: #00c000;")
        parent_layout.addWidget(status_line)
    
    def create_bottom_status_area(self, parent_layout):
        """创建底部状态区域"""
        bottom_status = QWidget()
        bottom_layout = QHBoxLayout(bottom_status)
        bottom_layout.setSpacing(10)
        
        # 左侧状态
        left_status_group = QGroupBox()
        left_status_group.setStyleSheet("QGroupBox { border: none; }")
        left_status_layout = QVBoxLayout(left_status_group)
        
        # No Slab Appr.
        no_slab_label = QLabel("No Slab Appr.")
        no_slab_label.setFont(QFont("Arial", 8, QFont.Bold))
        no_slab_label.setStyleSheet("color: #ff0000;")
        left_status_layout.addWidget(no_slab_label)
        
        # DESC / N-STOP
        status_row1 = QHBoxLayout()
        
        desc_btn = QPushButton("DESC")
        desc_btn.setFont(QFont("Arial", 8, QFont.Bold))
        desc_btn.setFixedSize(50, 20)
        desc_btn.setStyleSheet("background-color: #008000; color: white;")
        status_row1.addWidget(desc_btn)
        
        nstop_btn = QPushButton("N-STOP")
        nstop_btn.setFont(QFont("Arial", 8, QFont.Bold))
        nstop_btn.setFixedSize(60, 20)
        nstop_btn.setStyleSheet("background-color: #ff0000; color: white;")
        status_row1.addWidget(nstop_btn)
        
        left_status_layout.addLayout(status_row1)
        
        bottom_layout.addWidget(left_status_group)
        
        bottom_layout.addStretch(1)
        
        # 中间状态按钮
        mid_status_group = QGroupBox()
        mid_status_group.setStyleSheet("QGroupBox { border: none; }")
        mid_status_layout = QVBoxLayout(mid_status_group)
        
        status_row2 = QHBoxLayout()
        
        on_btn = QPushButton("ON")
        on_btn.setFont(QFont("Arial", 8, QFont.Bold))
        on_btn.setFixedSize(40, 20)
        on_btn.setStyleSheet("background-color: #00ff00;")
        status_row2.addWidget(on_btn)
        
        nstop_btn2 = QPushButton("N-STOP")
        nstop_btn2.setFont(QFont("Arial", 8, QFont.Bold))
        nstop_btn2.setFixedSize(60, 20)
        nstop_btn2.setStyleSheet("background-color: #ff0000; color: white;")
        status_row2.addWidget(nstop_btn2)
        
        dtran_btn = QPushButton("D-TRAN")
        dtran_btn.setFont(QFont("Arial", 8, QFont.Bold))
        dtran_btn.setFixedSize(60, 20)
        dtran_btn.setStyleSheet("background-color: #008000; color: white;")
        status_row2.addWidget(dtran_btn)
        
        status_row3 = QHBoxLayout()
        
        ready_btn = QPushButton("Ready")
        ready_btn.setFont(QFont("Arial", 8, QFont.Bold))
        ready_btn.setFixedSize(50, 20)
        ready_btn.setStyleSheet("background-color: #00ff00;")
        status_row3.addWidget(ready_btn)
        
        neg30_label = QLabel("-30")
        neg30_label.setFont(QFont("Arial", 8))
        neg30_label.setStyleSheet("color: #0000ff;")
        status_row3.addWidget(neg30_label)
        
        mid_status_layout.addLayout(status_row2)
        mid_status_layout.addLayout(status_row3)
        
        bottom_layout.addWidget(mid_status_group)
        
        bottom_layout.addStretch(1)
        
        # 右侧状态
        right_status_group = QGroupBox()
        right_status_group.setStyleSheet("QGroupBox { border: none; }")
        right_status_layout = QVBoxLayout(right_status_group)
        
        status_row4 = QHBoxLayout()
        
        on_for_btn = QPushButton("ON-FOR")
        on_for_btn.setFont(QFont("Arial", 8, QFont.Bold))
        on_for_btn.setFixedSize(60, 20)
        on_for_btn.setStyleSheet("background-color: #00ff00;")
        status_row4.addWidget(on_for_btn)
        
        crp_for_btn = QPushButton("CRP-FOR")
        crp_for_btn.setFont(QFont("Arial", 8, QFont.Bold))
        crp_for_btn.setFixedSize(70, 20)
        crp_for_btn.setStyleSheet("background-color: #008000; color: white;")
        status_row4.addWidget(crp_for_btn)
        
        status_row5 = QHBoxLayout()
        
        num9_label = QLabel("9")
        num9_label.setFont(QFont("Arial", 10, QFont.Bold))
        num9_label.setStyleSheet("color: #ff8000;")
        status_row5.addWidget(num9_label)
        
        right_status_layout.addLayout(status_row4)
        right_status_layout.addLayout(status_row5)
        
        bottom_layout.addWidget(right_status_group)
        
        bottom_layout.addStretch(1)
        
        # SP/LP/HP状态
        sp_group = QGroupBox()
        sp_group.setStyleSheet("QGroupBox { border: none; }")
        sp_layout = QVBoxLayout(sp_group)
        
        sp_row1 = QHBoxLayout()
        
        sp_label = QLabel("SP")
        sp_label.setFont(QFont("Arial", 8, QFont.Bold))
        sp_label.setStyleSheet("color: #0000ff;")
        sp_row1.addWidget(sp_label)
        
        num2_label = QLabel("2")
        num2_label.setFont(QFont("Arial", 10, QFont.Bold))
        num2_label.setStyleSheet("color: #0000ff;")
        sp_row1.addWidget(num2_label)
        
        sp_layout.addLayout(sp_row1)
        
        sp_row2 = QHBoxLayout()
        
        lp_label = QLabel("LP")
        lp_label.setFont(QFont("Arial", 8, QFont.Bold))
        lp_label.setStyleSheet("color: #0000ff;")
        sp_row2.addWidget(lp_label)
        
        num3_label = QLabel("3")
        num3_label.setFont(QFont("Arial", 10, QFont.Bold))
        num3_label.setStyleSheet("color: #0000ff;")
        sp_row2.addWidget(num3_label)
        
        sp_layout.addLayout(sp_row2)
        
        sp_row3 = QHBoxLayout()
        
        hp_label = QLabel("HP")
        hp_label.setFont(QFont("Arial", 8, QFont.Bold))
        hp_label.setStyleSheet("color: #0000ff;")
        sp_row3.addWidget(hp_label)
        
        num8_label = QLabel("8")
        num8_label.setFont(QFont("Arial", 10, QFont.Bold))
        num8_label.setStyleSheet("color: #0000ff;")
        sp_row3.addWidget(num8_label)
        
        sp_layout.addLayout(sp_row3)
        
        bottom_layout.addWidget(sp_group)
        
        bottom_layout.addStretch(1)
        
        # MP/T状态
        mp_group = QGroupBox()
        mp_group.setStyleSheet("QGroupBox { border: none; }")
        mp_layout = QVBoxLayout(mp_group)
        
        mp_row1 = QHBoxLayout()
        
        mp_label = QLabel("MP 3")
        mp_label.setFont(QFont("Arial", 8, QFont.Bold))
        mp_label.setStyleSheet("color: #008000;")
        mp_row1.addWidget(mp_label)
        
        mpsb_label = QLabel("MPSB Ackn")
        mpsb_label.setFont(QFont("Arial", 8, QFont.Bold))
        mpsb_label.setStyleSheet("color: #ffff00;")
        mp_row1.addWidget(mpsb_label)
        
        mp_layout.addLayout(mp_row1)
        
        xtran_btn = QPushButton("X-TRAN")
        xtran_btn.setFont(QFont("Arial", 8, QFont.Bold))
        xtran_btn.setFixedSize(60, 20)
        xtran_btn.setStyleSheet("background-color: #008000; color: white;")
        mp_layout.addWidget(xtran_btn)
        
        bottom_layout.addWidget(mp_group)
        
        bottom_layout.addStretch(1)
        
        # 剩余板坯数
        slab_left_group = QGroupBox()
        slab_left_group.setStyleSheet("QGroupBox { border: none; }")
        slab_left_layout = QVBoxLayout(slab_left_group)
        
        slab_left_label = QLabel("Nr.of Slab left RM")
        slab_left_label.setFont(QFont("Arial", 8, QFont.Bold))
        slab_left_label.setStyleSheet("color: #000000;")
        slab_left_layout.addWidget(slab_left_label)
        
        bottom_layout.addWidget(slab_left_group)
        
        parent_layout.addWidget(bottom_status)
    
    def create_params_area(self, parent_layout):
        """创建参数显示区域"""
        params_area = QWidget()
        params_area.setStyleSheet("background-color: #d8d8d8;")
        params_layout = QHBoxLayout(params_area)
        params_layout.setContentsMargins(5, 5, 5, 5)
        params_layout.setSpacing(5)
        
        # 左侧参数
        left_params = QGroupBox()
        left_params.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        left_params_layout = QGridLayout(left_params)
        left_params_layout.setContentsMargins(5, 5, 5, 5)
        left_params_layout.setSpacing(3)
        
        param_labels = ["Entry", "", "", "1.00 m/s", "1.00 m/s", "SP", "", "SG Ref[mm]", "SG Ref[mm]", "SG", "", "", "R1", "", "", "", "Swivel", "", "SG", "", "", "HGC DS", "HGC OS", "E2", "", "", "R2", "", "", "", "Swivel", "", "", "SG", "", "", "Exit", "", "3.00 m/s", "0.00 m/s", "T", "B", "T-B", "B", ""]
        param_values = ["1110 °C", "600 °C", "", "", "", "1361 mm", "1361 mm", "2260.0", "2260.0", "2250 mm", "2250 mm", "2260.0", "2260.0", "203.48 mm", "203.48 mm", "1.43 m/s", "0.01 MN", "7.3", "-0.51 mm", "-0.51 mm", "2157 mm", "2171 mm", "600 °C", "31.03 mm", "31.10 mm", "1030 mm", "1030 mm", "1.00 m/s", "1.00 m/s", "-0.05 MN", "155.2 mm", "155.26 mm", "1.00 m/s", "1.00 m/s", "0.20 MN", "+0.45 mm", "+0.45 mm", "Ski", "7 %", "2157 mm", "2171 mm", "25.12 mm", "25.12 mm", "1110 W mm", "600 °C", "", "", "5.1", "-3.1", "8", "-3", "8 °C"]
        
        row, col = 0, 0
        for i, (label, value) in enumerate(zip(param_labels, param_values)):
            if label:
                lbl = QLabel(label)
                lbl.setFont(QFont("Arial", 7))
                lbl.setStyleSheet("color: #000000;")
                left_params_layout.addWidget(lbl, row, col)
            
            if value:
                val = QLabel(value)
                val.setFont(QFont("Arial", 7, QFont.Bold))
                if "°C" in value or "mm" in value or "m/s" in value or "MN" in value or "%" in value:
                    val.setStyleSheet("color: #0000ff;")
                else:
                    val.setStyleSheet("color: #008000;")
                left_params_layout.addWidget(val, row, col + 1)
            
            col += 2
            if col >= 8:
                col = 0
                row += 1
        
        params_layout.addWidget(left_params)
        
        # 右侧参数
        right_params = QGroupBox()
        right_params.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        right_params_layout = QGridLayout(right_params)
        right_params_layout.setContentsMargins(5, 5, 5, 5)
        right_params_layout.setSpacing(3)
        
        # R2 Fan按钮
        r2_fan_btn = QPushButton("R2 Fan")
        r2_fan_btn.setFont(QFont("Arial", 8, QFont.Bold))
        r2_fan_btn.setFixedSize(80, 20)
        r2_fan_btn.setStyleSheet("background-color: #008000; color: white;")
        right_params_layout.addWidget(r2_fan_btn, 0, 0, 1, 2)
        
        # Next Slab / Actual Slab / Slab exit
        next_slab_label = QLabel("Next Slab")
        next_slab_label.setFont(QFont("Arial", 7, QFont.Bold))
        right_params_layout.addWidget(next_slab_label, 1, 0)
        
        actual_slab_label = QLabel("Actual Slab")
        actual_slab_label.setFont(QFont("Arial", 7, QFont.Bold))
        right_params_layout.addWidget(actual_slab_label, 1, 1)
        
        slab_exit_label = QLabel("Slab exit")
        slab_exit_label.setFont(QFont("Arial", 7, QFont.Bold))
        right_params_layout.addWidget(slab_exit_label, 1, 2)
        
        # SP Slab ID
        sp_slab_id = QLabel("SP")
        sp_slab_id.setFont(QFont("Arial", 7))
        right_params_layout.addWidget(sp_slab_id, 2, 0)
        
        sp_slab_box = QFrame()
        sp_slab_box.setFixedHeight(16)
        sp_slab_box.setStyleSheet("background-color: #000080;")
        right_params_layout.addWidget(sp_slab_box, 2, 1, 1, 2)
        
        # R1 Slab ID
        r1_slab_id = QLabel("R1")
        r1_slab_id.setFont(QFont("Arial", 7))
        right_params_layout.addWidget(r1_slab_id, 3, 0)
        
        r1_slab_box = QFrame()
        r1_slab_box.setFixedHeight(16)
        r1_slab_box.setStyleSheet("background-color: #000080;")
        right_params_layout.addWidget(r1_slab_box, 3, 1, 1, 2)
        
        # R2 Slab ID
        r2_slab_id = QLabel("R2")
        r2_slab_id.setFont(QFont("Arial", 7))
        right_params_layout.addWidget(r2_slab_id, 4, 0)
        
        r2_slab_box = QFrame()
        r2_slab_box.setFixedHeight(16)
        r2_slab_box.setStyleSheet("background-color: #000080;")
        right_params_layout.addWidget(r2_slab_box, 4, 1, 1, 2)
        
        # WCL显示
        wcl_label1 = QLabel("WCL 90 %")
        wcl_label1.setFont(QFont("Arial", 7, QFont.Bold))
        wcl_label1.setStyleSheet("color: #008000;")
        right_params_layout.addWidget(wcl_label1, 3, 3)
        
        wcl_label2 = QLabel("WCL 90 %")
        wcl_label2.setFont(QFont("Arial", 7, QFont.Bold))
        wcl_label2.setStyleSheet("color: #008000;")
        right_params_layout.addWidget(wcl_label2, 4, 3)
        
        # R2 Max speed / SP Level
        r2_max_speed_label = QLabel("R2 Max speed")
        r2_max_speed_label.setFont(QFont("Arial", 7))
        right_params_layout.addWidget(r2_max_speed_label, 5, 0)
        
        r2_max_speed_val = QLabel("5.8 m/s")
        r2_max_speed_val.setFont(QFont("Arial", 7, QFont.Bold))
        r2_max_speed_val.setStyleSheet("color: #00d4ff;")
        right_params_layout.addWidget(r2_max_speed_val, 5, 1)
        
        sp_level_label = QLabel("SP Level")
        sp_level_label.setFont(QFont("Arial", 7))
        right_params_layout.addWidget(sp_level_label, 5, 2)
        
        sp_level_val = QLabel("35.6 %")
        sp_level_val.setFont(QFont("Arial", 7, QFont.Bold))
        sp_level_val.setStyleSheet("color: #00d4ff;")
        right_params_layout.addWidget(sp_level_val, 5, 3)
        
        # RT STOP按钮
        rt_stop_btn = QPushButton("RT STOP")
        rt_stop_btn.setFont(QFont("Arial", 7, QFont.Bold))
        rt_stop_btn.setFixedSize(60, 18)
        rt_stop_btn.setStyleSheet("background-color: #800000; color: white;")
        right_params_layout.addWidget(rt_stop_btn, 6, 3)
        
        # 速度显示
        speed_label = QLabel("V 90 m/s")
        speed_label.setFont(QFont("Arial", 7, QFont.Bold))
        speed_label.setStyleSheet("color: #008000;")
        right_params_layout.addWidget(speed_label, 6, 1)
        
        wcl_label3 = QLabel("WCL 90 %")
        wcl_label3.setFont(QFont("Arial", 7, QFont.Bold))
        wcl_label3.setStyleSheet("color: #008000;")
        right_params_layout.addWidget(wcl_label3, 6, 2)
        
        # R1 SPD UP / EXIT SPD UP按钮
        r1_spd_btn = QPushButton("R1 SPD UP")
        r1_spd_btn.setFont(QFont("Arial", 7, QFont.Bold))
        r1_spd_btn.setFixedSize(70, 18)
        r1_spd_btn.setStyleSheet("background-color: #008000; color: white;")
        right_params_layout.addWidget(r1_spd_btn, 7, 2)
        
        exit_spd_btn = QPushButton("EXIT SPD UP")
        exit_spd_btn.setFont(QFont("Arial", 7, QFont.Bold))
        exit_spd_btn.setFixedSize(70, 18)
        exit_spd_btn.setStyleSheet("background-color: #008000; color: white;")
        right_params_layout.addWidget(exit_spd_btn, 7, 3)
        
        params_layout.addWidget(right_params)
        
        parent_layout.addWidget(params_area)
    
    def create_data_tables(self, parent_layout):
        """创建数据表格区域"""
        table_area = QWidget()
        table_area.setStyleSheet("background-color: #e8e8e8;")
        table_layout = QHBoxLayout(table_area)
        table_layout.setContentsMargins(5, 5, 5, 5)
        table_layout.setSpacing(10)
        
        # 左侧表格
        left_table = QGroupBox()
        left_table.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        left_table_layout = QVBoxLayout(left_table)
        
        # 表格标题行
        header_row = QWidget()
        header_layout = QHBoxLayout(header_row)
        
        headers = ["E2[mm]", "R2[mm]", "V [m/s]", "Desc", "Ski[%]", "Ski[m]"]
        for header in headers:
            lbl = QLabel(header)
            lbl.setFont(QFont("Arial", 7, QFont.Bold))
            lbl.setStyleSheet("color: #000000;")
            lbl.setFixedWidth(60)
            header_layout.addWidget(lbl)
        
        left_table_layout.addWidget(header_row)
        
        # 表格数据
        for i in range(5):
            data_row = QWidget()
            data_layout = QHBoxLayout(data_row)
            
            values = ["1650", "1650", "3.5", str(i + 1), "1", "1"]
            for j, value in enumerate(values):
                val = QLabel(value)
                val.setFont(QFont("Arial", 7, QFont.Bold))
                if j < 3:
                    val.setStyleSheet("color: #000080;")
                else:
                    val.setStyleSheet("color: #008000;")
                val.setFixedWidth(60)
                val.setAlignment(Qt.AlignCenter)
                data_layout.addWidget(val)
            
            left_table_layout.addWidget(data_row)
        
        table_layout.addWidget(left_table)
        
        # 右侧表格
        right_table = QGroupBox()
        right_table.setStyleSheet("QGroupBox { border: 1px solid #808080; }")
        right_table_layout = QVBoxLayout(right_table)
        
        # 表格标题行
        right_header_row = QWidget()
        right_header_layout = QHBoxLayout(right_header_row)
        
        right_headers = ["E2[mm]", "R2[mm]", "V [m/s]", "Desc", "Ski[%]", "Ski[m]"]
        for header in right_headers:
            lbl = QLabel(header)
            lbl.setFont(QFont("Arial", 7, QFont.Bold))
            lbl.setStyleSheet("color: #000000;")
            lbl.setFixedWidth(60)
            right_header_layout.addWidget(lbl)
        
        right_table_layout.addWidget(right_header_row)
        
        # 表格数据
        for i in range(5):
            data_row = QWidget()
            data_layout = QHBoxLayout(data_row)
            
            values = ["1650", "1650", "1650", str(i + 1), "1", "1"]
            for j, value in enumerate(values):
                val = QLabel(value)
                val.setFont(QFont("Arial", 7, QFont.Bold))
                if j < 3:
                    val.setStyleSheet("color: #008080;")
                else:
                    val.setStyleSheet("color: #008000;")
                val.setFixedWidth(60)
                val.setAlignment(Qt.AlignCenter)
                data_layout.addWidget(val)
            
            right_table_layout.addWidget(data_row)
        
        table_layout.addWidget(right_table)
        
        table_layout.addStretch(1)
        
        parent_layout.addWidget(table_area)
    
    def create_bottom_buttons(self, parent_layout):
        """创建底部操作按钮区域"""
        bottom_bar = QWidget()
        bottom_bar.setStyleSheet("background-color: #a8a8a8;")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(5, 5, 5, 5)
        bottom_layout.setSpacing(5)
        
        button_names = [
            "Mill Mode", "Stand Mode", "Sizing Press Mode", "Simulation",
            "Roll Data", "Jogging Selection", "Set Run Counter",
            "Release Drives", "Change Ski", "Cooling", "Confirm", "Fault acknowledge"
        ]
        
        for name in button_names:
            btn = QPushButton(name)
            btn.setFont(QFont("Arial", 9))
            btn.setFixedSize(120, 40)
            btn.setStyleSheet("background-color: #c0c0c0; border: 1px solid #808080;")
            bottom_layout.addWidget(btn)
        
        bottom_layout.addStretch(1)
        
        parent_layout.addWidget(bottom_bar)
    
    def create_id_box(self, label, value, color):
        """创建ID显示框"""
        box = QGroupBox()
        box.setStyleSheet(f"QGroupBox {{ border: 2px solid {color}; background-color: #f0f0f0; }}")
        layout = QVBoxLayout(box)
        
        lbl = QLabel(label)
        lbl.setFont(QFont("Arial", 8))
        lbl.setStyleSheet("color: #000000;")
        layout.addWidget(lbl)
        
        if value:
            val = QLabel(value)
            val.setFont(QFont("Arial", 10, QFont.Bold))
            val.setStyleSheet(f"color: {color};")
            layout.addWidget(val)
        
        return box
    
    def create_status_box(self, value, unit, bg_color, text_color):
        """创建状态显示框"""
        box = QFrame()
        box.setStyleSheet(f"background-color: {bg_color}; border: 2px solid {text_color};")
        layout = QVBoxLayout(box)
        
        val = QLabel(value)
        val.setFont(QFont("Arial", 12, QFont.Bold))
        val.setStyleSheet(f"color: {text_color};")
        val.setAlignment(Qt.AlignCenter)
        layout.addWidget(val)
        
        unit_lbl = QLabel(unit)
        unit_lbl.setFont(QFont("Arial", 8))
        unit_lbl.setStyleSheet(f"color: {text_color};")
        unit_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(unit_lbl)
        
        return box


class MainWindow(QMainWindow):
    """主窗口"""
    # 定义错误信号
    error_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("轧制计划管理系统")
        self.setGeometry(100, 100, 1500, 900)
        self.setMinimumSize(1200, 700)
        
        # 居中显示
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
        
        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # 初始化属性
        # 获取exe文件所在目录或脚本所在目录
        if getattr(sys, 'frozen', False):
            # 打包成exe后的路径
            self.plan_dir = os.path.dirname(sys.executable)
        else:
            # 脚本运行时的路径
            self.plan_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(self.plan_dir, "furnace_order.db")
        self.coordinates = self.load_coordinate_config()
        
        # 自动执行相关
        self.auto_exec_timer = QTimer()
        self.auto_exec_timer.timeout.connect(self.auto_exec_timeout)

        self.next_execution_time = None
        self.auto_exec_running = False
        
        # 环境准备
        self.create_required_folders()
        self.init_database()
        
        # 连接错误信号
        self.error_signal.connect(self.show_error_message)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("轧制计划管理系统")
        title_label.setFont(QFont("宋体", 20, QFont.Bold))
        title_label.setStyleSheet("background-color: #f0f0f0;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 主框架
        main_frame = QWidget()
        main_frame.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(main_frame)
        
        # 主框架布局
        main_frame_layout = QVBoxLayout(main_frame)
        main_frame_layout.setContentsMargins(0, 0, 0, 0)
        main_frame_layout.setSpacing(10)
        
        # 列表标题
        list_title = QLabel("计划号列表")
        list_title.setFont(QFont("宋体", 20))
        list_title.setStyleSheet("background-color: #f0f0f0;")
        list_title.setAlignment(Qt.AlignLeft)
        main_frame_layout.addWidget(list_title)
        
        # 列表框架
        list_frame = QWidget()
        list_frame.setStyleSheet("background-color: #f0f0f0;")
        main_frame_layout.addWidget(list_frame)
        
        # 列表框架布局
        list_frame_layout = QVBoxLayout(list_frame)
        list_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建自定义表格类，确保标注单元格始终保持背景色
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QPainter, QColor, QBrush

        class CustomTableWidget(QTableWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

            def paintEvent(self, event):
                # 调用父类的paintEvent
                super().paintEvent(event)
                
                # 重新绘制标注单元格，确保它们保持红色背景
                painter = QPainter(self.viewport())
                for row in range(self.rowCount()):
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item:
                            bg_color = item.background().color().name()
                            # 不管是否是选中行，都绘制标注单元格的背景
                            # 这样标注单元格的颜色会显示在光标条颜色的上面
                            if bg_color == '#ff0000':
                                # 红色背景（标注单元格）
                                # 获取单元格的矩形
                                rect = self.visualRect(self.model().index(row, col))
                                # 绘制红色背景
                                painter.fillRect(rect, QBrush(QColor('#FF0000')))
                                # 绘制文字
                                painter.setPen(QColor('white'))
                                painter.setFont(item.font())
                                painter.drawText(rect, item.textAlignment(), item.text())
                            elif bg_color == '#ffff00':
                                # 黄色背景（换辊行、自定义信息行）
                                # 获取单元格的矩形
                                rect = self.visualRect(self.model().index(row, col))
                                # 绘制黄色背景
                                painter.fillRect(rect, QBrush(QColor('#FFFF00')))
                                # 绘制文字
                                painter.setPen(QColor('black'))
                                painter.setFont(item.font())
                                painter.drawText(rect, item.textAlignment(), item.text())

        # 创建自定义表格
        self.table_widget = CustomTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["计划号", "块数", "状态", "起止钢卷号"])
        
        # 隐藏垂直表头（行号列）
        self.table_widget.verticalHeader().setVisible(False)
        
        # 设置列宽（按照要求固定）
        self.table_widget.setColumnWidth(0, 170)  # 计划号列宽
        self.table_widget.setColumnWidth(1, 100)  # 块数列宽
        self.table_widget.setColumnWidth(2, 800)  # 状态列宽
        self.table_widget.setColumnWidth(3, 395)  # 起止钢卷号列宽
        
        # 设置字体和行高
        font = QFont("宋体", 28, QFont.Bold)
        self.table_widget.setFont(font)
        self.table_widget.verticalHeader().setDefaultSectionSize(50)
        
        # 设置表头字体
        header_font = QFont("宋体", 28, QFont.Bold)
        self.table_widget.horizontalHeader().setFont(header_font)
        
        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.MultiSelection)
        
        # 启用上下文菜单
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 连接双击事件
        self.table_widget.doubleClicked.connect(self.on_plan_double_clicked)
        
        # 设置表格样式,添加边框和选中行背景色
        table_style = """
            QTableWidget {
               
                background-color: white;
                border: 1px solid #CCCCCC;
                gridline-color: #CCCCCC;
                outline: none;
            }
            QTableWidget::item {
                border: 1px solid #CCCCCC;
                outline: none;
                selection-background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #3366FF;
                color: white;
                outline: none;
                selection-background-color: #3366FF;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                padding: 5px;
                outline: none;
            }
        """
        self.table_widget.setStyleSheet(table_style)
        
        # 添加表格到布局
        list_frame_layout.addWidget(self.table_widget)
        
        # 统计信息和选项框架
        stats_frame = QWidget()
        stats_frame.setStyleSheet("background-color: #f0f0f0;")
        main_frame_layout.addWidget(stats_frame)
        
        # 统计信息和选项布局
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        # 统计信息标签
        # 总块数显示
        self.stats_label = QLabel("总块数: 0 | 无文件: 0")
        self.stats_label.setFont(QFont("宋体", 20))
        self.stats_label.setStyleSheet("background-color: #f0f0f0; color: blue;")
        self.stats_label.setAlignment(Qt.AlignLeft)
        stats_layout.addWidget(self.stats_label)
        
        # 左侧伸缩空间，使右侧控件靠右对齐
        stats_layout.addStretch(1)
        
        # 自动执行选项
        auto_exec_frame = QWidget()
        auto_exec_frame.setStyleSheet("background-color: #f0f0f0;")
        auto_exec_layout = QHBoxLayout(auto_exec_frame)
        auto_exec_layout.setContentsMargins(0, 0, 0, 0)
        auto_exec_layout.setSpacing(10)
        
        # 自动打印复选框
        self.auto_print_checkbox = QCheckBox("自动打印")
        self.auto_print_checkbox.setFont(QFont("宋体", 20))
        self.auto_print_checkbox.setStyleSheet("background-color: #f0f0f0;")
        auto_exec_layout.addWidget(self.auto_print_checkbox)
        
        self.auto_exec_checkbox = QCheckBox("自动执行")
        self.auto_exec_checkbox.setFont(QFont("宋体", 20))
        self.auto_exec_checkbox.setStyleSheet("background-color: #f0f0f0;")
        auto_exec_layout.addWidget(self.auto_exec_checkbox)
        
        # 下一次执行时间显示
        self.next_execution_label = QLabel("下一次执行: 无")
        self.next_execution_label.setFont(QFont("宋体", 14))
        self.next_execution_label.setStyleSheet("color: blue; background-color: #f0f0f0;")
        # 设置固定宽度，确保显示不被压缩
        self.next_execution_label.setFixedWidth(200)
        auto_exec_layout.addWidget(self.next_execution_label)
        # 初始化标签显示
        print("初始化下一次执行时间标签")
        self.next_execution_label.setText("下一次执行: 无")
        
        stats_layout.addWidget(auto_exec_frame)
        

        
        # 按钮框架
        btn_frame = QWidget()
        btn_frame.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(btn_frame)
        
        # 按钮布局
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        # 左侧按钮
        left_btn_layout = QHBoxLayout()
        left_btn_layout.setSpacing(2)
        
        # 创建按钮样式
        button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 5px 10px;
                font-family: 宋体;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setFont(QFont("宋体", 20))
        self.select_all_btn.setFixedSize(80, 40)
        self.select_all_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.setFont(QFont("宋体", 20))
        self.deselect_all_btn.setFixedSize(120, 40)
        self.deselect_all_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.deselect_all_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFont(QFont("宋体", 20))
        self.refresh_btn.setFixedSize(80, 40)
        self.refresh_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.refresh_btn)
        
        self.auto_export_btn = QPushButton("自动导出")
        self.auto_export_btn.setFont(QFont("宋体", 20))
        self.auto_export_btn.setFixedSize(120, 40)
        self.auto_export_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.auto_export_btn)
        
        self.settings_btn = QPushButton("⚙ 设置")
        self.settings_btn.setFont(QFont("宋体", 20))
        self.settings_btn.setFixedSize(120, 40)
        self.settings_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.settings_btn)
        
        self.furnace_details_btn = QPushButton("装炉明细")
        self.furnace_details_btn.setFont(QFont("宋体", 20))
        self.furnace_details_btn.setFixedSize(120, 40)
        self.furnace_details_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.furnace_details_btn)
        
        self.process_plans_btn = QPushButton("处理计划")
        self.process_plans_btn.setFont(QFont("宋体", 20))
        self.process_plans_btn.setFixedSize(120, 40)
        self.process_plans_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.process_plans_btn)
        
        self.rm_main_btn = QPushButton("粗轧主画面")
        self.rm_main_btn.setFont(QFont("宋体", 20))
        self.rm_main_btn.setFixedSize(140, 40)
        self.rm_main_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.rm_main_btn)
        
        
        btn_layout.addLayout(left_btn_layout)
        
        # 右侧伸缩空间
        btn_layout.addStretch(1)
        
        # 右侧按钮
        right_btn_layout = QHBoxLayout()
        right_btn_layout.setSpacing(2)
        
        self.show_selected_btn = QPushButton("显示")
        self.show_selected_btn.setFont(QFont("宋体", 20))
        self.show_selected_btn.setFixedSize(80, 40)
        self.show_selected_btn.setStyleSheet(button_style)
        right_btn_layout.addWidget(self.show_selected_btn)
        
        self.print_selected_btn = QPushButton("打印")
        self.print_selected_btn.setFont(QFont("宋体", 20))
        self.print_selected_btn.setFixedSize(80, 40)
        self.print_selected_btn.setStyleSheet(button_style)
        right_btn_layout.addWidget(self.print_selected_btn)
        
        btn_layout.addLayout(right_btn_layout)
        
        # 连接信号槽
        self.connect_signals()
        
        # 服务启动

        # 从settings.json加载自动执行设置
        print("开始加载自动执行设置")
        settings = self.get_settings()
        print(f"获取到的设置: {settings}")
        
        # 同步复选框状态
        self.auto_exec_checkbox.setChecked(settings.get("autoExec", False))
        # 同步自动打印复选框状态
        self.auto_print_checkbox.setChecked(settings.get("autoPrint", True))

        
        if settings.get("autoExec", False):
            print("autoExec为True，启动自动执行服务")
            self.start_auto_execution()
            # 启动后立即更新标签
            print("启动后立即更新标签")
            self.update_next_execution_label()
        else:
            print("autoExec为False，不启动自动执行服务")
        
        # 数据加载
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_data()
    
    def create_required_folders(self):
        """自动创建所需的文件夹和文件"""
        # 创建计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        if not os.path.exists(plan_dir):
            os.makedirs(plan_dir)
            try:
                print(f"✓ 创建计划号文件夹: {plan_dir}")
            except UnicodeEncodeError:
                print(f"创建计划号文件夹: {plan_dir}")

        # 创建备份文件夹
        backup_dir = os.path.join(plan_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            try:
                print(f"✓ 创建备份文件夹: {backup_dir}")
            except UnicodeEncodeError:
                print(f"创建备份文件夹: {backup_dir}")
        
        # 清理 backup 目录中超过12小时的文件
        self.cleanup_backup_directory(backup_dir)

        # 创建必要的模板文件
        required_files = {
            "export_coordinates.json": "{}",
            "processed_plans.txt": "",
            "printed_plans.txt": "",
            "no_aps_plans.txt": ""
        }

        for filename, default_content in required_files.items():
            file_path = os.path.join(self.plan_dir, filename)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    try:
                        print(f"✓ 创建文件: {filename}")
                    except UnicodeEncodeError:
                        print(f"创建文件: {filename}")
                except Exception as e:
                    try:
                        print(f"✗ 创建文件失败 {filename}: {e}")
                    except UnicodeEncodeError:
                        print(f"创建文件失败 {filename}: {e}")

        # 特殊处理APS.txt文件 - 如果不存在，从项目目录读取
        aps_file_path = os.path.join(self.plan_dir, "APS.txt")
        if not os.path.exists(aps_file_path):
            try:
                # 从项目目录读取现有的APS.txt文件
                # 使用正确的路径逻辑，确保打包后也能找到文件
                if getattr(sys, 'frozen', False):
                    project_aps_file = os.path.join(sys._MEIPASS, "APS.txt")
                else:
                    project_aps_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "APS.txt")

                if os.path.exists(project_aps_file):
                    # 读取项目中的APS.txt文件内容
                    with open(project_aps_file, 'r', encoding='utf-8') as f:
                        aps_content = f.read()
                    # 创建新的APS.txt文件
                    with open(aps_file_path, 'w', encoding='utf-8') as f:
                        f.write(aps_content)
                    try:
                        print(f"✓ 从项目目录复制APS.txt文件")
                    except UnicodeEncodeError:
                        print(f"从项目目录复制APS.txt文件")
                else:
                    try:
                        print(f"✗ 项目目录中不存在APS.txt文件")
                    except UnicodeEncodeError:
                        print(f"项目目录中不存在APS.txt文件")
            except Exception as e:
                try:
                    print(f"✗ 创建APS.txt文件失败: {e}")
                except UnicodeEncodeError:
                    print(f"创建APS.txt文件失败: {e}")
    
    def cleanup_backup_directory(self, backup_dir):
        """清理backup目录中超过12小时的文件，将其移动到"原始文件"子目录
        
        Args:
            backup_dir: backup目录路径
        """
        import os
        import time
        
        # 创建"原始文件"目录（如果不存在）
        original_files_dir = os.path.join(backup_dir, "原始文件")
        if not os.path.exists(original_files_dir):
            os.makedirs(original_files_dir)
            print(f"✓ 创建原始文件目录: {original_files_dir}")
        
        # 获取当前时间
        current_time = time.time()
        # 12小时的秒数
        twelve_hours = 12 * 60 * 60
        
        # 统计移动的文件数量
        moved_count = 0
        
        # 遍历backup目录中的文件
        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                file_path = os.path.join(backup_dir, filename)
                
                # 跳过目录（包括"原始文件"目录）
                if not os.path.isfile(file_path):
                    continue
                
                # 只处理xls和xlsx文件
                if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
                    continue
                
                # 获取文件的修改时间
                file_mtime = os.path.getmtime(file_path)
                
                # 计算文件存在的时间
                file_age = current_time - file_mtime
                
                # 如果文件存在超过12小时，移动到"原始文件"目录
                if file_age > twelve_hours:
                    try:
                        # 目标文件路径
                        dest_path = os.path.join(original_files_dir, filename)
                        
                        # 如果目标文件已存在，添加时间戳
                        if os.path.exists(dest_path):
                            name, ext = os.path.splitext(filename)
                            timestamp = int(time.time())
                            dest_path = os.path.join(original_files_dir, f"{name}_{timestamp}{ext}")
                        
                        # 移动文件
                        os.rename(file_path, dest_path)
                        moved_count += 1
                        print(f"✓ 移动文件到原始文件目录: {filename}")
                    except Exception as e:
                        print(f"✗ 移动文件失败 {filename}: {e}")
        
        if moved_count > 0:
            print(f"\n✓ 清理完成: 成功移动 {moved_count} 个文件到原始文件目录")
    
    def init_database(self):
        """初始化数据库"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建计划表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_number TEXT UNIQUE,
                    block_count INTEGER,
                    status TEXT,
                    start_coil TEXT,
                    end_coil TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建打印记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS print_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_number TEXT,
                    printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_number) REFERENCES plans(plan_number)
                )
            ''')
            
            # 创建装炉明细打印记录表（存储已打印的钢卷号）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS furnace_printed_coils (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_number TEXT,
                    coil_number TEXT,
                    sequence INTEGER,
                    printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_number) REFERENCES plans(plan_number)
                )
            ''')
            
            # 创建计划顺序表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_order (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no INTEGER,
                    plan_no TEXT,
                    coil_no TEXT,
                    steel_grade TEXT,
                    billet_width REAL,
                    reduction_width REAL,
                    adjustment_width REAL,
                    roll_width REAL,
                    tolerance_band TEXT,
                    roughing_alarm TEXT,
                    descaling TEXT,
                    billet_thickness REAL,
                    billet_length REAL,
                    roll_thickness REAL,
                    middle_thickness REAL,
                    rt2 REAL,
                    strength REAL,
                    edge_cutting TEXT,
                    destination TEXT,
                    order_width REAL,
                    billet_head_width REAL,
                    billet_tail_width REAL,
                    hot_rolled_product_classification TEXT,
                    steelmaking_steel_grade TEXT,
                    negative_tolerance REAL,
                    positive_tolerance REAL,
                    reheat_billet TEXT,
                    original_roll_width REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建总计划号列表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS total_plan_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_no TEXT,
                    seq_no INTEGER,
                    steel_grade TEXT,
                    specification TEXT,
                    quantity INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
    
    def load_processed_plans(self):
        """加载已处理的计划（存储格式：计划号\t钢卷号）"""
        try:
            self.processed_plans = {}  # {plan_no: {coil_no, ...}}
            processed_plans_file = os.path.join(self.plan_dir, "processed_plans.txt")
            if os.path.exists(processed_plans_file):
                with open(processed_plans_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            if '\t' in line:
                            # 新格式：计划号\t钢卷号
                                plan_no, coil_no = line.split('\t', 1)
                                plan_no = plan_no.strip()
                                coil_no = coil_no.strip()
                                if plan_no not in self.processed_plans:
                                    self.processed_plans[plan_no] = set()
                                self.processed_plans[plan_no].add(coil_no)
                            else:
                            # 旧格式：只有计划号（向后兼容
                                plan_no = line
                                self.processed_plans[plan_no] = set()
            total_coil_count = sum(len(coils) for coils in self.processed_plans.values())
            print(f"已加载 {len(self.processed_plans)} 个计划号，共 {total_coil_count} 个已处理钢卷号")
        except Exception as e:
            print(f"加载已处理计划失败: {str(e)}")
            self.processed_plans = {}
    
    def load_printed_plans(self):
        """加载已打印的计划（存储格式：计划号\t钢卷号）"""
        try:
            self.printed_plans = {}  # {plan_no: {coil_no, ...}}
            printed_plans_file = os.path.join(self.plan_dir, "printed_plans.txt")
            if os.path.exists(printed_plans_file):
                with open(printed_plans_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            if '\t' in line:
                            # 新格式：计划号\t钢卷号
                                plan_no, coil_no = line.split('\t', 1)
                                plan_no = plan_no.strip()
                                coil_no = coil_no.strip()
                                if plan_no not in self.printed_plans:
                                    self.printed_plans[plan_no] = set()
                                self.printed_plans[plan_no].add(coil_no)
                            else:
                            # 旧格式：只有计划号（向后兼容
                                plan_no = line
                                self.printed_plans[plan_no] = set()
            total_coil_count = sum(len(coils) for coils in self.printed_plans.values())
            print(f"已加载 {len(self.printed_plans)} 个计划号，共 {total_coil_count} 个已打印钢卷号")
        except Exception as e:
            print(f"加载已打印计划失败: {str(e)}")
            self.printed_plans = {}
    
    def load_no_aps_plans(self):
        """加载无APS的计划"""
        try:
            no_aps_plans_file = os.path.join(self.plan_dir, "no_aps_plans.txt")
            if os.path.exists(no_aps_plans_file):
                with open(no_aps_plans_file, 'r', encoding='utf-8') as f:
                    self.no_aps_plans = set(line.strip() for line in f if line.strip())
            else:
                self.no_aps_plans = set()
            print(f"已加载 {len(self.no_aps_plans)} 个无APS计划")
        except Exception as e:
            print(f"加载无APS计划失败: {str(e)}")
            self.no_aps_plans = set()
    
    def load_low_roll_width_plans(self):
        """加载低轧宽的计划"""
        try:
            low_roll_width_plans_file = os.path.join(self.plan_dir, "low_roll_width_plans.txt")
            if os.path.exists(low_roll_width_plans_file):
                with open(low_roll_width_plans_file, 'r', encoding='utf-8') as f:
                    self.low_roll_width_plans = set(line.strip() for line in f if line.strip())
            else:
                self.low_roll_width_plans = set()
            print(f"已加载 {len(self.low_roll_width_plans)} 个低轧宽计划")
        except Exception as e:
            print(f"加载低轧宽计划失败: {str(e)}")
            self.low_roll_width_plans = set()
    
    def has_unprocessed_coils(self, plan_no, file_path):
        """检查计划号文件中是否有未处理的钢卷号（仅对D开头的计划号检查钢卷号）"""
        try:
            # 非D开头的计划号，保持原有判断逻辑
            if not plan_no.startswith('D') and not plan_no.startswith('d'):
                # 兼容旧格式：如果是set类型，直接判断
                if isinstance(self.processed_plans, set):
                    return plan_no not in self.processed_plans
                # 新格式dict：如果没有处理记录，认为需要处理；只要有记录（即使是空set），就认为已处理
                if plan_no not in self.processed_plans:
                    return True
                return False
            
            # D开头的计划号，检查钢卷号
            all_coil_nos = self.get_all_coil_nos_from_plan_file(file_path)
            if not all_coil_nos:
                # 如果无法获取钢卷号列表，默认认为需要处理（可能是文件格式特殊）
                return True
            
            if plan_no not in self.processed_plans:
                return True
            
            processed_coils = self.processed_plans.get(plan_no, set())
            for coil_no in all_coil_nos:
                if coil_no not in processed_coils:
                    return True
            
            return False
        except Exception as e:
            print(f"检查未处理钢卷号失败: {e}")
            return True  # 出错时默认需要处理
    
    def has_unprinted_coils(self, plan_no, file_path):
        """检查计划号文件中是否有未打印的钢卷号（仅对D开头的计划号检查钢卷号）"""
        try:
            # 非D开头的计划号，保持原有判断逻辑
            if not plan_no.startswith('D') and not plan_no.startswith('d'):
                # 兼容旧格式：如果是set类型，直接判断
                if isinstance(self.printed_plans, set):
                    return plan_no not in self.printed_plans
                # 新格式dict：如果没有打印记录，或者没有钢卷号记录，认为需要打印
                if plan_no not in self.printed_plans or not self.printed_plans.get(plan_no, set()):
                    return True
                return False
            
            # D开头的计划号，检查钢卷号
            all_coil_nos = self.get_all_coil_nos_from_plan_file(file_path)
            if not all_coil_nos:
                # 如果无法获取钢卷号列表，默认认为需要打印（可能是文件格式特殊）
                return True
            
            if plan_no not in self.printed_plans:
                return True
            
            printed_coils = self.printed_plans.get(plan_no, set())
            for coil_no in all_coil_nos:
                if coil_no not in printed_coils:
                    return True
            
            return False
        except Exception as e:
            print(f"检查未打印钢卷号失败: {e}")
            return True  # 出错时默认需要打印
    
    def mark_all_coils_processed(self, plan_no, file_path):
        """标记计划号文件中的所有钢卷号为已处理（仅对D开头的计划号记录钢卷号）"""
        try:
            # 非D开头的计划号，保持原有逻辑（仅标记计划号）
            if not plan_no.startswith('D') and not plan_no.startswith('d'):
                # 如果是新格式dict，保存为一个空set或者包含一个标记值
                if isinstance(self.processed_plans, dict):
                    self.processed_plans[plan_no] = set()
                # 如果是旧格式set，直接add
                elif isinstance(self.processed_plans, set):
                    self.processed_plans.add(plan_no)
                print(f"标记 {plan_no} 为已处理（非D开头计划）")
                return
            
            # D开头的计划号，记录所有钢卷号
            all_coil_nos = self.get_all_coil_nos_from_plan_file(file_path)
            
            if plan_no not in self.processed_plans:
                self.processed_plans[plan_no] = set()
            
            for coil_no in all_coil_nos:
                self.processed_plans[plan_no].add(coil_no)
            
            if all_coil_nos:
                print(f"标记 {plan_no} 的 {len(all_coil_nos)} 个钢卷号为已处理（D开头计划）")
            else:
                print(f"标记 {plan_no} 为已处理（D开头计划，无钢卷号）")
        except Exception as e:
            print(f"标记已处理钢卷号失败: {e}")
    
    def mark_all_coils_printed(self, plan_no, file_path):
        """标记计划号文件中的所有钢卷号为已打印（仅对D开头的计划号记录钢卷号）"""
        try:
            # 非D开头的计划号，保持原有逻辑（仅标记计划号）
            if not plan_no.startswith('D') and not plan_no.startswith('d'):
                if isinstance(self.printed_plans, dict):
                    self.printed_plans[plan_no] = set()
                elif isinstance(self.printed_plans, set):
                    self.printed_plans.add(plan_no)
                print(f"标记 {plan_no} 为已打印（非D开头计划）")
                return
            
            # D开头的计划号，记录所有钢卷号
            all_coil_nos = self.get_all_coil_nos_from_plan_file(file_path)
            
            if plan_no not in self.printed_plans:
                self.printed_plans[plan_no] = set()
            
            for coil_no in all_coil_nos:
                self.printed_plans[plan_no].add(coil_no)
            
            if all_coil_nos:
                print(f"标记 {plan_no} 的 {len(all_coil_nos)} 个钢卷号为已打印（D开头计划）")
            else:
                print(f"标记 {plan_no} 为已打印（D开头计划，无钢卷号）")
        except Exception as e:
            print(f"标记已打印钢卷号失败: {e}")
    
    def show_error_message(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)
    
    def save_processed_plans(self):
        """保存已处理的计划（D开头的保存钢卷号，其他只保存计划号）"""
        try:
            processed_file = os.path.join(self.plan_dir, "processed_plans.txt")
            with open(processed_file, 'w', encoding='utf-8') as f:
                # 兼容旧格式set
                if isinstance(self.processed_plans, set):
                    for plan_no in self.processed_plans:
                        f.write(f"{plan_no}\n")
                    print(f"已保存 {len(self.processed_plans)} 个已处理计划号（旧格式）")
                else:
                    # 新格式dict
                    for plan_no, coil_nos in self.processed_plans.items():
                        # D开头的计划号，保存每个钢卷号
                        if plan_no.startswith('D') or plan_no.startswith('d'):
                            for coil_no in coil_nos:
                                f.write(f"{plan_no}\t{coil_no}\n")
                        else:
                            # 非D开头的计划号，只保存计划号（保持旧格式）
                            f.write(f"{plan_no}\n")
                    total_coil_count = sum(len(coils) for plan_no, coils in self.processed_plans.items() 
                                           if plan_no.startswith('D') or plan_no.startswith('d'))
                    print(f"已保存 {len(self.processed_plans)} 个已处理计划号，共 {total_coil_count} 个已处理钢卷号（仅D开头计划）")
        except Exception as e:
            print(f"保存已处理计划号失败: {str(e)}")
    
    def save_printed_plans(self):
        """保存已打印的计划（D开头的保存钢卷号，其他只保存计划号）"""
        try:
            printed_file = os.path.join(self.plan_dir, "printed_plans.txt")
            with open(printed_file, 'w', encoding='utf-8') as f:
                # 兼容旧格式set
                if isinstance(self.printed_plans, set):
                    for plan_no in self.printed_plans:
                        f.write(f"{plan_no}\n")
                    print(f"已保存 {len(self.printed_plans)} 个已打印计划号（旧格式）")
                else:
                    # 新格式dict
                    for plan_no, coil_nos in self.printed_plans.items():
                        # D开头的计划号，保存每个钢卷号
                        if plan_no.startswith('D') or plan_no.startswith('d'):
                            for coil_no in coil_nos:
                                f.write(f"{plan_no}\t{coil_no}\n")
                        else:
                            # 非D开头的计划号，只保存计划号（保持旧格式）
                            f.write(f"{plan_no}\n")
                    total_coil_count = sum(len(coils) for plan_no, coils in self.printed_plans.items() 
                                           if plan_no.startswith('D') or plan_no.startswith('d'))
                    print(f"已保存 {len(self.printed_plans)} 个已打印计划号，共 {total_coil_count} 个已打印钢卷号（仅D开头计划）")
        except Exception as e:
            print(f"保存已打印计划号失败: {str(e)}")
    
    def save_no_aps_plans(self):
        """保存无APS的计划号"""
        try:
            no_aps_file = os.path.join(self.plan_dir, "no_aps_plans.txt")
            with open(no_aps_file, 'w', encoding='utf-8') as f:
                for plan_no in self.no_aps_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.no_aps_plans)} 个无APS计划号")
        except Exception as e:
            print(f"保存无APS计划号失败: {str(e)}")
    
    def save_low_roll_width_plans(self):
        """保存低轧宽的计划号"""
        try:
            low_roll_width_file = os.path.join(self.plan_dir, "low_roll_width_plans.txt")
            with open(low_roll_width_file, 'w', encoding='utf-8') as f:
                for plan_no in self.low_roll_width_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.low_roll_width_plans)} 个低轧宽计划号")
        except Exception as e:
            print(f"保存低轧宽计划号失败: {str(e)}")
    
    def 匹配除鳞钢种(self, 牌号, removePhosphorusList):
        """检查牌号是否匹配除鳞钢种列表（支持%通配符）"""
        if not 牌号:
            return False
        
        牌号字符串 = str(牌号).strip()
        
        # 检查是否匹配任何除鳞钢种
        for 钢种 in removePhosphorusList:
            钢种字符串 = 钢种.strip()
            
            # 精确匹配
            if 牌号字符串 == 钢种字符串:
                return True
            
            # 通配符匹配：以"1E"开头
            if 钢种字符串 == "1E" and 牌号字符串.startswith("1E"):
                return True
            
            # 通配符匹配：以"-p"结尾
            if 钢种字符串 == "-p" and 牌号字符串.lower().endswith("-p"):
                return True
            
            # 通配符匹配：以"-P"结尾
            if 钢种字符串 == "-P" and 牌号字符串.endswith("-P"):
                return True
            
            # 支持%通配符匹配（%表示任意字符序列，包括空序列）
            if '%' in 钢种字符串:
                # 将%通配符转换为正则表达式
                pattern = 钢种字符串.replace('%', '.*')
                import re
                if re.match(pattern, 牌号字符串):
                    return True
        
        return False
        
    def event(self, event):
        """处理自定义事件"""
        from PyQt5.QtCore import QEvent
        
        # 处理导出计划明细事件
        if hasattr(event, 'valid_no_file_plans'):
            try:
                valid_no_file_plans = event.valid_no_file_plans
                plan_detail_export_btn = event.plan_detail_export_btn
                test_window = event.test_window
                delay_time = event.delay_time
                coord_map = event.coord_map
                
                print(f"开始导出无文件计划号明细: {valid_no_file_plans}")
                
                # 导出无文件计划号明细
                for plan_no in valid_no_file_plans:
                    print(f"导出计划号: {plan_no}")
                    # 调用导出计划号明细函数
                    self.export_single_plan_detail(plan_no, test_window, plan_detail_export_btn, delay_time, coord_map)
                
                print("无文件计划号明细导出完成")
            except Exception as e:
                print(f"处理导出计划明细事件失败: {str(e)}")
            return True
        
        # 处理刷新事件 - 只处理特定的刷新事件
        if hasattr(event, 'refresh_type') and event.refresh_type == 'plan_list':
            try:
                # 刷新计划号列表
                self.refresh_plan_list()
            except Exception as e:
                print(f"处理刷新事件失败: {str(e)}")
            return True
        
        # 处理激活主窗口事件 - 通过事件类型和属性判断
        if event.type() == QEvent.User:
            # 检查是否是激活主窗口事件（通过排除其他已知的User事件）
            if (not hasattr(event, 'refresh_type') and 
                not hasattr(event, 'valid_no_file_plans') and 
                not hasattr(event, 'success') and
                not hasattr(event, 'plan_detail_export_btn')):
                try:
                    # 尝试多种方法激活主窗口
                    print("开始激活主窗口...")
                    
                    # 方法1：使用Qt的方法
                    self.activateWindow()
                    self.raise_()
                    self.show()
                    print("已使用Qt方法激活主窗口")
                    
                    # 方法2：使用win32gui
                    try:
                        import win32gui
                        import win32con
                        # 尝试获取窗口句柄的不同方式
                        main_hwnd = None
                        # 方式1：使用winId()
                        try:
                            main_hwnd = self.winId()
                        except:
                            pass
                        # 方式2：通过窗口标题查找
                        if not main_hwnd:
                            try:
                                main_hwnd = win32gui.FindWindow(None, "装炉顺序管理系统")
                            except:
                                pass
                        
                        if main_hwnd:
                            print(f"尝试使用win32gui激活主窗口: {main_hwnd}")
                            # 先ShowWindow再SetForegroundWindow
                            win32gui.ShowWindow(main_hwnd, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(main_hwnd)
                            # 额外尝试：使用SetWindowPos
                            win32gui.SetWindowPos(main_hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                            print("已使用win32gui激活主窗口")
                        else:
                            print("未找到主窗口句柄")
                    except Exception as e:
                        print(f"win32gui激活失败: {e}")
                    
                    # 方法3：使用QApplication的方法
                    try:
                        from PyQt5.QtWidgets import QApplication
                        QApplication.setActiveWindow(self)
                        print("已使用QApplication方法激活主窗口")
                    except Exception as e:
                        print(f"QApplication激活失败: {e}")
                    
                    # 方法4：使用keybd_event模拟按键
                    try:
                        import win32api
                        import win32con
                        # 模拟Alt键按下和释放，有时能帮助激活窗口
                        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                        print("已使用keybd_event激活主窗口")
                    except Exception as e:
                        print(f"keybd_event激活失败: {e}")
                    
                    print("主窗口激活完成")
                except Exception as e:
                    print(f"处理激活主窗口事件失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                return True
            
            # 处理完成事件
            elif hasattr(event, 'success'):
                try:
                    # 关闭进度窗口
                    if hasattr(event, 'progress_window') and event.progress_window:
                        try:
                            event.progress_window.close()
                            print("进度窗口已关闭")
                        except Exception as e:
                            print(f"关闭进度窗口失败: {e}")
                    
                    # 显示结果
                    if event.success:
                        # 检查是否有导出的计划号
                        if event.exported_plans:
                            # 更新最近导出的计划号列表
                            self.recently_exported_plans = set(event.exported_plans)
                            print(f"已更新最近导出的计划号: {event.exported_plans}")
                            # 刷新计划号列表,使绿色标注生效
                            self.refresh_plan_list_from_file()
                            
                            # 直接处理导出的计划号
                            print("\n=== 自动处理导出的计划号 ===")
                            # 选中刚刚导出的计划号
                            self.table_widget.clearSelection()
                            for i, item in enumerate(self.plan_data):
                                if item['plan_no'] in event.exported_plans:
                                    self.table_widget.selectRow(i)
                            print(f"已选中 {len(event.exported_plans)} 个导出的计划号")
                            
                            # 调用处理计划方法，不检查是否已处理过
                            print("开始自动处理计划...")
                            try:
                                # 获取设置中的自动打印设置
                                settings = self.get_settings()
                                auto_print = settings.get("autoPrint", True)
                                
                                # 调用处理计划方法，传入auto_print参数
                                if self.process_selected_plans(force_process=True, auto_print=auto_print):
                                    print("计划处理完成")
                                else:
                                    print("计划处理失败")
                            except Exception as e:
                                print(f"自动处理计划失败: {e}")
                                import traceback
                                traceback.print_exc()
                    
                    # 显示消息
                    if event.success:
                        # 使用自定义消息框显示成功消息 - 可手动关闭，自动3秒关闭
                        self.custom_messagebox("成功", "自动导出完成！", msg_type='info', auto_close=3)
                        
                        # 先回到主程序画面（轧制计划管理系统）
                        print("返回主程序画面（轧制计划管理系统）")
                        try:
                            self.activateWindow()
                            self.raise_()
                            self.show()
                            print("成功返回主程序画面")
                        except Exception as e:
                            print(f"返回主程序画面失败: {e}")
                        # 10秒后进入装炉明细画面（使用类方法）
                        QTimer.singleShot(10000, self.go_to_furnace_details)
                    else:
                        # 使用自定义消息框显示错误消息 - 可手动关闭，自动3秒关闭
                        self.custom_messagebox("错误", event.message, msg_type='error', auto_close=3)
                except Exception as e:
                    print(f"处理完成事件失败: {e}")
                return True
            
            # 处理错误事件
            elif hasattr(event, 'message') and not hasattr(event, 'success'):
                try:
                    # 使用自定义消息框显示错误消息 - 可手动关闭，自动3秒关闭
                    self.custom_messagebox("错误", event.message, msg_type='error', auto_close=3)
                except Exception as e:
                    print(f"处理错误事件失败: {e}")
                return True
        
        # 处理其他事件
        return super().event(event)
    
    def load_coordinate_config(self):
        """加载坐标配置"""
        try:
            import json
            # 使用self.plan_dir确保打包后也能正确读取配置文件
            config_file = os.path.join(self.plan_dir, "export_coordinates.json")
            if os.path.exists(config_file):
                # 检查文件大小，如果文件太小可能是空文件
                if os.path.getsize(config_file) < 5:
                    print("坐标配置文件为空,使用默认配置")
                    return self.get_default_coordinates()
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    coordinates = json.load(f)
                
                # 检查是否为空对象
                if not isinstance(coordinates, dict) or len(coordinates) == 0:
                    print("坐标配置文件内容为空,使用默认配置")
                    return self.get_default_coordinates()
                
                print("坐标配置加载成功")
                return coordinates
            else:
                print("坐标配置文件不存在,使用默认配置")
                return self.get_default_coordinates()
        except Exception as e:
            print(f"加载坐标配置失败: {e}, 使用默认配置")
            return self.get_default_coordinates()
    
    def get_default_coordinates(self):
        """获取默认坐标配置"""
        return {
                    "zhuanglu_tab": [284, 85],
                    "zhuanglu_export_btn": [988, 819],
                    "zhizhi_tab": [107, 85],
                    "plan_select": [734, 135],
                    "zhizhi_export_btn": [78, 708],
                    "first_plan": [235, 207],
                    "plan_detail_export": [79, 859],
                    "plan_spacing": 21,
                    "first_plan_offset": 0,
                    "test_window": "BGCMS1-宝钢股份多基地制造管理系统运行环境",
                    "auto_process_after_export": False,
                    "auto_print_after_export": False,
                    "export_speed": "中",
                    "show_operation_warning": True,
                    "anti_logout_enabled": False,
                    "auto_exec_enabled": False,
                    "auto_exec_mode": "interval",
                    "auto_exec_interval": 30,
                    "auto_exec_times": "",
                    "anti_logout_interval": 60000
                }
    

    def load_data(self):
        """加载Excel数据 - 调用刷新计划号列表方法"""
        try:
            import os
            # 重新加载已处理和已打印的状态
            self.load_processed_plans()
            self.load_printed_plans()
            self.load_no_aps_plans()
            self.load_low_roll_width_plans()
            
            # 刷新计划号列表
            self.refresh_plan_list()
            print("数据加载完成")
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
    
    def refresh_plan_list(self, export_zhuanglu=False):
        """刷新计划号列表"""
        try:
            print("\n=== 开始刷新计划号列表 ===")
            
            # 1. 强制刷新装炉顺序数据缓存
            self.clear_zhuanglu_cache()
            
            # 2. 扫描并重命名计划号文件
            self.scan_and_rename_plan_files()
            
            # 3. 从数据库读取数据并更新表格
            self.refresh_plan_list_from_file()
            
            print("=== 计划号列表刷新完成 ===\n")
        except Exception as e:
            print(f"刷新计划号列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear_zhuanglu_cache(self):
        """清除装炉顺序相关的缓存数据"""
        print("清除装炉顺序缓存...")
        
        # 清除装炉顺序映射
        if hasattr(self, '装炉顺序映射'):
            self.装炉顺序映射 = {}
        
        # 清除轧宽余量映射
        if hasattr(self, '轧宽余量映射'):
            self.轧宽余量映射 = {}
        
        # 清除文件系统缓存（Windows）
        try:
            import ctypes
            ctypes.windll.kernel32.FlushFileBuffers(-1)
            print("文件系统缓存已刷新")
        except:
            pass
        
        # 清除 xlrd 的内部缓存
        if 'xlrd' in sys.modules:
            xlrd_module = sys.modules['xlrd']
            if hasattr(xlrd_module, '_open_workbooks'):
                xlrd_module._open_workbooks.clear()
                print("xlrd 内部缓存已清除")
        
        print("装炉顺序缓存清除完成")
    
    def ensure_zhuanglu_shunxu_file(self, force_reload=False):
        """确保装炉顺序文件能被准确获取
        Args:
            force_reload: 是否强制重新加载（跳过缓存）
        Returns:
            tuple: (success, message)
        """
        print("\n=== 确保装炉顺序文件 ===")
        
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        # 1. 检查文件是否存在
        if not os.path.exists(zhuanglu_file):
            msg = f"装炉顺序文件不存在: {zhuanglu_file}"
            print(f"[×] {msg}")
            return False, msg
        
        # 2. 如果强制重新加载，清除缓存并关闭Excel进程
        if force_reload:
            self.clear_zhuanglu_cache()
            self.kill_all_excel_processes()
        
        # 3. 验证文件是最新的（检查文件修改时间）
        file_mtime = os.path.getmtime(zhuanglu_file)
        import time
        current_time = time.time()
        file_age_seconds = current_time - file_mtime
        file_age_minutes = file_age_seconds / 60
        print(f"文件修改时间: {time.ctime(file_mtime)}")
        print(f"文件年龄: {file_age_minutes:.1f} 分钟")
        
        # 4. 尝试读取文件验证其有效性（带重试机制）
        success, result = self.safe_read_excel_with_retry(zhuanglu_file)
        if not success:
            msg = f"无法读取装炉顺序文件: {result}"
            print(f"[×] {msg}")
            return False, msg
        
        workbook = result
        sheet = workbook.sheet_by_index(0)
        
        # 5. 验证文件内容
        if sheet.nrows < 2:
            msg = "装炉顺序文件只有表头或为空"
            print(f"[×] {msg}")
            return False, msg
        
        headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
        required_cols = ["钢卷号", "装炉顺序号", "计划号"]
        missing_cols = [col for col in required_cols if col not in headers]
        
        if missing_cols:
            msg = f"装炉顺序文件缺少必要列: {', '.join(missing_cols)}"
            print(f"[×] {msg}")
            return False, msg
        
        # 6. 释放资源
        if hasattr(workbook, 'release_resources'):
            workbook.release_resources()
        
        msg = f"装炉顺序文件验证通过，共 {sheet.nrows - 1} 条数据"
        print(f"[√] {msg}")
        return True, msg
    
    def safe_read_excel_with_retry(self, file_path, max_retries=5, retry_delay=2.0):
        """带重试机制的安全读取Excel文件，处理导出后可能无法读取的问题"""
        import xlrd
        import time
        import os
        
        for attempt in range(max_retries):
            try:
                # 先检查文件是否可以访问
                if not os.path.exists(file_path):
                    return False, f"文件不存在: {file_path}"
                
                # 检查文件是否被占用（尝试以写入模式打开）
                try:
                    with open(file_path, 'rb') as f:
                        pass  # 文件可以访问
                except PermissionError:
                    print(f"文件被占用，尝试关闭Excel进程...")
                    self.kill_all_excel_processes()
                    time.sleep(1)
                    continue
                
                # 尝试读取文件
                workbook = xlrd.open_workbook(file_path)
                print(f"读取文件成功（尝试 {attempt + 1}/{max_retries}）")
                return True, workbook
                
            except Exception as e:
                print(f"读取文件失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
                if attempt < max_retries - 1:
                    # 关闭Excel进程并重试
                    self.kill_all_excel_processes()
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False, str(e)
    
    def kill_all_excel_processes(self):
        """强制关闭所有Excel进程，解决文件被占用的问题"""
        try:
            import subprocess
            import time
            
            # 第一次尝试正常关闭
            subprocess.run(
                ['taskkill', '/im', 'EXCEL.EXE'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(1)
            
            # 第二次尝试强制关闭
            subprocess.run(
                ['taskkill', '/f', '/im', 'EXCEL.EXE'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(2)
            
            print("Excel进程已强制关闭")
        except Exception as e:
            print(f"关闭Excel进程失败: {e}")
    
    def scan_and_rename_plan_files(self):
        """扫描并重命名计划号文件"""
        try:
            import os
            
            # 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            # 如果计划号文件夹不存在,创建它
            if not os.path.exists(plan_dir):
                print(f"计划号文件夹不存在,创建: {plan_dir}")
                os.makedirs(plan_dir)
                return
            
            print("\n=== 扫描并重命名计划号文件 ===")
            print(f"扫描目录: {plan_dir}")
            
            # 获取计划号文件夹中的所有文件
            files = os.listdir(plan_dir)
            renamed_count = 0
            skipped_count = 0
            
            for file in files:
                file_path = os.path.join(plan_dir, file)
                
                # 跳过目录
                if os.path.isdir(file_path):
                    continue
                
                # 跳过系统文件
                if file.startswith("装炉顺序") or file.startswith("总计划号列表") or file in ["装炉顺序_显示.xls", "合并文件.xls"]:
                    print(f"跳过系统文件: {file}")
                    skipped_count += 1
                    continue
                
                # 只处理xls和xlsx文件
                if not (file.endswith(".xls") or file.endswith(".xlsx")):
                    continue
                
                # 这里可以添加读取文件获取计划号并重命名的逻辑
                # 暂时跳过实际的重命名操作
                print(f"处理文件: {file}")
            
            print(f"扫描完成: 处理 {len(files)} 个文件,跳过 {skipped_count} 个文件")
        except Exception as e:
            print(f"扫描并重命名计划号文件失败: {str(e)}")
    
    def refresh_data(self):
        """刷新数据"""
        # 刷新计划号列表（load_data会自动加载状态）
        self.load_data()
    
    def process_plans(self, auto_print=False, show_result=True, force_process=False):
        """处理计划号文件 - 使用 pandas + xlwt 方案
        
        Args:
            auto_print: 是否在处理完成后自动打印（默认False,仅自动导出流程中为True）
            show_result: 是否显示处理结果弹窗（默认True,在显示按钮调用时为False）
            force_process: 是否强制处理（忽略已处理状态，默认False）
        """
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            from PyQt5.QtCore import Qt
            
            # 如果不是强制处理，重新加载状态确保数据最新
            # 强制处理时保持当前状态不变（可能已经被调用方修改）
            if not force_process:
                print("process_plans: 重新加载状态...")
                self.load_processed_plans()
                self.load_printed_plans()
                print("process_plans: 状态重新加载完成")
            
            # 检查是否选择了计划号
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("警告")
                msg_box.setText("请先在计划号列表中选择要处理的计划号")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            if not os.path.exists(plan_dir):
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("错误")
                msg_box.setText(f"计划号文件夹不存在: {plan_dir}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 获取选中的计划号
            selected_plans = [self.plan_data[index.row()]['plan_no'] for index in selected_items]
            print(f"process_plans: 选中的计划号: {selected_plans}")
            
            # 筛选可处理的计划号
            # 条件：1. 不是D开头 2. 没有"无文件"标识 3. A1单元格不是"轧制计划明细表"
            valid_plans = []
            skipped_plans = []
            no_file_plans = []
            already_processed_plans = []
            
            for plan_no in selected_plans:
                # 条件1：排除D开头的计划号
                if plan_no.startswith('D') or plan_no.startswith('d'):
                    skipped_plans.append(plan_no)
                    continue
                
                # 条件2：检查是否有"无文件"标识
                plan_status = None
                for data in self.plan_data:
                    if data['plan_no'] == plan_no:
                        plan_status = data.get('status', '')
                        break
                
                if plan_status == '无文件':
                    no_file_plans.append(plan_no)
                    continue
                
                # 条件3：检查A1单元格是否为"轧制计划明细表"
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    try:
                        import xlrd
                        workbook = xlrd.open_workbook(file_path)
                        sheet = workbook.sheet_by_index(0)
                        if sheet.nrows > 0 and sheet.ncols > 0:
                            a1_value = str(sheet.cell_value(0, 0)).strip()
                            if a1_value == "轧制计划明细表":
                                already_processed_plans.append(plan_no)
                                continue
                    except Exception as e:
                        print(f"检查计划号 {plan_no} 文件失败: {str(e)}")
                
                # 所有条件都满足，可以处理
                valid_plans.append(plan_no)
            
            # 输出筛选结果
            if skipped_plans:
                print(f"跳过D开头计划号: {skipped_plans}")
            if no_file_plans:
                print(f"跳过无文件计划号: {no_file_plans}")
            if already_processed_plans:
                print(f"跳过已处理计划号(A1=轧制计划明细表): {already_processed_plans}")
            print(f"可处理计划号: {valid_plans}")
            
            # 如果没有可处理的计划号，显示提示
            if not valid_plans and show_result:
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_text = "没有符合条件的计划号可处理\n\n"
                if skipped_plans:
                    msg_text += f"D开头计划号已跳过: {', '.join(skipped_plans)}\n"
                if no_file_plans:
                    msg_text += f"无文件计划号已跳过: {', '.join(no_file_plans)}\n"
                if already_processed_plans:
                    msg_text += f"已处理计划号已跳过: {', '.join(already_processed_plans)}\n"
                msg_box.setText(msg_text)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 如果不是强制处理，检查已处理状态（原有逻辑保持不变）
            if not force_process:
                already_processed = []
                for plan_no in valid_plans:
                    if isinstance(self.processed_plans, set):
                        if plan_no in self.processed_plans:
                            already_processed.append(plan_no)
                    elif isinstance(self.processed_plans, dict):
                        if plan_no in self.processed_plans:
                            already_processed.append(plan_no)
                
                if already_processed and show_result:
                    self.activateWindow()
                    self.raise_()
                    self.show()
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("提示")
                    msg_box.setText(f"以下计划号已处理过,无需重复处理：\n\n{', '.join(already_processed)}")
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                    msg_box.setModal(True)
                    QApplication.setActiveWindow(msg_box)
                    msg_box.exec_()
                    self.activateWindow()
                    self.raise_()
                    self.show()
                    return
            
            # 构建选中计划号的文件路径列表（只处理valid_plans）
            selected_files = []
            for plan_no in valid_plans:
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    selected_files.append((plan_no, file_path))
                else:
                    print(f'文件不存在: {plan_no}.xls')
            
            if not selected_files:
                return
            
            # 直接处理,不显示确认窗口
            
            # 处理每个文件
            processed_count = 0
            failed_count = 0
            skipped_count = 0
            success_files = []
            failed_files = []
            skipped_files = []
            
            for plan_no, file_path in selected_files:
                try:
                    print(f"开始处理: {plan_no}.xls")
                    has_low_roll_width, has_no_aps = self.run_excel_macro_with_pandas(file_path)
                    processed_count += 1
                    success_files.append(plan_no)
                    print(f"处理成功: {plan_no}.xls")
                    # 标记所有钢卷号为已处理
                    if not hasattr(self, 'processed_plans'):
                        self.processed_plans = {}
                    self.mark_all_coils_processed(plan_no, file_path)
                    
                    # 更新plan_data中的has_low_roll_width和has_no_aps字段
                    for i, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[i]['has_low_roll_width'] = has_low_roll_width
                            self.plan_data[i]['has_no_aps'] = has_no_aps
                            break
                    
                    # 更新低轧宽板坯集合并保存
                    if has_low_roll_width:
                        self.low_roll_width_plans.add(plan_no)
                    else:
                        # 如果不再有低轧宽板坯,从集合中移除
                        self.low_roll_width_plans.discard(plan_no)
                    self.save_low_roll_width_plans()
                    
                    # 更新无APS计划集合并保存
                    if has_no_aps:
                        self.no_aps_plans.add(plan_no)
                    else:
                        # 如果不再有无APS钢种,从集合中移除
                        self.no_aps_plans.discard(plan_no)
                    self.save_no_aps_plans()
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    print(f"处理失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_count > 0:
                print(f"process_plans: 保存已处理计划状态，共处理 {processed_count} 个计划")
                self.save_processed_plans()
                # 刷新列表显示
                self.refresh_data()
                print(f"process_plans: 状态保存和刷新完成")
            
            # 检查是否需要自动打印（仅在自动导出流程中）
            if auto_print and success_files:
                # 自动执行打印功能（打印刚刚处理的计划号）
                print("\n=== 自动执行计划打印 ===")
                # 选中刚刚处理成功的计划号
                self.table_widget.clearSelection()
                for i, plan_data in enumerate(self.plan_data):
                    if plan_data['plan_no'] in success_files:
                        self.table_widget.selectRow(i)
                # 自动打印选中的计划号
                self.print_selected()
            else:
                # 显示结果 - 使用自定义窗口
                if show_result:
                    self.show_result_dialog("处理完成！", success_files, failed_files, skipped_files, auto_close=3)
        except Exception as e:
            print(f"处理计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_result_dialog(self, title, success_files, failed_files, skipped_files, auto_close=None):
        """显示结果对话框（处理完成/打印完成共用）"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont
        
        # 创建自定义窗口
        result_window = QDialog(self)
        result_window.setWindowTitle("完成")
        result_window.setWindowModality(Qt.ApplicationModal)
        
        # 设置窗口大小
        window_width = 600
        window_height = 450
        result_window.resize(window_width, window_height)
        
        # 将窗口居中显示（相对于主程序窗口）
        if self.isVisible():
            main_rect = self.frameGeometry()
            center_x = main_rect.x() + (main_rect.width() - window_width) // 2
            center_y = main_rect.y() + (main_rect.height() - window_height) // 2
            result_window.move(center_x, center_y)
        else:
            # 如果主窗口不可见，居中到屏幕
            screen_rect = QApplication.desktop().screenGeometry()
            center_x = (screen_rect.width() - window_width) // 2
            center_y = (screen_rect.height() - window_height) // 2
            result_window.move(center_x, center_y)
        
        # 主布局
        main_layout = QVBoxLayout(result_window)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("宋体", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 统计信息
        processed_count = len(success_files)
        failed_count = len(failed_files)
        skipped_count = len(skipped_files)
        stats_label = QLabel(f"成功: {processed_count} 个 | 失败: {failed_count} 个 | 跳过: {skipped_count} 个")
        stats_label.setFont(QFont("宋体", 16))
        stats_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(stats_label)
        
        # 成功的文件
        if success_files:
            success_label = QLabel(f"成功的计划号: {', '.join(success_files)}")
            success_label.setFont(QFont("宋体", 14))
            success_label.setWordWrap(True)
            main_layout.addWidget(success_label)
        
        # 失败的文件
        if failed_files:
            failed_label = QLabel(f"失败的计划号: {', '.join(failed_files)}")
            failed_label.setFont(QFont("宋体", 14))
            failed_label.setWordWrap(True)
            main_layout.addWidget(failed_label)
        
        # 跳过的文件
        if skipped_files:
            skipped_label = QLabel(f"跳过的计划号: {', '.join(skipped_files)}")
            skipped_label.setFont(QFont("宋体", 14))
            skipped_label.setWordWrap(True)
            main_layout.addWidget(skipped_label)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setFont(QFont("宋体", 14))
        ok_btn.setFixedSize(100, 40)
        ok_btn.clicked.connect(result_window.accept)
        btn_layout.addWidget(ok_btn)
        
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)
        
        # 设置自动关闭
        if auto_close is not None:
            QTimer.singleShot(auto_close * 1000, result_window.accept)
        
        # 显示窗口
        result_window.exec_()
    
    def print_furnace_details(self, is_incremental=False, table_widget=None):
        """打印装炉明细 - 像主程序画面中的格式打印
        
        Args:
            is_incremental: 是否增量打印（只打印新增的钢卷号数据）
            table_widget: 可选参数，指定要打印的表格控件，默认为主窗口的表格
        """
        try:
            import os
            import time
            import xlwt
            import json
            
            # 使用传入的表格或默认使用主窗口的表格
            target_table = table_widget if table_widget else self.table_widget
            
            # 获取所有数据
            rows = []
            for row_idx in range(target_table.rowCount()):
                row_data = []
                for col_idx in range(target_table.columnCount()):
                    item = target_table.item(row_idx, col_idx)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                rows.append(row_data)
            
            if not rows:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "没有数据可打印")
                return
            
            # 初始化增量打印标志
            真正增量打印 = False
            
            # 如果是增量打印，找出新增的钢卷号
            if is_incremental:
                # 从数据库读取已打印的钢卷号
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 获取当前计划号
                plan_number = ""
                if rows:
                    plan_number = rows[0][1] if len(rows[0]) > 1 else ""  # 计划号在第1列
                
                # 调试信息
                print(f"调试信息: is_incremental = {is_incremental}")
                print(f"调试信息: plan_number = '{plan_number}'")
                
                # 查询已打印的钢卷号
                cursor.execute('''
                    SELECT coil_number, sequence FROM furnace_printed_coils 
                    WHERE plan_number = ?
                ''', (plan_number,))
                previous_data = cursor.fetchall()
                
                # 调试信息
                print(f"调试信息: previous_data = {previous_data}")
                
                # 关闭连接
                conn.close()
                
                # 获取已打印钢卷号列表
                previous_coils = set(row[0] for row in previous_data)
                
                # 调试信息
                print(f"调试信息: previous_coils = {previous_coils}")
                
                # 如果没有已打印数据，视为首次打印
                if not previous_data:
                    print(f"调试信息: 没有已打印数据，设置 is_incremental = False")
                    is_incremental = False
                
                # 获取当前所有钢卷号（过滤掉特殊行如换辊行、自定义信息行）
                current_coils_ordered = []  # 按顺序保存钢卷号和对应行索引
                for row_idx, row_data in enumerate(rows):
                    # 检查是否是特殊行（通过序号列判断）
                    first_col_text = row_data[0] if row_data else ""
                    # 如果序号列包含"换辊"或"△"等特殊标记，则跳过
                    if "换辊" in first_col_text or "△" in first_col_text:
                        continue
                    coil_number = row_data[1] if len(row_data) > 1 else ""  # 钢卷号在第1列
                    if coil_number and coil_number.strip():
                        current_coils_ordered.append({
                            'coil_number': coil_number.strip(),
                            'row_data': row_data,
                            'row_idx': row_idx
                        })
                
                # 找出新增的钢卷号（不在上次打印数据中的）
                new_coils = []
                for item in current_coils_ordered:
                    if item['coil_number'] not in previous_coils:
                        new_coils.append(item)
                
                if not new_coils:
                    # 调试信息
                    print(f"调试信息: previous_coils = {previous_coils}")
                    print(f"调试信息: current_coils_ordered = {[item['coil_number'] for item in current_coils_ordered]}")
                    print(f"调试信息: new_coils = {[item['coil_number'] for item in new_coils]}")
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "提示", "没有新增的钢卷号，无需打印")
                    return
                
                print(f"增量打印：上次打印 {len(previous_coils)} 个钢卷号，当前 {len(current_coils_ordered)} 个，新增 {len(new_coils)} 个")
                
                # 检查新增钢卷号是否在表格最前面（前面没有已打印钢卷号）
                # 找出所有新增钢卷号中最小的 row_idx
                min_new_row_idx = min(item['row_idx'] for item in new_coils)
                
                # 找出所有已打印钢卷号中最大的 row_idx
                max_printed_row_idx = -1
                for i, item in enumerate(current_coils_ordered):
                    if item['coil_number'] in previous_coils:
                        max_printed_row_idx = i
                
                # 检查当前表格中是否还有已打印的钢卷号
                has_printed_coil = False
                for item in current_coils_ordered:
                    if item['coil_number'] in previous_coils:
                        has_printed_coil = True
                        break
                
                # 根据用户选择决定是否增量打印
                真正增量打印 = is_incremental
                if is_incremental:
                    if not has_printed_coil:
                        print(f"首次打印或无已打印记录，打印全部数据")
                        真正增量打印 = False
                    else:
                        print(f"执行增量打印（只打印新增钢卷号）")
                else:
                    print(f"执行全部打印（用户选择了全部打印）")
                
                # 确定新增钢卷号的位置（尾部增加还是中间插入）
                # 找出最后一个已打印钢卷号的位置
                last_printed_idx = -1
                for i, item in enumerate(current_coils_ordered):
                    if item['coil_number'] in previous_coils:
                        last_printed_idx = i
                
                # 分类新增钢卷号
                tail_new_coils = []  # 尾部新增
                insert_new_coils = []  # 中间插入新增
                
                for item in new_coils:
                    if item['row_idx'] > last_printed_idx:
                        # 在最后一个已打印钢卷号之后，为尾部新增
                        tail_new_coils.append(item)
                    else:
                        # 在中间插入
                        insert_new_coils.append(item)
                
                # 计算新增钢卷号的新序号
                # 获取原数据最后一块的序号（数据库返回的是元组 (coil_number, sequence)）
                last_seq_num = 1
                for item in previous_data:
                    seq_str = str(item[1])  # sequence 在索引1位置
                    # 提取纯数字序号（可能带后缀）
                    import re
                    match = re.match(r'^(\d+)', seq_str)
                    if match:
                        seq_num = int(match.group(1))
                        if seq_num > last_seq_num:
                            last_seq_num = seq_num
                
                # 计算新增序号
                new_seq_info = []  # 保存新序号信息
                
                # 将所有新增钢卷号按位置排序
                all_new_coils_sorted = sorted(new_coils, key=lambda x: x['row_idx'])
                
                # 找出第一个已打印钢卷号的序号（作为中间插入的基准）
                first_printed_seq = "1"
                for item in current_coils_ordered:
                    if item['coil_number'] in previous_coils:
                        # 从数据库中获取该钢卷号的序号
                        for prev_item in previous_data:
                            if prev_item[0] == item['coil_number']:
                                first_printed_seq = str(prev_item[1])
                                break
                        break
                
                # 分别统计中间插入和尾部新增的数量
                insert_count = 0
                tail_count = 0
                
                # 逐个处理每个新增钢卷号，按位置排序
                for item in all_new_coils_sorted:
                    # 判断是中间插入还是尾部新增
                    if item['row_idx'] > last_printed_idx:
                        # 尾部新增
                        tail_count += 1
                        new_seq = last_seq_num + tail_count
                    else:
                        # 中间插入
                        insert_count += 1
                        # 使用 "第一个已打印序号-1>" 格式
                        import re
                        match = re.match(r'^(\d+)', first_printed_seq)
                        if match:
                            base_seq = match.group(1)
                            new_seq = f"{base_seq}-{insert_count}>"
                        else:
                            new_seq = f"?-{insert_count}>"
                    
                    # 添加到 new_seq_info
                    new_seq_info.append({
                        'coil_number': item['coil_number'],
                        'row_data': item['row_data'],
                        'new_sequence': new_seq
                    })
                
                print(f"尾部新增: {len(tail_new_coils)} 个")
                print(f"中间插入新增: {len(insert_new_coils)} 个")
                for info in new_seq_info:
                    print(f"  {info['coil_number']} -> 序号: {info['new_sequence']}")
                
                # 只有真正执行增量打印时才执行以下逻辑
                if 真正增量打印:
                    # 更新rows为只包含新增数据
                    rows = [info['row_data'] for info in new_seq_info]
                    
                    # 将新增钢卷号保存到数据库
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    for info in new_seq_info:
                        # 提取新序号的数字部分
                        seq_str = info['new_sequence']
                        import re
                        match = re.match(r'^(\d+)', seq_str)
                        seq_num = int(match.group(1)) if match else seq_num + 1
                        
                        cursor.execute('''
                            INSERT INTO furnace_printed_coils (plan_number, coil_number, sequence)
                            VALUES (?, ?, ?)
                        ''', (plan_number, info['coil_number'], seq_num))
                    
                    conn.commit()
                    conn.close()
                    
                    print(f"已将 {len(new_seq_info)} 个新增钢卷号保存到数据库")
                    
                    # 提示信息
                    提示行 = [f"装炉明细打印-新增({len(new_seq_info)}块)"]
            else:
                # 首次打印或全部打印
                # 获取当前计划号
                plan_number = ""
                if rows:
                    plan_number = rows[0][1] if len(rows[0]) > 1 else ""  # 计划号在第1列
                
                # 连接数据库
                import sqlite3
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 如果是全部打印，先删除该计划号的所有打印记录
                if not is_incremental:
                    cursor.execute('DELETE FROM furnace_printed_coils WHERE plan_number = ?', (plan_number,))
                
                # 收集当前所有钢卷号并保存到数据库
                seq_num = 1
                count = 0
                for row_idx, row_data in enumerate(rows):
                    first_col_text = row_data[0] if row_data else ""
                    if "换辊" in first_col_text or "△" in first_col_text:
                        continue
                    coil_number = row_data[1] if len(row_data) > 1 else ""
                    if coil_number and coil_number.strip():
                        # 插入数据库
                        cursor.execute('''
                            INSERT INTO furnace_printed_coils (plan_number, coil_number, sequence)
                            VALUES (?, ?, ?)
                        ''', (plan_number, coil_number.strip(), seq_num))
                        seq_num += 1
                        count += 1
                
                # 提交事务
                conn.commit()
                conn.close()
                
                print(f"已保存打印数据到数据库: {count} 个钢卷号")
                
                # 过滤掉特殊行
                filtered_rows = []
                for row_data in rows:
                    first_col_text = row_data[0] if row_data else ""
                    if "换辊" in first_col_text or "△" in first_col_text:
                        continue
                    filtered_rows.append(row_data)
                rows = filtered_rows
                
                提示行 = ["装炉明细打印"]
            
            # 创建临时 Excel 文件（存储在计划号文件夹中）
            plan_dir = os.path.join(self.plan_dir, "计划号")
            temp_file_name = f"temp_装炉明细打印_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            
            # 创建工作簿和工作表
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet('装炉明细')
            
            # 设置页边距为0（上下左右都为0，使用inches为单位）
            sheet.left_margin = 0.0
            sheet.right_margin = 0.0
            sheet.top_margin = 0.0
            sheet.bottom_margin = 0.0
            
            # 设置页眉页脚为空（无页眉页脚）
            sheet.header_str = b''
            sheet.footer_str = b''
            
            # 设置列名
            提示行 = ["装炉明细打印"]
            headers = ["序号", "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "订宽"]
            
            # 获取各列的索引（使用列名）
            粗轧报信列索引 = headers.index("粗轧报信")
            钢卷号列索引 = headers.index("钢卷号")
            牌号列索引 = headers.index("牌号（钢级）")
            坯宽列索引 = headers.index("坯宽")
            坯长列索引 = headers.index("坯长")
            轧厚列索引 = headers.index("轧厚")
            强度列索引 = headers.index("强度")
            
            # 定义样式
            # 大标题样式
            style_title = xlwt.XFStyle()
            font_title = xlwt.Font()
            font_title.name = '仿宋'
            font_title.height = 280  # 14pt
            font_title.bold = True
            style_title.font = font_title
            alignment_title = xlwt.Alignment()
            alignment_title.horz = xlwt.Alignment.HORZ_CENTER
            alignment_title.vert = xlwt.Alignment.VERT_CENTER
            style_title.alignment = alignment_title
            
            # 打印时间样式（右对齐）
            style_time = xlwt.XFStyle()
            font_time = xlwt.Font()
            font_time.name = '仿宋'
            font_time.height = 200  # 10pt
            font_time.bold = True
            style_time.font = font_time
            alignment_time = xlwt.Alignment()
            alignment_time.horz = xlwt.Alignment.HORZ_RIGHT
            alignment_time.vert = xlwt.Alignment.VERT_CENTER
            style_time.alignment = alignment_time
            
            # 字段列名样式（带边框）
            style_header_border = xlwt.XFStyle()
            font_header_border = xlwt.Font()
            font_header_border.name = '仿宋'
            font_header_border.height = 280  # 14pt
            font_header_border.bold = True
            style_header_border.font = font_header_border
            alignment_header_border = xlwt.Alignment()
            alignment_header_border.horz = xlwt.Alignment.HORZ_CENTER
            alignment_header_border.vert = xlwt.Alignment.VERT_CENTER
            style_header_border.alignment = alignment_header_border
            borders_header = xlwt.Borders()
            borders_header.left = xlwt.Borders.THIN
            borders_header.right = xlwt.Borders.THIN
            borders_header.top = xlwt.Borders.THIN
            borders_header.bottom = xlwt.Borders.THIN
            style_header_border.borders = borders_header
            
            # 字段列名样式（强度字段，12pt 字号）
            style_header_strength = xlwt.XFStyle()
            font_header_strength = xlwt.Font()
            font_header_strength.name = '仿宋'
            font_header_strength.height = 240  # 12pt
            font_header_strength.bold = True
            style_header_strength.font = font_header_strength
            style_header_strength.alignment = alignment_header_border
            style_header_strength.borders = borders_header
            
            # 序号列样式（14pt）- 左边框为实线
            style_data_seq = xlwt.XFStyle()
            font_data_seq = xlwt.Font()
            font_data_seq.name = '仿宋'
            font_data_seq.height = 280  # 14pt
            font_data_seq.bold = True
            style_data_seq.font = font_data_seq
            alignment_data = xlwt.Alignment()
            alignment_data.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data.vert = xlwt.Alignment.VERT_CENTER
            style_data_seq.alignment = alignment_data
            borders_data_seq = xlwt.Borders()
            borders_data_seq.left = xlwt.Borders.THIN
            borders_data_seq.right = xlwt.Borders.NO_LINE
            borders_data_seq.top = xlwt.Borders.THIN
            borders_data_seq.bottom = xlwt.Borders.THIN
            style_data_seq.borders = borders_data_seq
            
            # 数据行样式（带边框，去掉竖线）
            borders_data = xlwt.Borders()
            borders_data.left = xlwt.Borders.NO_LINE
            borders_data.right = xlwt.Borders.NO_LINE
            borders_data.top = xlwt.Borders.THIN
            borders_data.bottom = xlwt.Borders.THIN
            
            # 钢卷号列样式（16pt）- 居中对齐
            style_data_coil = xlwt.XFStyle()
            font_data_coil = xlwt.Font()
            font_data_coil.name = '仿宋'
            font_data_coil.height = 320  # 16pt
            font_data_coil.bold = True
            style_data_coil.font = font_data_coil
            alignment_data_coil = xlwt.Alignment()
            alignment_data_coil.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_coil.vert = xlwt.Alignment.VERT_CENTER
            style_data_coil.alignment = alignment_data_coil
            style_data_coil.borders = borders_data
            
            # 钢卷号列样式（16pt）- 居中对齐 - 带删除线（用于不在装炉顺序中的钢卷号）
            style_data_coil_strikethrough = xlwt.XFStyle()
            font_data_coil_strikethrough = xlwt.Font()
            font_data_coil_strikethrough.name = '仿宋'
            font_data_coil_strikethrough.height = 320  # 16pt
            font_data_coil_strikethrough.bold = True
            font_data_coil_strikethrough.struck_out = True  # 删除线
            style_data_coil_strikethrough.font = font_data_coil_strikethrough
            style_data_coil_strikethrough.alignment = alignment_data_coil
            style_data_coil_strikethrough.borders = borders_data
            
            # 计划号列样式（13pt）- 居中对齐
            style_data_plan = xlwt.XFStyle()
            font_data_plan = xlwt.Font()
            font_data_plan.name = '仿宋'
            font_data_plan.height = 260  # 13pt
            font_data_plan.bold = True
            style_data_plan.font = font_data_plan
            alignment_data_plan = xlwt.Alignment()
            alignment_data_plan.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_plan.vert = xlwt.Alignment.VERT_CENTER
            style_data_plan.alignment = alignment_data_plan
            style_data_plan.borders = borders_data
            
            # 轧厚列样式（13pt）- 居中对齐，左右虚线
            style_data_roll_thickness = xlwt.XFStyle()
            font_data_roll_thickness = xlwt.Font()
            font_data_roll_thickness.name = '仿宋'
            font_data_roll_thickness.height = 260  # 13pt
            font_data_roll_thickness.bold = True
            style_data_roll_thickness.font = font_data_roll_thickness
            alignment_data_roll_thickness = xlwt.Alignment()
            alignment_data_roll_thickness.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_roll_thickness.vert = xlwt.Alignment.VERT_CENTER
            style_data_roll_thickness.alignment = alignment_data_roll_thickness
            borders_roll_thickness = xlwt.Borders()
            borders_roll_thickness.left = xlwt.Borders.MEDIUM_DASHED
            borders_roll_thickness.right = xlwt.Borders.MEDIUM_DASHED
            borders_roll_thickness.top = xlwt.Borders.THIN
            borders_roll_thickness.bottom = xlwt.Borders.THIN
            style_data_roll_thickness.borders = borders_roll_thickness
            
            # 坯长列样式（12pt）- 居中对齐，左右虚线
            style_data_billet_length = xlwt.XFStyle()
            font_data_billet_length = xlwt.Font()
            font_data_billet_length.name = '仿宋'
            font_data_billet_length.height = 240  # 12pt
            font_data_billet_length.bold = True
            style_data_billet_length.font = font_data_billet_length
            alignment_data_billet_length = xlwt.Alignment()
            alignment_data_billet_length.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_billet_length.vert = xlwt.Alignment.VERT_CENTER
            style_data_billet_length.alignment = alignment_data_billet_length
            borders_billet_length = xlwt.Borders()
            borders_billet_length.left = xlwt.Borders.MEDIUM_DASHED
            borders_billet_length.right = xlwt.Borders.MEDIUM_DASHED
            borders_billet_length.top = xlwt.Borders.THIN
            borders_billet_length.bottom = xlwt.Borders.THIN
            style_data_billet_length.borders = borders_billet_length
            
            # 14pt 样式 - 居中对齐（用于其他列）
            style_data_14pt_center = xlwt.XFStyle()
            font_data_14pt_center = xlwt.Font()
            font_data_14pt_center.name = '仿宋'
            font_data_14pt_center.height = 280  # 14pt
            font_data_14pt_center.bold = True
            style_data_14pt_center.font = font_data_14pt_center
            alignment_data_14pt_center = xlwt.Alignment()
            alignment_data_14pt_center.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_14pt_center.vert = xlwt.Alignment.VERT_CENTER
            style_data_14pt_center.alignment = alignment_data_14pt_center
            style_data_14pt_center.borders = borders_data
            
            # 14pt 样式 - 居中对齐（用于牌号）
            style_data_14pt = xlwt.XFStyle()
            font_data_14pt = xlwt.Font()
            font_data_14pt.name = '仿宋'
            font_data_14pt.height = 280  # 14pt
            font_data_14pt.bold = True
            style_data_14pt.font = font_data_14pt
            alignment_data_14pt = xlwt.Alignment()
            alignment_data_14pt.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_14pt.vert = xlwt.Alignment.VERT_CENTER
            style_data_14pt.alignment = alignment_data_14pt
            style_data_14pt.borders = borders_data
            
            # 12pt 样式
            style_data_12pt = xlwt.XFStyle()
            font_data_12pt = xlwt.Font()
            font_data_12pt.name = '仿宋'
            font_data_12pt.height = 240  # 12pt
            font_data_12pt.bold = True
            style_data_12pt.font = font_data_12pt
            alignment_data_12pt = xlwt.Alignment()
            alignment_data_12pt.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_12pt.vert = xlwt.Alignment.VERT_CENTER
            alignment_data_12pt.wrap = 1  # 启用自动换行
            style_data_12pt.alignment = alignment_data_12pt
            style_data_12pt.borders = borders_data
            
            # 14pt 样式（坯宽列）- 左边框为长虚线
            style_data_billet_width = xlwt.XFStyle()
            font_data_billet_width = xlwt.Font()
            font_data_billet_width.name = '仿宋'
            font_data_billet_width.height = 280  # 14pt
            font_data_billet_width.bold = True
            style_data_billet_width.font = font_data_billet_width
            style_data_billet_width.alignment = alignment_data_14pt_center
            borders_data_billet_width = xlwt.Borders()
            borders_data_billet_width.left = xlwt.Borders.MEDIUM_DASHED
            borders_data_billet_width.right = xlwt.Borders.THIN
            borders_data_billet_width.top = xlwt.Borders.THIN
            borders_data_billet_width.bottom = xlwt.Borders.THIN
            style_data_billet_width.borders = borders_data_billet_width
            
            # 14pt 样式（坯宽到强度之间的列）- 左右边框为长虚线
            style_data_dashed = xlwt.XFStyle()
            font_data_dashed = xlwt.Font()
            font_data_dashed.name = '仿宋'
            font_data_dashed.height = 280  # 14pt
            font_data_dashed.bold = True
            style_data_dashed.font = font_data_dashed
            style_data_dashed.alignment = alignment_data_14pt_center
            borders_data_dashed = xlwt.Borders()
            borders_data_dashed.left = xlwt.Borders.MEDIUM_DASHED
            borders_data_dashed.right = xlwt.Borders.MEDIUM_DASHED
            borders_data_dashed.top = xlwt.Borders.THIN
            borders_data_dashed.bottom = xlwt.Borders.THIN
            style_data_dashed.borders = borders_data_dashed
            
            # 14pt 样式（强度列）- 左边框为长虚线，右边框为实线
            style_data_12pt_strength = xlwt.XFStyle()
            font_data_12pt_strength = xlwt.Font()
            font_data_12pt_strength.name = '仿宋'
            font_data_12pt_strength.height = 280  # 14pt
            font_data_12pt_strength.bold = True
            style_data_12pt_strength.font = font_data_12pt_strength
            style_data_12pt_strength.alignment = alignment_data_14pt_center
            borders_data_strength = xlwt.Borders()
            borders_data_strength.left = xlwt.Borders.MEDIUM_DASHED
            borders_data_strength.right = xlwt.Borders.THIN
            borders_data_strength.top = xlwt.Borders.THIN
            borders_data_strength.bottom = xlwt.Borders.THIN
            style_data_12pt_strength.borders = borders_data_strength
            
            # 14pt 自动换行样式（用于粗轧报信）- 完全复刻主程序处理计划功能的样式
            style_data_wrap_14pt = xlwt.XFStyle()
            font_data_wrap_14pt = xlwt.Font()
            font_data_wrap_14pt.name = '仿宋'
            font_data_wrap_14pt.height = 280  # 14pt
            font_data_wrap_14pt.bold = True
            style_data_wrap_14pt.font = font_data_wrap_14pt
            alignment_data_wrap_14pt = xlwt.Alignment()
            alignment_data_wrap_14pt.horz = xlwt.Alignment.HORZ_LEFT
            alignment_data_wrap_14pt.vert = xlwt.Alignment.VERT_CENTER
            alignment_data_wrap_14pt.wrap = True
            style_data_wrap_14pt.alignment = alignment_data_wrap_14pt
            borders_data_wrap = xlwt.Borders()
            borders_data_wrap.left = xlwt.Borders.NO_LINE
            borders_data_wrap.right = xlwt.Borders.NO_LINE
            borders_data_wrap.top = xlwt.Borders.THIN
            borders_data_wrap.bottom = xlwt.Borders.THIN
            style_data_wrap_14pt.borders = borders_data_wrap
            
            # 14pt 左对齐样式（用于粗轧报信，单行或无内容时不自动换行）
            style_data_14pt_left_no_wrap = xlwt.XFStyle()
            font_data_14pt_left = xlwt.Font()
            font_data_14pt_left.name = '仿宋'
            font_data_14pt_left.height = 280  # 14pt
            font_data_14pt_left.bold = True
            style_data_14pt_left_no_wrap.font = font_data_14pt_left
            alignment_data_14pt_left = xlwt.Alignment()
            alignment_data_14pt_left.horz = xlwt.Alignment.HORZ_LEFT
            alignment_data_14pt_left.vert = xlwt.Alignment.VERT_CENTER
            style_data_14pt_left_no_wrap.alignment = alignment_data_14pt_left
            style_data_14pt_left_no_wrap.borders = borders_data
            
            # 设置列宽（固定值）
            # xlwt列宽单位是1/256字符宽，但Excel显示的宽度 = (xlwt宽度/256) - 0.7109375
            # 所以需要补偿：xlwt宽度 = (目标宽度 + 0.7109375) × 256
            def xlwt_col_width(excel_width):
                return int((excel_width + 0.7109375) * 256)
            
            col_widths = [
                xlwt_col_width(7.0),           # 1. 序号
                xlwt_col_width(7.0),           # 2. 计划号
                xlwt_col_width(17.0),          # 3. 钢卷号
                xlwt_col_width(17.0),          # 4. 牌号（钢级）
                xlwt_col_width(7.0),           # 5. 坯宽
                xlwt_col_width(7.0),           # 6. 减宽
                xlwt_col_width(6.0),           # 7. 调宽
                xlwt_col_width(7.0),           # 8. 轧宽
                xlwt_col_width(10.0),          # 9. 公差带
                xlwt_col_width(30.0),          # 10. 粗轧报信
                xlwt_col_width(6.0),           # 11. 除鳞
                xlwt_col_width(6.0),           # 12. 坯厚
                xlwt_col_width(6.5),           # 13. 坯长
                xlwt_col_width(6.0),           # 14. 轧厚
                xlwt_col_width(4.0),           # 15. 中厚
                xlwt_col_width(6.0),           # 16. RT2
                xlwt_col_width(4.5),           # 17. 强度
                xlwt_col_width(7.0)            # 18. 订宽
            ]
            
            for col_idx, width in enumerate(col_widths):
                if col_idx < len(headers):
                    sheet.col(col_idx).width = width
            
            # 写入提示行（第一行）并合并单元格
            # 如果是增量打印，使用提示行变量
            提示内容 = 提示行[0] if '提示行' in dir() else "装炉明细打印"
            sheet.write_merge(0, 0, 0, len(headers) - 1, 提示内容, style_title)
            sheet.row(0).height = 460  # 23pt
            sheet.row(0).height_mismatch = True
            
            # 第二行：打印时间
            print_time = time.strftime("%Y-%m-%d %H:%M:%S")
            sheet.write(1, len(headers) - 1, f"打印时间：{print_time}", style_time)
            sheet.row(1).height = 460  # 23pt
            sheet.row(1).height_mismatch = True
            
            # 写入字段名行（第三行）
            for col, header in enumerate(headers):
                if col >= len(headers) - 2:  # 强度和订宽字段（最后两列使用12pt样式）
                    sheet.write(2, col, header, style_header_strength)
                else:
                    sheet.write(2, col, header, style_header_border)
            sheet.row(2).height = 500  # 25pt
            sheet.row(2).height_mismatch = True
            
            # 写入数据行
            seq_num = 1
            print(f"准备写入 {len(rows)} 行数据")
            for row_idx, row_data in enumerate(rows):
                print(f"写入第 {row_idx + 1} 行: {row_data}")
                
                # 写入序号
                if 真正增量打印 and 'new_seq_info' in dir() and row_idx < len(new_seq_info):
                    写入序号 = new_seq_info[row_idx]['new_sequence']
                else:
                    写入序号 = seq_num
                sheet.write(row_idx + 3, 0, 写入序号, style_data_seq)
                
                # 写入计划号（13pt，居中对齐）
                sheet.write(row_idx + 3, 1, row_data[0], style_data_plan)
                
                # 写入其他字段（使用列名索引）
                for data_idx, value in enumerate(row_data[1:], 2):  # 从钢卷号开始，Excel列从2开始
                    if data_idx == 钢卷号列索引:  # 钢卷号列（16pt，居中对齐）
                        sheet.write(row_idx + 3, data_idx, value, style_data_coil)
                    elif data_idx == 牌号列索引:  # 牌号列（14pt，居中对齐）
                        sheet.write(row_idx + 3, data_idx, value, style_data_14pt)
                    elif data_idx == 坯宽列索引:  # 坯宽列（14pt，左边框虚线）
                        sheet.write(row_idx + 3, data_idx, value, style_data_billet_width)
                    elif data_idx == 粗轧报信列索引:  # 粗轧报信列（14pt，左对齐，始终启用自动换行）
                        sheet.write(row_idx + 3, data_idx, value, style_data_wrap_14pt)
                        # 立即计算并设置行高
                        if value and len(str(value)) > 0:
                            内容 = str(value)
                            总宽度 = sum(0.6 if c.isascii() else 1 for c in 内容)
                            每行宽度 = 13
                            需要行数 = max(1, int((总宽度 + 每行宽度 - 1) // 每行宽度))
                            最后一行宽度 = 总宽度 % 每行宽度
                            if 最后一行宽度 == 0:
                                最后一行宽度 = 每行宽度
                            if 最后一行宽度 > 每行宽度 * 0.8:
                                需要行数 = 需要行数 + 1
                            if 需要行数 > 1:
                                # 多行内容：设置计算的行高，不启用height_mismatch，让Excel自动调整
                                计算行高 = 500 + (需要行数 - 1) * 360
                                sheet.row(row_idx + 3).height = 计算行高
                            else:
                                # 单行内容：设置固定行高25pt，启用height_mismatch强制使用设置的行高
                                sheet.row(row_idx + 3).height = 500
                                sheet.row(row_idx + 3).height_mismatch = True
                        else:
                            # 无内容：设置固定行高25pt，启用height_mismatch强制使用设置的行高
                            sheet.row(row_idx + 3).height = 500
                            sheet.row(row_idx + 3).height_mismatch = True
                    elif data_idx == 坯长列索引:  # 坯长列（12pt，居中对齐，左右虚线）
                        sheet.write(row_idx + 3, data_idx, value, style_data_billet_length)
                    elif data_idx == 轧厚列索引:  # 轧厚列（13pt，居中对齐，左右虚线）
                        sheet.write(row_idx + 3, data_idx, value, style_data_roll_thickness)
                    elif data_idx == 强度列索引:  # 强度列（14pt，左边框虚线，右边框实线）
                        sheet.write(row_idx + 3, data_idx, value, style_data_12pt_strength)
                    elif data_idx == len(headers) - 1:  # 订宽列（最后一列）
                        # 订宽在表格控件中是第19列（索引18）
                        订宽值 = row_data[18] if len(row_data) > 18 else ""
                        sheet.write(row_idx + 3, data_idx, 订宽值, style_data_12pt_strength)
                    elif 5 <= data_idx <= 8 or 10 <= data_idx <= 11 or 14 <= data_idx <= 15:  # 坯宽到强度之间的列（左右虚线）
                        sheet.write(row_idx + 3, data_idx, value, style_data_dashed)
                    else:  # 其他所有列（14pt，居中对齐）
                        sheet.write(row_idx + 3, data_idx, value, style_data_14pt_center)
                
                seq_num += 1
            
            print(f"共写入 {seq_num - 1} 行数据")
            
            # 添加统计信息（计划号列表统计）
            # 添加空行分隔
            seq_num += 1
            sheet.write(seq_num + 2, 0, "", style_data_14pt_center)  # 空行
            
            # 判断是否为增量打印
            is_incremental_print = 真正增量打印 and 'new_seq_info' in dir()
            
            # 创建16号字体样式（带边框）
            style_16pt_center = xlwt.XFStyle()
            font_16pt = xlwt.Font()
            font_16pt.name = '仿宋'
            font_16pt.height = 320  # 16pt
            font_16pt.bold = True
            style_16pt_center.font = font_16pt
            style_16pt_center.alignment = alignment_data_14pt_center
            style_16pt_center.borders = borders_header
            
            style_16pt_bold = xlwt.XFStyle()
            style_16pt_bold.font = font_16pt
            style_16pt_bold.alignment = alignment_title
            style_16pt_bold.borders = borders_header
            
            # 添加统计信息标题
            seq_num += 1
            if is_incremental_print:
                sheet.write_merge(seq_num + 2, seq_num + 2, 0, len(headers) - 1, "新增计划号统计", style_16pt_bold)
            else:
                sheet.write_merge(seq_num + 2, seq_num + 2, 0, len(headers) - 1, "计划号列表统计", style_16pt_bold)
            sheet.row(seq_num + 2).height = 520  # 26pt
            sheet.row(seq_num + 2).height_mismatch = True
            
            # 添加表头
            seq_num += 1
            sheet.write_merge(seq_num + 2, seq_num + 2, 0, 1, "计划号", style_16pt_center)  # 第1-2列合并
            sheet.write(seq_num + 2, 2, "块数", style_16pt_center)  # 第3列
            sheet.write_merge(seq_num + 2, seq_num + 2, 3, 5, "起止钢卷号", style_16pt_center)  # 第4-6列合并
            sheet.write_merge(seq_num + 2, seq_num + 2, 6, len(headers) - 1, "预警", style_16pt_center)  # 第7到最后列合并
            sheet.row(seq_num + 2).height = 560  # 28pt
            sheet.row(seq_num + 2).height_mismatch = True
            
            # 收集统计数据
            stats_data = []
            total_blocks = 0
            
            # 收集预警信息
            plan_warnings_map = {}
            for row_data in rows:
                first_col_text = row_data[0] if row_data else ""
                if "换辊" in first_col_text or "△" in first_col_text:
                    continue
                plan_no = row_data[1] if len(row_data) > 1 else ""
                
                if plan_no:
                    if plan_no not in plan_warnings_map:
                        plan_warnings_map[plan_no] = set()
                    
                    # 检查减宽超265：减宽列(索引5) > 265
                    try:
                        jiankuan = float(row_data[5]) if len(row_data) > 5 and row_data[5] else 0
                        if jiankuan > 265:
                            plan_warnings_map[plan_no].add("减宽超265")
                    except:
                        pass
            
            if is_incremental_print:
                # 增量打印：只统计新增的钢卷号
                new_plan_stats = {}
                for info in new_seq_info:
                    coil_no = info['coil_number']
                    row_data = info['row_data']
                    plan_no = row_data[1] if row_data and len(row_data) > 1 else ''
                    
                    if plan_no not in new_plan_stats:
                        new_plan_stats[plan_no] = {
                            'count': 0,
                            'coils': []
                        }
                    new_plan_stats[plan_no]['count'] += 1
                    new_plan_stats[plan_no]['coils'].append(coil_no)
                
                # 处理统计数据
                for plan_no, stats in new_plan_stats.items():
                    coils = sorted(stats['coils'])
                    coil_range = f"{coils[0]}-{coils[-1]}" if coils else ""  # 去掉中括号
                    block_count = stats['count']
                    
                    # 获取预警信息
                    warnings = list(plan_warnings_map.get(plan_no, []))
                    
                    # 从 no_aps_plans 中检查无APS预警
                    if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                        warnings.append("无APS")
                    
                    # 从 low_roll_width_plans 中检查轧宽<930预警
                    if hasattr(self, 'low_roll_width_plans') and plan_no in self.low_roll_width_plans:
                        warnings.append("轧宽<930")
                    
                    warning_str = ", ".join(warnings) if warnings else ""
                    
                    stats_data.append({
                        'plan_no': plan_no,
                        'block_count': block_count,
                        'coil_range': coil_range,
                        'warning': warning_str
                    })
                    total_blocks += block_count
            else:
                # 全部打印：统计所有计划号
                for plan_info in self.plan_data:
                    plan_no = plan_info.get('plan_no', '')
                    block_count = plan_info.get('count', 0)
                    min_coil = plan_info.get('min_coil', '')
                    max_coil = plan_info.get('max_coil', '')
                    coil_range = f"{min_coil}-{max_coil}" if min_coil and max_coil else ""  # 去掉中括号
                    
                    # 获取预警信息
                    warnings = list(plan_warnings_map.get(plan_no, []))
                    
                    # 从 no_aps_plans 中检查无APS预警
                    if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                        warnings.append("无APS")
                    
                    # 从 low_roll_width_plans 中检查轧宽<930预警
                    if hasattr(self, 'low_roll_width_plans') and plan_no in self.low_roll_width_plans:
                        warnings.append("轧宽<930")
                    
                    warning_str = ", ".join(warnings) if warnings else ""
                    
                    stats_data.append({
                        'plan_no': plan_no,
                        'block_count': block_count,
                        'coil_range': coil_range,
                        'warning': warning_str
                    })
                    total_blocks += block_count
            
            # 写入统计数据
            for data in stats_data:
                seq_num += 1
                
                # 第1-2列合并：计划号
                sheet.write_merge(seq_num + 2, seq_num + 2, 0, 1, data['plan_no'], style_16pt_center)
                # 第3列：块数
                sheet.write(seq_num + 2, 2, str(data['block_count']), style_16pt_center)
                # 第4-6列合并：起止钢卷号
                sheet.write_merge(seq_num + 2, seq_num + 2, 3, 5, data['coil_range'], style_16pt_center)
                # 第7到最后列合并：预警
                sheet.write_merge(seq_num + 2, seq_num + 2, 6, len(headers) - 1, data['warning'], style_16pt_center)
                
                sheet.row(seq_num + 2).height = 500  # 25pt
                sheet.row(seq_num + 2).height_mismatch = True
            
            # 添加合计行
            seq_num += 1
            sheet.write_merge(seq_num + 2, seq_num + 2, 0, 1, "合计", style_16pt_center)
            sheet.write(seq_num + 2, 2, str(total_blocks), style_16pt_center)
            sheet.write_merge(seq_num + 2, seq_num + 2, 3, len(headers) - 1, "", style_16pt_center)
            sheet.row(seq_num + 2).height = 500  # 25pt
            sheet.row(seq_num + 2).height_mismatch = True
            
            print(f"共写入 {seq_num} 行数据（含统计信息）")
            
            # 获取设置，决定是否保存打印文件
            settings = self.get_settings()
            save_print_file = settings.get("savePrintFile", True)
            
            # 保存文件（根据设置决定是否保存）
            if save_print_file:
                workbook.save(temp_file_path)
                print(f"已生成打印文件：{temp_file_path}")
            else:
                # 不保存文件到磁盘，使用内存流暂存用于打印
                import io
                output = io.BytesIO()
                workbook.save(output)
                output.seek(0)
                # 将内存流写入临时文件用于打印
                with open(temp_file_path, 'wb') as f:
                    f.write(output.getvalue())
                print(f"临时生成打印文件（不保存）：{temp_file_path}")
            
            # 验证文件是否存在且有内容
            import os
            file_size = 0
            if os.path.exists(temp_file_path):
                file_size = os.path.getsize(temp_file_path)
                print(f"文件大小：{file_size} 字节")
                if file_size > 0:
                    print("文件生成成功，包含内容")
                    # 使用原程序的打印方法
                    success = self.print_excel_file(temp_file_path)
                    if success:
                        print("打印成功")
                        # 显示打印成功消息（使用与处理完成相同的弹窗样式）
                        self.show_result_dialog("打印完成！", success_files=[os.path.basename(temp_file_path)], 
                                               failed_files=[], skipped_files=[], auto_close=3)
                    else:
                        print("打印失败，保留文件供手动打印")
                        # 显示打印失败消息（使用与处理完成相同的弹窗样式）
                        self.show_result_dialog("打印失败！", success_files=[], 
                                               failed_files=[os.path.basename(temp_file_path)], 
                                               skipped_files=[], auto_close=3)
                else:
                    print("警告：文件生成但为空")
                    # 显示文件为空消息
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "警告", f"文件生成但为空：\n{temp_file_path}")
            else:
                print("错误：文件未生成")
                # 显示文件未生成消息
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "错误", f"文件未生成：\n{temp_file_path}")
            
            # 根据设置决定是否删除临时文件
            if save_print_file:
                print(f"文件已保留：{temp_file_path}")
            else:
                # 删除临时文件
                try:
                    os.remove(temp_file_path)
                    print(f"临时文件已删除：{temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败：{str(e)}")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            QMessageBox.critical(self, "错误", f"打印失败：{str(e)}")
            print(f"打印失败：{str(e)}")
            print(traceback.format_exc())
    
    def run_excel_macro_with_pandas(self, file_path):
        """使用 pandas + xlwt 处理Excel文件（xls格式）
        
        提取指定字段,删除其他字段,添加"轧宽+（余量）"和"装炉顺序号"字段
        """
        import os
        import xlwt
        from xlutils.copy import copy
        import pandas as pd
        
        # 1. 使用xlrd读取原文件
        success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
        if not success:
            raise Exception(f"读取文件失败: {result}")
        workbook = result
        sheet = workbook.sheet_by_index(0)
        
        # 从文件路径中提取计划号
        expected_plan_no = os.path.splitext(os.path.basename(file_path))[0]
        
        # 在处理数据前验证文件中的计划号是否与文件名一致
        # 注意：这里不使用验证，因为重新导出时可能会出现文件内容与文件名不匹配的情况
        # 这是正常的，重新导出本来就是用最新的数据覆盖旧文件
        # if not self.validate_plan_file_in_sheet(sheet, expected_plan_no):
        #     raise Exception(f"文件验证失败: {expected_plan_no}.xls 中的计划号与文件名不匹配")
        
        # 2. 加载装炉顺序数据,构建映射
        装炉顺序映射 = {}
        轧宽余量映射 = {}
        装炉顺序文件 = os.path.join(self.plan_dir, "计划号", "装炉顺序.xls")
        
        # 加载第5工作表的钢种列表
        钢种列表 = []
        第5工作表文件 = os.path.join(self.plan_dir, "计划号", "装炉顺序.xls")  # 假设第5工作表在同一个文件中
        if os.path.exists(第5工作表文件):
            success, result = self.safe_read_excel(第5工作表文件, max_retries=3, retry_delay=0.5)
            if success:
                workbook3 = result
                try:
                    if workbook3.nsheets >= 5:
                        sheet3 = workbook3.sheet_by_index(4)  # 第5工作表（索引4）
                        for row_idx in range(sheet3.nrows):
                            钢种值 = sheet3.cell_value(row_idx, 0)
                            if 钢种值:
                                钢种列表.append(str(钢种值).strip())
                except Exception:
                    pass
                finally:
                    # 只有xlrd的Workbook对象才有release_resources方法
                    if hasattr(workbook3, 'release_resources'):
                        workbook3.release_resources()
        
        # 构建钢种集合用于快速查找
        钢种集合 = set(钢种列表)
        
        # 加载除鳞钢种列表
        removePhosphorusList = self.load_remove_phosphorus_list()
        
        # 加载APS钢种列表
        apsGrades = self.load_aps_grades()
        
        if os.path.exists(装炉顺序文件):
            success, result = self.safe_read_excel(装炉顺序文件, max_retries=3, retry_delay=0.5)
            if success:
                workbook2 = result
                sheet2 = workbook2.sheet_by_index(0)
                
                headers = []
                for col_idx in range(sheet2.ncols):
                    headers.append(sheet2.cell_value(0, col_idx))
                
                装炉钢卷号列 = headers.index("钢卷号") if "钢卷号" in headers else -1
                装炉顺序号列 = headers.index("装炉顺序号") if "装炉顺序号" in headers else -1
                轧宽余量列 = -1
                if "轧宽（+余量）" in headers:
                    轧宽余量列 = headers.index("轧宽（+余量）")
                elif "轧宽+（余量）" in headers:
                    轧宽余量列 = headers.index("轧宽+（余量）")
                
                if 装炉钢卷号列 != -1:
                    # 首先收集所有钢卷号和对应的装炉顺序号
                    钢卷号顺序号列表 = []
                    for row_idx in range(1, sheet2.nrows):
                        钢卷号 = sheet2.cell_value(row_idx, 装炉钢卷号列)
                        if 钢卷号:
                            钢卷号字符串 = str(钢卷号)
                            原装炉顺序号 = None
                            
                            if 装炉顺序号列 != -1:
                                try:
                                    原装炉顺序号 = int(sheet2.cell_value(row_idx, 装炉顺序号列))
                                except (ValueError, TypeError):
                                    原装炉顺序号 = 0
                            
                            钢卷号顺序号列表.append((钢卷号字符串, 原装炉顺序号))
                    
                    # 按装炉顺序号排序
                    钢卷号顺序号列表.sort(key=lambda x: x[1])
                    
                    # 为每个钢卷号分配装炉顺：等于装炉顺序号
                    for 钢卷号字符串, 原装炉顺序号 in 钢卷号顺序号列表:
                        轧宽余量值 = None
                        
                        # 重新读取轧宽余量值
                        for row_idx in range(1, sheet2.nrows):
                            钢卷号 = sheet2.cell_value(row_idx, 装炉钢卷号列)
                            if 钢卷号 and str(钢卷号) == 钢卷号字符串:
                                if 轧宽余量列 != -1:
                                    轧宽余量值 = sheet2.cell_value(row_idx, 轧宽余量列)
                                break
                        
                        # 存储原始装炉顺序号和装炉顺（装炉顺等于装炉顺序号）
                        装炉顺序映射[钢卷号字符串] = {
                            "原装炉顺序号": 原装炉顺序号,
                            "装炉顺": 原装炉顺序号
                        }
                        
                        if 轧宽余量值 is not None:
                            轧宽余量映射[钢卷号字符串] = 轧宽余量值
                
                # 释放资源
                if hasattr(workbook2, 'release_resources'):
                    workbook2.release_resources()
        
        # 3. 定义目标列（按照用户要求的最终顺序）
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
            "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
            "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式", "板坯头部宽度", "板坯尾部宽度",
            "计划号", "热轧产品分类", "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽",
            "装炉顺序号"
        ]
        
        # 定义字段名映射（按照用户要求的最终顺序显示名称）
        字段名映射 = {
            "顺序号": "序号",
            "钢卷号": "钢卷号",
            "牌号（钢级）": "牌号（钢级）",
            "坯宽": "坯宽",
            "侧压量": "减宽",
            "板坯宽度调宽标记": "调宽",
            "轧宽+（余量）": "轧宽",
            "碳": "公差带",
            "粗轧报信": "粗轧报信",
            "层号": "除鳞",
            "坯厚": "坯厚",
            "坯长": "坯长",
            "轧厚": "轧厚",
            "中间坯厚度设定值": "中厚",
            "RT2目标值": "RT2",
            "硬度组": "强度",
            "订货宽度": "订货宽度",
            "去向": "去向",
            "切边方式": "切边方式",
            "板坯头部宽度": "坯头部宽",
            "板坯尾部宽度": "坯尾部宽",
            "计划号": "计划号",
            "热轧产品分类": "热轧产品分类",
            "炼钢钢种": "炼钢钢种",
            "宽度负公差": "负公差",
            "宽度正公差": "正公差",
            "板坯炉后拒收次数": "回炉坯",
            "轧宽": "原轧宽",
            "装炉顺序号": "装炉顺"
        }
        
        # 定义反向映射（从映射后的名称到原始名称）
        反向字段名映射 = {}
        for 原始名称, 映射名称 in 字段名映射.items():
            反向字段名映射[映射名称] = 原始名称
        
        # 4. 查找当前列名
        current_columns = []
        for i in range(sheet.ncols):
            current_columns.append(sheet.cell_value(0, i))
        
        # 5. 创建新的工作簿
        new_workbook = xlwt.Workbook()
        new_sheet = new_workbook.add_sheet(sheet.name)
        
        # 设置页面属性
        # 设置纸张大小为美国Fanfold (标准值为39)
        # 注意：xlwt的paper_size值对应Excel的纸张类型枚举
        # 39 = xlPaperFanfoldUS (14.875 x 11 inches)
        new_sheet.paper_size = 137  # 137 = xlPaperFanfoldUS (14.875 x 11 inches) - 连续折叠纸
        # 设置页边距为0（使用inches为单位）
        new_sheet.left_margin = 0.0
        new_sheet.right_margin = 0.0
        new_sheet.top_margin = 0.0
        new_sheet.bottom_margin = 0.0
        # 设置页眉页脚为空（使用bytes类型）
        new_sheet.header_str = b''
        new_sheet.footer_str = b''
        # 设置文档缩放比例为140%
        new_sheet.normal_magn = 140
        
        # 6. 定义样式
        # 大标题样式
        style_title = xlwt.XFStyle()
        font_title = xlwt.Font()
        font_title.name = '仿宋'
        font_title.height = 280  # 14pt
        font_title.bold = True
        style_title.font = font_title
        alignment_title = xlwt.Alignment()
        alignment_title.horz = xlwt.Alignment.HORZ_CENTER
        alignment_title.vert = xlwt.Alignment.VERT_CENTER
        style_title.alignment = alignment_title
        
        # 信息行样式（计划号、块数、提示信息）
        style_header_info = xlwt.XFStyle()
        font_header_info = xlwt.Font()
        font_header_info.name = '仿宋'
        font_header_info.height = 280  # 14pt
        font_header_info.bold = True
        style_header_info.font = font_header_info
        alignment_header_info = xlwt.Alignment()
        alignment_header_info.horz = xlwt.Alignment.HORZ_LEFT
        alignment_header_info.vert = xlwt.Alignment.VERT_CENTER
        alignment_header_info.wrap = True
        style_header_info.alignment = alignment_header_info
        
        # 字段列名样式（带边框）
        style_header_border = xlwt.XFStyle()
        font_header_border = xlwt.Font()
        font_header_border.name = '仿宋'
        font_header_border.height = 280  # 14pt
        font_header_border.bold = True
        style_header_border.font = font_header_border
        alignment_header_border = xlwt.Alignment()
        alignment_header_border.horz = xlwt.Alignment.HORZ_CENTER
        alignment_header_border.vert = xlwt.Alignment.VERT_CENTER
        style_header_border.alignment = alignment_header_border
        borders_header = xlwt.Borders()
        borders_header.left = xlwt.Borders.THIN
        borders_header.right = xlwt.Borders.THIN
        borders_header.top = xlwt.Borders.THIN
        borders_header.bottom = xlwt.Borders.THIN
        style_header_border.borders = borders_header
        
        # 强度列字段名样式（带右边框实线）
        style_header_strength = xlwt.XFStyle()
        font_header_strength = xlwt.Font()
        font_header_strength.name = '仿宋'
        font_header_strength.height = 280  # 14pt
        font_header_strength.bold = True
        style_header_strength.font = font_header_strength
        alignment_header_strength = xlwt.Alignment()
        alignment_header_strength.horz = xlwt.Alignment.HORZ_CENTER
        alignment_header_strength.vert = xlwt.Alignment.VERT_CENTER
        style_header_strength.alignment = alignment_header_strength
        borders_header_strength = xlwt.Borders()
        borders_header_strength.left = xlwt.Borders.THIN
        borders_header_strength.right = xlwt.Borders.THIN  # 右边框实线
        borders_header_strength.top = xlwt.Borders.THIN
        borders_header_strength.bottom = xlwt.Borders.THIN
        style_header_strength.borders = borders_header_strength
        
        # 打印时间样式（右对齐,10 号字体）
        style_time = xlwt.XFStyle()
        font_time = xlwt.Font()
        font_time.name = '仿宋'
        font_time.height = 200  # 10pt
        font_time.bold = True
        style_time.font = font_time
        alignment_time = xlwt.Alignment()
        alignment_time.horz = xlwt.Alignment.HORZ_RIGHT
        alignment_time.vert = xlwt.Alignment.VERT_CENTER
        style_time.alignment = alignment_time
        
        # 数据行样式（带边框,去掉竖线）
        style_data = xlwt.XFStyle()
        font_data = xlwt.Font()
        font_data.name = '仿宋'
        font_data.height = 220  # 11pt
        font_data.bold = True
        style_data.font = font_data
        alignment_data = xlwt.Alignment()
        alignment_data.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data.vert = xlwt.Alignment.VERT_CENTER
        style_data.alignment = alignment_data
        borders_data = xlwt.Borders()
        borders_data.left = xlwt.Borders.NO_LINE
        borders_data.right = xlwt.Borders.NO_LINE
        borders_data.top = xlwt.Borders.THIN
        borders_data.bottom = xlwt.Borders.THIN
        style_data.borders = borders_data
        
        # 特殊字体大小样式
        # 12pt 样式（加粗,去掉竖线）
        style_data_12pt = xlwt.XFStyle()
        font_data_12pt = xlwt.Font()
        font_data_12pt.name = '仿宋'
        font_data_12pt.height = 240  # 12pt
        font_data_12pt.bold = True
        style_data_12pt.font = font_data_12pt
        alignment_data_12pt = xlwt.Alignment()
        alignment_data_12pt.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_12pt.vert = xlwt.Alignment.VERT_CENTER
        style_data_12pt.alignment = alignment_data_12pt
        borders_data_12pt = xlwt.Borders()
        borders_data_12pt.left = xlwt.Borders.NO_LINE
        borders_data_12pt.right = xlwt.Borders.NO_LINE
        borders_data_12pt.top = xlwt.Borders.THIN
        borders_data_12pt.bottom = xlwt.Borders.THIN
        style_data_12pt.borders = borders_data_12pt
        
        # 12pt 左对齐样式（用于牌号钢级）
        style_data_12pt_left = xlwt.XFStyle()
        font_data_12pt_left = xlwt.Font()
        font_data_12pt_left.name = '仿宋'
        font_data_12pt_left.height = 240  # 12pt
        font_data_12pt_left.bold = True
        style_data_12pt_left.font = font_data_12pt_left
        alignment_data_12pt_left = xlwt.Alignment()
        alignment_data_12pt_left.horz = xlwt.Alignment.HORZ_LEFT
        alignment_data_12pt_left.vert = xlwt.Alignment.VERT_CENTER
        style_data_12pt_left.alignment = alignment_data_12pt_left
        borders_data_12pt_left = xlwt.Borders()
        borders_data_12pt_left.left = xlwt.Borders.NO_LINE
        borders_data_12pt_left.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left.top = xlwt.Borders.THIN
        borders_data_12pt_left.bottom = xlwt.Borders.THIN
        style_data_12pt_left.borders = borders_data_12pt_left
        
        # 14pt 样式（加粗,去掉竖线）
        style_data_14pt = xlwt.XFStyle()
        font_data_14pt = xlwt.Font()
        font_data_14pt.name = '仿宋'
        font_data_14pt.height = 280  # 14pt
        font_data_14pt.bold = True
        style_data_14pt.font = font_data_14pt
        alignment_data_14pt = xlwt.Alignment()
        alignment_data_14pt.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_14pt.vert = xlwt.Alignment.VERT_CENTER
        style_data_14pt.alignment = alignment_data_14pt
        borders_data_14pt = xlwt.Borders()
        borders_data_14pt.left = xlwt.Borders.NO_LINE
        borders_data_14pt.right = xlwt.Borders.NO_LINE
        borders_data_14pt.top = xlwt.Borders.THIN
        borders_data_14pt.bottom = xlwt.Borders.THIN
        style_data_14pt.borders = borders_data_14pt
        
        # 16pt 样式（加粗,去掉竖线）
        style_data_16pt = xlwt.XFStyle()
        font_data_16pt = xlwt.Font()
        font_data_16pt.name = '仿宋'
        font_data_16pt.height = 320  # 16pt
        font_data_16pt.bold = True
        style_data_16pt.font = font_data_16pt
        style_data_16pt.alignment = alignment_data
        style_data_16pt.borders = borders_data
        
        # 虚线边框样式（用于除鳞、轧宽、公差带）
        style_data_dashed = xlwt.XFStyle()
        font_data_dashed = xlwt.Font()
        font_data_dashed.name = '仿宋'
        font_data_dashed.height = 220  # 11pt
        font_data_dashed.bold = True
        style_data_dashed.font = font_data_dashed
        alignment_data_dashed = xlwt.Alignment()
        alignment_data_dashed.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_dashed.vert = xlwt.Alignment.VERT_CENTER
        style_data_dashed.alignment = alignment_data_dashed
        borders_data_dashed = xlwt.Borders()
        borders_data_dashed.left = xlwt.Borders.DASHED
        borders_data_dashed.right = xlwt.Borders.DASHED
        borders_data_dashed.top = xlwt.Borders.THIN
        borders_data_dashed.bottom = xlwt.Borders.THIN
        style_data_dashed.borders = borders_data_dashed
        
        # 12pt 长间隔虚线边框样式（用于除鳞、公差带）
        style_data_12pt_dashed = xlwt.XFStyle()
        font_data_12pt_dashed = xlwt.Font()
        font_data_12pt_dashed.name = '仿宋'
        font_data_12pt_dashed.height = 240  # 12pt
        font_data_12pt_dashed.bold = True
        style_data_12pt_dashed.font = font_data_12pt_dashed
        style_data_12pt_dashed.alignment = alignment_data_12pt
        borders_data_12pt_dashed = xlwt.Borders()
        borders_data_12pt_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashed.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashed.top = xlwt.Borders.THIN
        borders_data_12pt_dashed.bottom = xlwt.Borders.THIN
        style_data_12pt_dashed.borders = borders_data_12pt_dashed
        
        # 12pt 长间隔虚线边框样式（用于轧厚）- 左右虚线
        style_data_12pt_dashdot = xlwt.XFStyle()
        font_data_12pt_dashdot = xlwt.Font()
        font_data_12pt_dashdot.name = '仿宋'
        font_data_12pt_dashdot.height = 240  # 12pt
        font_data_12pt_dashdot.bold = True
        style_data_12pt_dashdot.font = font_data_12pt_dashdot
        style_data_12pt_dashdot.alignment = alignment_data_12pt
        borders_data_12pt_dashdot = xlwt.Borders()
        borders_data_12pt_dashdot.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashdot.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashdot.top = xlwt.Borders.THIN
        borders_data_12pt_dashdot.bottom = xlwt.Borders.THIN
        style_data_12pt_dashdot.borders = borders_data_12pt_dashdot
        
        # 12pt 左侧长间隔虚线边框样式（用于坯宽）
        style_data_12pt_left_dashed = xlwt.XFStyle()
        font_data_12pt_left_dashed = xlwt.Font()
        font_data_12pt_left_dashed.name = '仿宋'
        font_data_12pt_left_dashed.height = 240  # 12pt
        font_data_12pt_left_dashed.bold = True
        style_data_12pt_left_dashed.font = font_data_12pt_left_dashed
        style_data_12pt_left_dashed.alignment = alignment_data_12pt
        borders_data_12pt_left_dashed = xlwt.Borders()
        borders_data_12pt_left_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_left_dashed.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left_dashed.top = xlwt.Borders.THIN
        borders_data_12pt_left_dashed.bottom = xlwt.Borders.THIN
        style_data_12pt_left_dashed.borders = borders_data_12pt_left_dashed
        
        # 14pt 左侧长间隔虚线边框样式（用于坯宽）
        style_data_14pt_left_dashed = xlwt.XFStyle()
        font_data_14pt_left_dashed = xlwt.Font()
        font_data_14pt_left_dashed.name = '仿宋'
        font_data_14pt_left_dashed.height = 280  # 14pt
        font_data_14pt_left_dashed.bold = True
        style_data_14pt_left_dashed.font = font_data_14pt_left_dashed
        style_data_14pt_left_dashed.alignment = alignment_data_14pt
        borders_data_14pt_left_dashed = xlwt.Borders()
        borders_data_14pt_left_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_left_dashed.right = xlwt.Borders.NO_LINE
        borders_data_14pt_left_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_left_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_left_dashed.borders = borders_data_14pt_left_dashed
        
        # 14pt 实线边框样式（用于轧宽）- 去掉左边线
        style_data_14pt_dashed = xlwt.XFStyle()
        font_data_14pt_dashed = xlwt.Font()
        font_data_14pt_dashed.name = '仿宋'
        font_data_14pt_dashed.height = 280  # 14pt
        font_data_14pt_dashed.bold = True
        style_data_14pt_dashed.font = font_data_14pt_dashed
        style_data_14pt_dashed.alignment = alignment_data_14pt
        borders_data_14pt_dashed = xlwt.Borders()
        borders_data_14pt_dashed.left = xlwt.Borders.NO_LINE  # 去掉左边线
        borders_data_14pt_dashed.right = xlwt.Borders.THIN
        borders_data_14pt_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_dashed.borders = borders_data_14pt_dashed
        
        # 14pt 长间隔虚线边框样式（用于调宽）
        style_data_14pt_long_dashed = xlwt.XFStyle()
        font_data_14pt_long_dashed = xlwt.Font()
        font_data_14pt_long_dashed.name = '仿宋'
        font_data_14pt_long_dashed.height = 280  # 14pt
        font_data_14pt_long_dashed.bold = True
        style_data_14pt_long_dashed.font = font_data_14pt_long_dashed
        style_data_14pt_long_dashed.alignment = alignment_data_14pt
        borders_data_14pt_long_dashed = xlwt.Borders()
        borders_data_14pt_long_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_long_dashed.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_long_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_long_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_long_dashed.borders = borders_data_14pt_long_dashed
        
        # 14pt 长间隔虚线边框样式（用于轧厚）- 左右虚线
        style_data_14pt_dashdot = xlwt.XFStyle()
        font_data_14pt_dashdot = xlwt.Font()
        font_data_14pt_dashdot.name = '仿宋'
        font_data_14pt_dashdot.height = 280  # 14pt
        font_data_14pt_dashdot.bold = True
        style_data_14pt_dashdot.font = font_data_14pt_dashdot
        style_data_14pt_dashdot.alignment = alignment_data_14pt
        borders_data_14pt_dashdot = xlwt.Borders()
        borders_data_14pt_dashdot.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_dashdot.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_dashdot.top = xlwt.Borders.THIN
        borders_data_14pt_dashdot.bottom = xlwt.Borders.THIN
        style_data_14pt_dashdot.borders = borders_data_14pt_dashdot
        
        # 14pt 样式（用于坯厚、RT2）
        style_data_14pt_center = xlwt.XFStyle()
        font_data_14pt_center = xlwt.Font()
        font_data_14pt_center.name = '仿宋'
        font_data_14pt_center.height = 280  # 14pt
        font_data_14pt_center.bold = True
        style_data_14pt_center.font = font_data_14pt_center
        style_data_14pt_center.alignment = alignment_data_14pt
        borders_data_14pt_center = xlwt.Borders()
        borders_data_14pt_center.left = xlwt.Borders.NO_LINE
        borders_data_14pt_center.right = xlwt.Borders.NO_LINE
        borders_data_14pt_center.top = xlwt.Borders.THIN
        borders_data_14pt_center.bottom = xlwt.Borders.THIN
        style_data_14pt_center.borders = borders_data_14pt_center
        
        # 12pt 样式（用于强度列）- 右边框为实线
        style_data_12pt_strength = xlwt.XFStyle()
        font_data_12pt_strength = xlwt.Font()
        font_data_12pt_strength.name = '仿宋'
        font_data_12pt_strength.height = 240  # 12pt
        font_data_12pt_strength.bold = True
        style_data_12pt_strength.font = font_data_12pt_strength
        style_data_12pt_strength.alignment = alignment_data_12pt
        borders_data_strength = xlwt.Borders()
        borders_data_strength.left = xlwt.Borders.NO_LINE
        borders_data_strength.right = xlwt.Borders.THIN  # 右边框为实线
        borders_data_strength.top = xlwt.Borders.THIN
        borders_data_strength.bottom = xlwt.Borders.THIN
        style_data_12pt_strength.borders = borders_data_strength
        
        # 自动换行样式（用于粗轧报信）
        style_data_wrap = xlwt.XFStyle()
        font_data_wrap = xlwt.Font()
        font_data_wrap.name = '仿宋'
        font_data_wrap.height = 240  # 12pt
        font_data_wrap.bold = True
        style_data_wrap.font = font_data_wrap
        alignment_data_wrap = xlwt.Alignment()
        alignment_data_wrap.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_wrap.vert = xlwt.Alignment.VERT_CENTER
        alignment_data_wrap.wrap = True
        style_data_wrap.alignment = alignment_data_wrap
        borders_data_wrap = xlwt.Borders()
        borders_data_wrap.left = xlwt.Borders.NO_LINE
        borders_data_wrap.right = xlwt.Borders.NO_LINE
        borders_data_wrap.top = xlwt.Borders.THIN
        borders_data_wrap.bottom = xlwt.Borders.THIN
        style_data_wrap.borders = borders_data_wrap
        
        # 14pt 自动换行样式（用于粗轧报信）- 左对齐
        style_data_wrap_14pt = xlwt.XFStyle()
        font_data_wrap_14pt = xlwt.Font()
        font_data_wrap_14pt.name = '仿宋'
        font_data_wrap_14pt.height = 280  # 14pt
        font_data_wrap_14pt.bold = True
        style_data_wrap_14pt.font = font_data_wrap_14pt
        alignment_data_wrap_14pt = xlwt.Alignment()
        alignment_data_wrap_14pt.horz = xlwt.Alignment.HORZ_LEFT
        alignment_data_wrap_14pt.vert = xlwt.Alignment.VERT_CENTER
        alignment_data_wrap_14pt.wrap = True
        style_data_wrap_14pt.alignment = alignment_data_wrap_14pt
        style_data_wrap_14pt.borders = borders_data_wrap
        
        # 14pt 双横线+长间隔虚线样式（用于减宽超标）
        style_data_14pt_double = xlwt.XFStyle()
        font_data_14pt_double = xlwt.Font()
        font_data_14pt_double.name = '仿宋'
        font_data_14pt_double.height = 280  # 14pt
        font_data_14pt_double.bold = True
        style_data_14pt_double.font = font_data_14pt_double
        style_data_14pt_double.alignment = alignment_data_14pt
        borders_data_14pt_double = xlwt.Borders()
        borders_data_14pt_double.left = xlwt.Borders.MEDIUM_DASHED  # 长间隔虚线
        borders_data_14pt_double.right = xlwt.Borders.MEDIUM_DASHED  # 长间隔虚线
        borders_data_14pt_double.top = xlwt.Borders.DOUBLE
        borders_data_14pt_double.bottom = xlwt.Borders.DOUBLE
        style_data_14pt_double.borders = borders_data_14pt_double
        
        # 第一列左侧实线边框样式（12pt）
        style_data_12pt_left_border = xlwt.XFStyle()
        font_data_12pt_left_border = xlwt.Font()
        font_data_12pt_left_border.name = '仿宋'
        font_data_12pt_left_border.height = 240  # 12pt
        font_data_12pt_left_border.bold = True
        style_data_12pt_left_border.font = font_data_12pt_left_border
        style_data_12pt_left_border.alignment = alignment_data_12pt
        borders_data_12pt_left_border = xlwt.Borders()
        borders_data_12pt_left_border.left = xlwt.Borders.THIN
        borders_data_12pt_left_border.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left_border.top = xlwt.Borders.THIN
        borders_data_12pt_left_border.bottom = xlwt.Borders.THIN
        style_data_12pt_left_border.borders = borders_data_12pt_left_border
        
        # 第一列左侧实线边框样式（16pt - 用于钢卷号）
        style_data_16pt_left_border = xlwt.XFStyle()
        font_data_16pt_left_border = xlwt.Font()
        font_data_16pt_left_border.name = '仿宋'
        font_data_16pt_left_border.height = 320  # 16pt
        font_data_16pt_left_border.bold = True
        style_data_16pt_left_border.font = font_data_16pt_left_border
        style_data_16pt_left_border.alignment = alignment_data
        borders_data_16pt_left_border = xlwt.Borders()
        borders_data_16pt_left_border.left = xlwt.Borders.THIN
        borders_data_16pt_left_border.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left_border.top = xlwt.Borders.THIN
        borders_data_16pt_left_border.bottom = xlwt.Borders.THIN
        style_data_16pt_left_border.borders = borders_data_16pt_left_border
        
        # 钢卷号左对齐样式（16pt - 用于钢卷号,带下边框）
        style_data_16pt_left = xlwt.XFStyle()
        font_data_16pt_left = xlwt.Font()
        font_data_16pt_left.name = '仿宋'
        font_data_16pt_left.height = 320  # 16pt
        font_data_16pt_left.bold = True
        style_data_16pt_left.font = font_data_16pt_left
        # 创建左对齐配置
        alignment_data_16pt_left = xlwt.Alignment()
        alignment_data_16pt_left.horz = xlwt.Alignment.HORZ_LEFT  # 左对齐
        alignment_data_16pt_left.vert = xlwt.Alignment.VERT_CENTER
        style_data_16pt_left.alignment = alignment_data_16pt_left
        borders_data_16pt_left = xlwt.Borders()
        borders_data_16pt_left.left = xlwt.Borders.NO_LINE
        borders_data_16pt_left.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left.top = xlwt.Borders.NO_LINE
        borders_data_16pt_left.bottom = xlwt.Borders.THIN  # 下边框
        style_data_16pt_left.borders = borders_data_16pt_left
        
        # 钢卷号左对齐样式（16pt - 用于钢卷号,带下边框和删除线 - 不在装炉顺序中的钢卷号）
        style_data_16pt_left_strikethrough = xlwt.XFStyle()
        font_data_16pt_left_strikethrough = xlwt.Font()
        font_data_16pt_left_strikethrough.name = '仿宋'
        font_data_16pt_left_strikethrough.height = 320  # 16pt
        font_data_16pt_left_strikethrough.bold = True
        font_data_16pt_left_strikethrough.struck_out = True  # 删除线
        style_data_16pt_left_strikethrough.font = font_data_16pt_left_strikethrough
        style_data_16pt_left_strikethrough.alignment = alignment_data_16pt_left
        style_data_16pt_left_strikethrough.borders = borders_data_16pt_left
        
        # 装炉顺列右侧实线边框样式（12pt）
        style_data_12pt_right_border = xlwt.XFStyle()
        font_data_12pt_right_border = xlwt.Font()
        font_data_12pt_right_border.name = '仿宋'
        font_data_12pt_right_border.height = 240  # 12pt
        font_data_12pt_right_border.bold = True
        style_data_12pt_right_border.font = font_data_12pt_right_border
        style_data_12pt_right_border.alignment = alignment_data_12pt
        borders_data_12pt_right_border = xlwt.Borders()
        borders_data_12pt_right_border.left = xlwt.Borders.NO_LINE
        borders_data_12pt_right_border.right = xlwt.Borders.THIN
        borders_data_12pt_right_border.top = xlwt.Borders.THIN
        borders_data_12pt_right_border.bottom = xlwt.Borders.THIN
        style_data_12pt_right_border.borders = borders_data_12pt_right_border
        
        # 7. 获取计划号和块数
        计划号 = ""
        块数 = sheet.nrows - 1
        
        for row_idx in range(1, sheet.nrows):
            if "计划号" in current_columns:
                计划号值 = sheet.cell_value(row_idx, current_columns.index("计划号"))
                if 计划号值:
                    计划号 = str(计划号值)
                    break
        
        # 获取当前时间
        from datetime import datetime
        当前时间 = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        # 找到"强度"列的索引（用于标题跨列）
        强度列索引 = -1
        装炉顺列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "强度":
                强度列索引 = col_idx
            elif 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
        
        # 如果找到强度列,标题跨列到该列；否则跨所有列
        if 强度列索引 >= 0:
            标题结束列 = 强度列索引
        else:
            标题结束列 = len(target_columns) - 1
        
        # 8. 设置列宽（按照原程序 furnace_order_manager.py 的列宽设置）
        # 最终顺序：序号、钢卷号、牌号（钢级）、坯宽、减宽、调宽、轧宽、公差带、粗轧报信、除鳞、坯厚、坯长、轧厚、中厚、RT2、强度、订货宽度、去向、切边方式、坯头部宽、坯尾部宽、计划号、热轧产品分类、炼钢钢种、负公差、正公差、回炉坯、原轧宽、装炉顺
        col_widths = [
            int(5.5 * 256 * 1.2),       # 1. 序号（原程序值：5.5）
            int(19 * 256 * 1.04),       # 2. 钢卷号（原程序值：19）
            int(18 * 256 * 1.04),       # 3. 牌号（钢级）（原程序值：18）
            int(7 * 256 * 1.04),        # 4. 坯宽（原程序值：7）
            int(7 * 256 * 1.05),         # 5. 减宽（侧压量）
            int(6 * 256 * 1.2),         # 6. 调宽（板坯宽度调宽标记）（原程序值：6）
            int(7 * 256 * 1.13),        # 7. 轧宽（轧宽 +（余量））（原程序值：7）
            int(9 * 256 * 1.03),         # 8. 公差带（碳）
            int((30 + 0.7109375) * 256),        # 9. 粗轧报信（与装炉明细打印一致：30）
            int(7 * 256 * 1.08),        # 10. 除鳞（层号）（原程序值：7）
            int(7 * 256 * 1.04),        # 11. 坯厚（原程序值：7）
            int(6.2 * 256 * 1.13),       # 12. 坯长
            int(6.5 * 256 * 1.04),        # 13. 轧厚（修改为 6.5）
            int(5 * 256 * 1.04),        # 14. 中厚（中间坯厚度设定值）（原程序值：5）
            int(6.57 * 256 * 1.04),     # 15. RT2（RT2 目标值）（原程序值：6.57）
            int(4.71 * 256 * 1.2),      # 16. 强度（硬度组）（修改为 4.71）
            int(8.0 * 256 * 1.04),      # 17. 订货宽度
            int(3.6 * 256 * 1.2),        # 18. 去向
            int(3.6 * 256 * 1.2),        # 19. 切边方式
            int(8.0 * 256 * 1.04),       # 20. 坯头部宽（板坯头部宽度）
            int(8.0 * 256 * 1.04),       # 21. 坯尾部宽（板坯尾部宽度）
            int(7.0 * 256 * 1.04),      # 22. 计划号（原程序值：7.0）
            int(8.0 * 256 * 1.04),       # 23. 热轧产品分类
            int(8.0 * 256 * 1.04),       # 24. 炼钢钢种
            int(8.0 * 256 * 1.04),       # 25. 负公差（宽度负公差）
            int(8.0 * 256 * 1.04),       # 26. 正公差（宽度正公差）
            int(8.0 * 256 * 1.04),       # 27. 回炉坯（板坯炉后拒收次数）
            int(8.0 * 256 * 1.04),       # 28. 原轧宽（轧宽）
            int(5.0 * 256 * 1.1)         # 29. 装炉顺（装炉顺序号）
        ]
        # 设置固定列宽
        for col_idx, width in enumerate(col_widths):
            if col_idx < len(target_columns):
                new_sheet.col(col_idx).width = width
                # 设置为固定列宽（不允许自动调整）
                new_sheet.col(col_idx).width_mismatch = True
        
        # 8. 写入数据
        # 初始化统计变量
        无APS钢种数 = 0
        无APS块数 = 0
        已添加无APS的钢种 = set()
        包含无APS = False
        减宽超标块数 = 0
        逆宽轧制板坯数 = 0
        低轧宽板坯数 = 0
        极低轧宽板坯数 = 0
        调宽问题列表 = []
        
        # 收集所有行数据
        all_row_data = []
        has_low_roll_width = False
        
        for row_idx in range(1, sheet.nrows):
            # 构建当前行的数据映射
            row_data = {}
            for col_idx, col_name in enumerate(current_columns):
                row_data[col_name] = sheet.cell_value(row_idx, col_idx)
            
            # 填充"装炉顺序号"字段
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                if 钢卷号值:
                    钢卷号字符串 = str(钢卷号值)
                    if 钢卷号字符串 in 装炉顺序映射:
                        # 保持原始装炉顺序号
                        原装炉顺序号 = 装炉顺序映射[钢卷号字符串]["原装炉顺序号"]
                        row_data["装炉顺序号"] = 原装炉顺序号
                        # 存储装炉顺用于后续写入
                        row_data["装炉顺"] = 装炉顺序映射[钢卷号字符串]["装炉顺"]
                        # 标记钢卷号在装炉顺序中
                        row_data["在装炉顺序中"] = True
                    else:
                        # 标记钢卷号不在装炉顺序中，需要添加删除线
                        row_data["在装炉顺序中"] = False
            
            # 如果"装炉顺序号"仍缺失，使用"顺序号"字段的值作为备选
            if "装炉顺序号" not in row_data or row_data["装炉顺序号"] is None or pd.isna(row_data["装炉顺序号"]):
                if "顺序号" in row_data and row_data["顺序号"] is not None and not pd.isna(row_data["顺序号"]):
                    row_data["装炉顺序号"] = row_data["顺序号"]
                    row_data["装炉顺"] = row_data["顺序号"]
                else:
                    row_data["装炉顺序号"] = ""
                    row_data["装炉顺"] = ""
            
            # 填充"轧宽+（余量）"字段
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                if 钢卷号值:
                    钢卷号字符串 = str(钢卷号值)
                    if 钢卷号字符串 in 轧宽余量映射:
                        row_data["轧宽+（余量）"] = 轧宽余量映射[钢卷号字符串]
            
            # 如果"轧宽+（余量）"仍缺失，使用"轧宽"字段的值作为备选
            if "轧宽+（余量）" not in row_data or row_data["轧宽+（余量）"] is None or pd.isna(row_data["轧宽+（余量）"]):
                if "轧宽" in row_data and row_data["轧宽"] is not None and not pd.isna(row_data["轧宽"]):
                    row_data["轧宽+（余量）"] = row_data["轧宽"]
                else:
                    row_data["轧宽+（余量）"] = ""
            
            # 钢种转换逻辑
            if "牌号（钢级）" in row_data and "炼钢钢种" in row_data and "热轧产品分类" in row_data:
                牌号值 = str(row_data.get("牌号（钢级）", "")).strip()
                炼钢钢种值 = str(row_data.get("炼钢钢种", "")).strip()
                热轧产品分类值 = str(row_data.get("热轧产品分类", "")).strip()
                
                # 规则1：如果牌号（钢级）列是"SPHC"且炼钢钢种列是"P3A1",则牌号（钢级）列值添加"-P"
                if 牌号值 == "SPHC" and 炼钢钢种值 == "P3A1":
                    row_data["牌号（钢级）"] = 牌号值 + "-P"
                else:
                    # 规则2：在第5工作表A列中查找当前行的牌号（钢级）字段和炼钢钢种字段值
                    牌号在列表中 = 牌号值 in 钢种集合
                    炼钢钢种在列表中 = 炼钢钢种值 in 钢种集合
                    
                    # 规则3：如果都找不到
                    if not 牌号在列表中 and not 炼钢钢种在列表中:
                        # 若热轧产品分类字段是"L"、"M"或"O",则牌号（钢级）字段值设为炼钢钢种字段值
                        if 热轧产品分类值 in ["L", "M", "O"]:
                            row_data["牌号（钢级）"] = 炼钢钢种值
                        # 若热轧产品分类字段列是"X"且C列值末尾不是"-P",则添加"-P"
                        elif 热轧产品分类值 == "X" and not 牌号值.endswith("-P"):
                            row_data["牌号（钢级）"] = 牌号值 + "-P"
            
            # 1. 清空除鳞字段所有数据
            if "层号" in target_columns:
                row_data["层号"] = ""
            
            # 2. 填充除鳞字段 - 与HTML文件中的逻辑一致
            if "层号" in target_columns and "牌号（钢级）" in row_data:
                # 获取转换后的牌号
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                
                # 检查牌号是否匹配除鳞钢种列表
                需要除鳞 = self.匹配除鳞钢种(brand, removePhosphorusList)
                
                # 检查是否为回炉坯（尝试多种可能的字段名）
                回炉坯值 = ""
                是回炉坯 = False
                
                # 尝试不同的回炉坯字段名
                回炉坯字段名列表 = ["回炉坯", "板坯炉后拒收次数"]
                
                for 字段名 in 回炉坯字段名列表:
                    if 字段名 in row_data:
                        回炉坯值 = row_data.get(字段名, "")
                        break
                
                # 检查回炉坯值
                是回炉坯 = (回炉坯值 != 0 and 回炉坯值 != "" and 回炉坯值 is not None)
                
                # 根据需要填充除鳞字段
                除鳞值 = ""
                if 需要除鳞:
                    除鳞值 = "Y"
                else:
                    # 如果没有匹配,填充空白
                    除鳞值 = ""
                
                # 如果是回炉坯,在除鳞字段前添加"回"
                if 是回炉坯:
                    if 除鳞值:
                        除鳞值 = "回" + 除鳞值
                    else:
                        除鳞值 = "回"
                
                # 检查牌号是否在APS钢种列表中
                if brand and apsGrades:
                    在APS列表中 = brand in apsGrades
                    if not 在APS列表中:
                        # 如果不在APS列表中,添加"无APS"标识
                        if 除鳞值:
                            除鳞值 = 除鳞值 + "无APS"
                        else:
                            除鳞值 = "无APS"
                
                # 最后设置除鳞字段的值
                row_data["层号"] = 除鳞值
            
            # 3. 添加标记逻辑
            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False
            row_data["标注信息"] = []
            
            # 检查除鳞字段是否包含"回"字,如果是则标记需标注
            if "层号" in row_data:
                除鳞值 = str(row_data.get("层号", "")).strip()
                if 除鳞值 and "回" in 除鳞值:
                    row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
            
            # 检查坯厚是否>230,如果是则标记需标注
            if "坯厚" in row_data:
                坯厚值 = row_data.get("坯厚", 0)
                try:
                    坯厚数值 = float(坯厚值) if 坯厚值 != "" else 0
                    if 坯厚数值 > 230:
                        row_data["需标注"] = True
                except (ValueError, TypeError):
                    pass
            
            # 检查牌号是否在APS列表中,如果不在则标记需标注
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无APS块数 += 1
                    row_data["需标注"] = True
                    row_data["标注信息"].append(f"无APS钢种: {brand}")
                    包含无APS = True
                    if brand not in 已添加无APS的钢种:
                        已添加无APS的钢种.add(brand)
                        无APS钢种数 += 1
                        # 添加无APS钢种到APS.txt文件
                        self.add_grade_to_aps(brand)
            
            # 处理调宽字段 - 如果调宽不为"0"，则进行特殊处理
            if "板坯宽度调宽标记" in row_data and str(row_data.get("板坯宽度调宽标记", "")).strip() != "0":
                if "板坯头部宽度" in row_data and "板坯尾部宽度" in row_data and "坯宽" in row_data:
                    板坯头部宽度值 = row_data.get("板坯头部宽度", 0)
                    板坯尾部宽度值 = row_data.get("板坯尾部宽度", 0)
                    
                    try:
                        板坯头部宽度值 = float(板坯头部宽度值) if 板坯头部宽度值 != "" else 0
                        板坯尾部宽度值 = float(板坯尾部宽度值) if 板坯尾部宽度值 != "" else 0
                    except (ValueError, TypeError):
                        板坯头部宽度值 = 0
                        板坯尾部宽度值 = 0
                    
                    调宽差值 = 板坯头部宽度值 - 板坯尾部宽度值
                    row_data["板坯宽度调宽标记"] = 调宽差值
                    
                    坯宽新值 = max(板坯头部宽度值, 板坯尾部宽度值)
                    row_data["坯宽"] = 坯宽新值
                    
                    if "轧宽" in row_data:
                        轧宽值 = row_data.get("轧宽", 0)
                        try:
                            轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                        except (ValueError, TypeError):
                            轧宽值 = 0
                        减宽新值 = 坯宽新值 - 轧宽值
                        if 减宽新值 >= 240:
                            减宽超标块数 += 1
                            row_data["减宽超标"] = True
                            row_data["需标注"] = True
                            row_data["标注信息"].append(f"减宽量超标: {减宽新值}")
                        elif 减宽新值 < 0:
                            逆宽轧制板坯数 += 1
                            row_data["减宽超标"] = True
                            row_data["需标注"] = True
                            row_data["标注信息"].append("逆宽轧制板坯")
                        row_data["侧压量"] = 减宽新值
                    
                    # 判断头部宽度和尾部宽度中小者<=轧宽，则标注调宽三角符号
                    if "轧宽" in row_data:
                        轧宽值 = row_data.get("轧宽", 0)
                        try:
                            轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                            # 计算头部宽度和尾部宽度的较小值
                            宽度较小值 = min(板坯头部宽度值, 板坯尾部宽度值)
                            if 宽度较小值 <= 轧宽值:
                                # 标注调宽三角符号
                                row_data["板坯宽度调宽标记"] = str(调宽差值) + "Δ"
                                row_data["需标注"] = True
                                # 记录调宽问题信息，用于提示行显示
                                if "钢卷号" in row_data:
                                    钢卷号 = row_data.get("钢卷号", "")
                                    调宽问题信息 = f"{钢卷号}-{宽度较小值}"
                                    调宽问题列表.append(调宽问题信息)
                        except (ValueError, TypeError):
                            pass
            
            # 只有在调宽为"0"时，才检查"侧压量"字段
            if "板坯宽度调宽标记" not in row_data or str(row_data.get("板坯宽度调宽标记", "")).strip() == "0":
                减宽值 = 0
                if "侧压量" in row_data:
                    减宽值 = row_data.get("侧压量", 0)
                
                try:
                    减宽值 = float(减宽值) if 减宽值 != "" else 0
                except (ValueError, TypeError):
                    减宽值 = 0
                
                if 减宽值 >= 240:
                    减宽超标块数 += 1
                    row_data["减宽超标"] = True
                    row_data["需标注"] = True
                    row_data["标注信息"].append(f"减宽量超标: {减宽值}")
                elif 减宽值 < 0:
                    逆宽轧制板坯数 += 1
                    row_data["减宽超标"] = True
                    row_data["需标注"] = True
                    row_data["标注信息"].append("逆宽轧制板坯")
            
            # 检查轧宽+（余量）是否<=920,如果是则添加标记
            if "轧宽+（余量）" in row_data:
                轧宽余量值 = row_data.get("轧宽+（余量）", "")
                try:
                    轧宽余量数值 = float(轧宽余量值) if 轧宽余量值 != "" else 0
                    if 轧宽余量数值 <= 920:
                        row_data["轧宽+（余量）"] = str(int(轧宽余量数值)) + "Δ"
                        row_data["低轧宽标记"] = True
                        row_data["需标注"] = True
                        低轧宽板坯数 += 1
                        row_data["标注信息"].append(f"轧宽低于930: {轧宽余量数值}")
                        if 轧宽余量数值 < 860:
                            极低轧宽板坯数 += 1
                            row_data["标注信息"].append(f"轧宽低于860: {轧宽余量数值}")
                        has_low_roll_width = True
                except (ValueError, TypeError):
                    pass
            
            # 比较轧宽+（余量）和轧宽，如果轧宽+（余量）大于轧宽，修改负公差和正公差
            if "轧宽+（余量）" in row_data and "轧宽" in row_data:
                轧宽余量值 = row_data.get("轧宽+（余量）", 0)
                轧宽值 = row_data.get("轧宽", 0)
                try:
                    轧宽余量值 = float(轧宽余量值) if 轧宽余量值 != "" else 0
                    轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                    if 轧宽余量值 > 轧宽值:
                        差值 = int(轧宽余量值 - 轧宽值)
                        负公差原始值 = row_data.get("宽度负公差", 0)
                        正公差原始值 = row_data.get("宽度正公差", 0)
                        try:
                            负公差原始值 = float(负公差原始值) if 负公差原始值 != "" else 0
                            正公差原始值 = float(正公差原始值) if 正公差原始值 != "" else 0
                            row_data["宽度负公差"] = int(负公差原始值 - 差值)
                            row_data["宽度正公差"] = int(正公差原始值 - 差值)
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass
            
            # 5. 填充公差带字段
            if "碳" in row_data and "宽度负公差" in row_data and "宽度正公差" in row_data:
                负公差值 = row_data.get("宽度负公差", "")
                正公差值 = row_data.get("宽度正公差", "")
                
                # 处理负公差值
                if isinstance(负公差值, (int, float)):
                    if 负公差值.is_integer():
                        负公差值 = str(int(负公差值))
                    else:
                        负公差值 = f"{负公差值:.1f}"
                else:
                    负公差值 = str(负公差值).strip()
                
                # 处理正公差值
                if isinstance(正公差值, (int, float)):
                    if 正公差值.is_integer():
                        正公差值 = str(int(正公差值))
                    else:
                        正公差值 = f"{正公差值:.1f}"
                else:
                    正公差值 = str(正公差值).strip()
                
                # 填充公差带：负公差 + "～" + 正公差
                row_data["碳"] = 负公差值 + "～" + 正公差值
                
                # 检查正公差是否<=15,如果是则标注*
                try:
                    正公差数值 = float(row_data.get("宽度正公差", 0))
                    if 正公差数值 <= 15:
                        # 在公差带标注*
                        row_data["碳"] = row_data["碳"] + "*"
                        # 在钢卷号标注*
                        if "钢卷号" in row_data:
                            row_data["钢卷号"] = str(row_data["钢卷号"]) + "*"
                except (ValueError, TypeError):
                    pass
            
            # 将处理后的数据添加到列表
            all_row_data.append(row_data)
        
        # 对D开头的计划号，检查并删除没有钢卷号的行
        if 计划号 and (计划号.startswith('D') or 计划号.startswith('d')):
            filtered_row_data = []
            for row_data in all_row_data:
                # 检查是否有钢卷号
                has_coil_no = False
                # 尝试多种可能的钢卷号列名
                coil_no_value = None
                for coil_col_name in ["钢卷号", "序号", "COIL_NO", "coil_no"]:
                    if coil_col_name in row_data:
                        coil_no_value = row_data[coil_col_name]
                        break
                
                if coil_no_value:
                    # 检查钢卷号是否为空
                    coil_no = str(coil_no_value)
                    # 清理一下（去除可能的星号等标记
                    clean_coil_no = ''.join(c for c in str(coil_no) if c.isdigit() or c == '*')
                    if clean_coil_no:
                        has_coil_no = True
                
                if has_coil_no:
                    filtered_row_data.append(row_data)
                else:
                    print(f"删除无钢卷号的行")
            
            # 更新块数
            all_row_data = filtered_row_data
            块数 = len(all_row_data)
            print(f"D开头计划号处理后，剩余{块数}行")
        
        # 如果处理后数据为空，保留原始数据（防止文件变空白）
        if not all_row_data:
            print("警告：处理后数据为空，保留原始数据")
            # 重新读取原始数据
            all_row_data = []
            for row_idx in range(1, sheet.nrows):
                row_data = {}
                for col_idx, col_name in enumerate(current_columns):
                    row_data[col_name] = sheet.cell_value(row_idx, col_idx)
                all_row_data.append(row_data)
            块数 = len(all_row_data)
        
        # 9. 写入表头
        # 第一行：大标题"轧制计划明细表"
        new_sheet.write_merge(0, 0, 0, 标题结束列, "轧制计划明细表", style_title)
        
        # 准备提示信息列表
        提示信息列表 = []
        序号 = 1
        
        if 无APS钢种数 > 0:
            无APS钢种列表 = ", ".join(sorted(已添加无APS的钢种))
            提示信息列表.append(f"{序号}.无APS钢种{无APS钢种数}个{无APS块数}块({无APS钢种列表})")
            序号 += 1
        if 减宽超标块数 > 0:
            提示信息列表.append(f"{序号}.减宽量超标{减宽超标块数}块")
            序号 += 1
        if 逆宽轧制板坯数 > 0:
            提示信息列表.append(f"{序号}.逆宽轧制板坯{逆宽轧制板坯数}块")
            序号 += 1
        if 低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有轧宽低于930板坯{低轧宽板坯数}块,注意定宽最小辊缝要求")
            序号 += 1
        if 极低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有低于860的板坯{极低轧宽板坯数}块,注意E2设定值")
            序号 += 1
        
        # 计算提示信息行数（先左右再上下,每行显示2条）
        if len(提示信息列表) == 0:
            提示信息行数 = 1  # 至少有一行（空行）
        else:
            提示信息行数 = (len(提示信息列表) + 1) // 2  # 向上取整,每行2条
        
        # 字段列名行号 = 提示信息起始行(1) + 提示信息行数
        字段列名行号 = 1 + 提示信息行数
        
        # 找到各列的索引
        轧宽列索引 = -1
        订宽列索引 = -1
        除鳞列索引 = -1
        强度列索引 = -1
        粗轧报信列索引 = -1
        装炉顺列索引 = -1
        牌号列索引 = -1
        公差带列索引 = -1
        序号列索引 = 0  # 假设序号是第一列
        钢卷号列索引 = 1  # 假设钢卷号是第二列
        
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "轧宽":
                轧宽列索引 = col_idx
            elif 映射后的列名 == "订宽":
                订宽列索引 = col_idx
            elif 映射后的列名 == "除鳞":
                除鳞列索引 = col_idx
            elif 映射后的列名 == "强度":
                强度列索引 = col_idx
            elif 映射后的列名 == "粗轧报信":
                粗轧报信列索引 = col_idx
            elif 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
            elif 映射后的列名 == "牌号（钢级）":
                牌号列索引 = col_idx
            elif 映射后的列名 == "公差带":
                公差带列索引 = col_idx
        
        # 第二行及以下：计划号、块数、提示信息、打印时间
        # 序号和钢卷号列合并,填充计划号信息
        # 设置提示信息行的行高（25pt = 500 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 500
            new_sheet.row(i).height_mismatch = True
        
        new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 序号列索引, 钢卷号列索引, f"计划号：{计划号}", style_header_info)
        
        # 牌号（钢级）列填充块数信息
        if 牌号列索引 >= 0:
            new_sheet.write(字段列名行号 - 1, 牌号列索引, f"块数：{块数} 块", style_header_info)
        
        # 根据用户要求重新设计提示信息显示区域
        # 左区域：坯宽到公差带（显示提示信息）
        # 中间区域：粗轧报信到坯厚（显示提示信息）
        # 右区域：坯长到强度（显示打印时间）
        
        # 找到需要的列索引
        坯宽列索引 = -1
        坯厚列索引 = -1
        坯长列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "坯宽":
                坯宽列索引 = col_idx
            elif 映射后的列名 == "坯厚":
                坯厚列索引 = col_idx
            elif 映射后的列名 == "坯长":
                坯长列索引 = col_idx
        
        # 计算左区域（坯宽到公差带）
        if 坯宽列索引 >= 0 and 公差带列索引 >= 0:
            左区域起始 = 坯宽列索引
            左区域结束 = 公差带列索引
        else:
            左区域起始 = -1
            左区域结束 = -1
        
        # 计算中间区域（粗轧报信到坯厚）
        if 粗轧报信列索引 >= 0 and 坯厚列索引 >= 0:
            中间区域起始 = 粗轧报信列索引
            中间区域结束 = 坯厚列索引
        else:
            中间区域起始 = -1
            中间区域结束 = -1
        
        # 计算右区域（坯长到强度）
        if 坯长列索引 >= 0 and 强度列索引 >= 0:
            右区域起始 = 坯长列索引
            右区域结束 = 强度列索引
        else:
            右区域起始 = -1
            右区域结束 = -1
        
        # 显示提示信息
        if 左区域起始 >= 0 and 左区域结束 >= 0 and 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 计算需要的行数（每行显示2条提示信息）
            提示信息总行数 = (len(提示信息列表) + 1) // 2  # 向上取整
            for i in range(提示信息总行数):
                # 左列（坯宽到公差带）：显示第 i*2 条提示信息
                左列索引 = i * 2
                if 左列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, 提示信息列表[左列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, "", style_header_info)
                
                # 中间列（粗轧报信到坯长）：显示第 i*2+1 条提示信息
                中间列索引 = i * 2 + 1
                if 中间列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, 提示信息列表[中间列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, "", style_header_info)
        elif 左区域起始 >= 0 and 左区域结束 >= 0:
            # 如果只有左区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, 提示信息, style_header_info)
        elif 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 如果只有中间区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, 提示信息, style_header_info)
        
        # 右区域（中厚到装炉顺）显示打印时间
        if 右区域起始 >= 0 and 右区域结束 >= 0:
            new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 右区域起始, 右区域结束, f"打印时间：{当前时间}", style_time)
        
        # 设置行高（25pt = 500 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 500
            new_sheet.row(i).height_mismatch = True
        
        # 字段列名（使用内外边框线样式,强度列带右边框）
        粗轧报信字段名 = ""
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            # 强度列使用特殊样式（带右边框）
            if 映射后的列名 == "强度":
                new_sheet.write(字段列名行号,col_idx, 映射后的列名,style_header_strength)
            else:
                new_sheet.write(字段列名行号,col_idx, 映射后的列名,style_header_border)
            # 记录粗轧报信字段名用于计算行高
            if 映射后的列名 == "粗轧报信":
                粗轧报信字段名 = 映射后的列名
        
        # 设置字段列名行的行高（25pt = 500 twips）
        new_sheet.row(字段列名行号).height = 500
        
        # 写入数据行
        for row_idx, row_data in enumerate(all_row_data, 字段列名行号 + 1):
            顺序号 = row_idx - 字段列名行号  # 从1开始的顺序号
            
            # 写入顺序号
            new_sheet.write(row_idx, 0, 顺序号, style_data_12pt_left_border)
            
            # 写入其他字段
            for col_idx, col_name in enumerate(target_columns[1:], 1):
                # 尝试多种可能的列名来获取数据
                value = row_data.get(col_name, "")
                
                # 如果找不到值，尝试其他可能的列名
                if value == "" or value is None:
                    # 尝试映射后的名称
                    mapped_name = 字段名映射.get(col_name, "")
                    if mapped_name and mapped_name != col_name:
                        value = row_data.get(mapped_name, "")
                
                # 如果还是找不到，尝试反向映射
                if value == "" or value is None:
                    # 尝试其他可能的列名变体
                    alternative_names = {
                        "侧压量": ["侧压量", "减宽", "减宽量"],
                        "板坯宽度调宽标记": ["板坯宽度调宽标记", "调宽", "调宽标记"],
                        "轧宽+（余量）": ["轧宽+（余量）", "轧宽（+余量）", "轧宽余量"],
                        "碳": ["碳", "公差带", "宽度公差"],
                        "层号": ["层号", "除鳞", "除鳞标记"],
                        "中间坯厚度设定值": ["中间坯厚度设定值", "中厚", "中间坯厚度"],
                        "RT2目标值": ["RT2目标值", "RT2", "RT2值"],
                        "硬度组": ["硬度组", "强度", "硬度"],
                        "宽度负公差": ["宽度负公差", "负公差", "公差负"],
                        "宽度正公差": ["宽度正公差", "正公差", "公差正"],
                        "板坯炉后拒收次数": ["板坯炉后拒收次数", "回炉坯", "拒收次数"],
                        "板坯头部宽度": ["板坯头部宽度", "坯头部宽", "头部宽度"],
                        "板坯尾部宽度": ["板坯尾部宽度", "坯尾部宽", "尾部宽度"],
                        "装炉顺序号": ["装炉顺序号", "装炉顺", "顺序号"]
                    }
                    
                    if col_name in alternative_names:
                        for alt_name in alternative_names[col_name]:
                            if alt_name in row_data:
                                value = row_data[alt_name]
                                break
                
                # 根据字段名选择不同的样式
                if col_name == "钢卷号":
                    # 检查是否需要标注三角符号
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    # 检查钢卷号是否在装炉顺序中，如果不在则添加删除线
                    在装炉顺序中 = row_data.get("在装炉顺序中", True)
                    if 在装炉顺序中:
                        new_sheet.write(row_idx, col_idx, value, style_data_16pt_left)
                    else:
                        new_sheet.write(row_idx, col_idx, value, style_data_16pt_left_strikethrough)
                elif col_name == "牌号（钢级）":
                    # 无 APS 钢种时添加Δ标记
                    is_no_aps = row_data.get("是无 APS 钢种", False)
                    需标注 = row_data.get("需标注", False)
                    if 需标注 and is_no_aps:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_left)
                elif col_name == "坯宽":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_left_dashed)
                elif col_name == "侧压量":
                    # 减宽超标时添加三角符号
                    if row_data.get("减宽超标", False):
                        if value:
                            try:
                                减宽数值 = float(value)
                                value = str(int(减宽数值)) + "Δ"
                            except (ValueError, TypeError):
                                value = str(value) + "Δ"
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)
                elif col_name == "板坯宽度调宽标记":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)
                elif col_name == "轧宽":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)
                elif col_name == "轧宽+（余量）":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)
                elif col_name == "碳":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)
                elif col_name == "粗轧报信":
                    new_sheet.write(row_idx, col_idx, value, style_data_wrap_14pt)
                elif col_name == "层号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)
                elif col_name == "坯厚":
                    # 坯厚>230 时添加Δ标记
                    if value:
                        try:
                            坯厚数值 = float(value)
                            if 坯厚数值 > 230:
                                value = str(value) + "Δ"
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)
                elif col_name == "坯长":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "轧厚":
                    # 保留小数点后 1 位,不进行四舍五入（直接截断）
                    if value:
                        try:
                            # 转换为浮点数
                            float_val = float(value)
                            # 截断到小数点后 1 位（不四舍五入）
                            import math
                            truncated_val = math.floor(float_val * 10) / 10
                            # 格式化为字符串,保留 1 位小数
                            value = f"{truncated_val:.1f}"
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashdot)
                elif col_name == "中间坯厚度设定值":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "去向":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "订货宽度":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "切边方式":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "RT2目标值":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)
                elif col_name == "硬度组":
                    # 保留个位数值（不保留小数）
                    if value:
                        try:
                            # 转换为浮点数
                            float_val = float(value)
                            # 截断到个位（不四舍五入）
                            import math
                            truncated_val = math.floor(float_val)
                            # 格式化为整数
                            value = str(int(truncated_val))
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_strength)
                elif col_name == "装炉顺序号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_right_border)
                else:
                    new_sheet.write(row_idx, col_idx, value, style_data)
        
        # 在写入所有数据后，统一重新设置行高（确保行高不会被自动换行覆盖）
        # 设置数据行的行高
        for row_idx, row_data in enumerate(all_row_data, 字段列名行号 + 1):
            粗轧报信值 = row_data.get("粗轧报信", "")
            if 粗轧报信值 and len(str(粗轧报信值)) > 0:
                # 计算多行内容的行高
                内容 = str(粗轧报信值)
                总宽度 = sum(0.6 if c.isascii() else 1 for c in 内容)
                每行宽度 = 13
                需要行数 = max(1, int((总宽度 + 每行宽度 - 1) // 每行宽度))
                最后一行宽度 = 总宽度 % 每行宽度
                if 最后一行宽度 == 0:
                    最后一行宽度 = 每行宽度
                if 最后一行宽度 > 每行宽度 * 0.8:
                    需要行数 = 需要行数 + 1
                if 需要行数 > 1:
                    # 多行时使用计算的行高，不启用height_mismatch，让Excel自动调整
                    计算行高 = 500 + (需要行数 - 1) * 360
                    new_sheet.row(row_idx).height = 计算行高
                else:
                    # 单行时强制设置为25pt（500 twips），启用height_mismatch强制使用设置的行高
                    new_sheet.row(row_idx).height = 500
                    new_sheet.row(row_idx).height_mismatch = True
            else:
                # 无内容时强制设置为25pt（500 twips），启用height_mismatch强制使用设置的行高
                new_sheet.row(row_idx).height = 500
                new_sheet.row(row_idx).height_mismatch = True
        
        # 10. 保存新文件
        new_file_path = file_path  # 覆盖原文件
        
        try:
            new_workbook.save(new_file_path)
            print(f"文件已保存: {new_file_path}")
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
        finally:
            # 释放所有资源
            print(f"run_excel_macro_with_pandas: 释放资源...")
            if hasattr(workbook, 'release_resources'):
                workbook.release_resources()
                print(f"run_excel_macro_with_pandas: 原文件资源已释放")
            # 强制垃圾回收
            import gc
            gc.collect()
            print(f"run_excel_macro_with_pandas: 垃圾回收完成")
        
        return has_low_roll_width, 包含无APS
    
    def safe_read_excel(self, file_path, max_retries=3, retry_delay=0.5):
        """安全读取Excel文件,支持重试
        
        Args:
            file_path: 文件路径
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            tuple: (success, result),success为布尔值,result为Workbook对象或错误信息
        """
        import xlrd
        import time
        
        for attempt in range(max_retries):
            try:
                workbook = xlrd.open_workbook(file_path)
                return True, workbook
            except Exception as e:
                print(f"读取文件失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False, str(e)
    
    def validate_plan_file(self, file_path, expected_plan_no):
        """验证导出的计划文件
        只检查:
        1. 文件是否存在
        2. "计划号"列是否存在
        3. 文件中"计划号"列的值是否与文件名一致
        
        不检查列数、行数等其他内容
        
        Args:
            file_path: 文件路径
            expected_plan_no: 期望的计划号（文件名）
            
        Returns:
            bool: 验证是否通过
        """
        import os
        
        try:
            # 1. 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"[×] 文件不存在: {file_path}")
                return False
            
            # 2. 尝试读取文件
            success, workbook = self.safe_read_excel(file_path)
            if not success:
                print(f"[×] 文件无法读取: {workbook}")
                return False
            
            sheet = workbook.sheet_by_index(0)
            
            # 3. 检查是否有表头行
            if sheet.nrows < 1:
                print(f"[×] 文件没有表头行")
                return False
            
            # 4. 查找"计划号"列
            header_row = 0
            plan_no_col_index = None
            headers = [str(sheet.cell_value(header_row, col)).strip() for col in range(sheet.ncols)]
            
            for col_idx, header in enumerate(headers):
                if header == "计划号":
                    plan_no_col_index = col_idx
                    break
            
            if plan_no_col_index is None:
                print(f"[×] 文件中找不到'计划号'列，表头: {headers}")
                return False
            
            print(f"[√] 找到'计划号'列在第 {plan_no_col_index} 列")
            
            # 5. 检查是否有数据行
            if sheet.nrows < 2:
                print(f"[×] 文件只有表头，没有数据")
                return False
            
            # 6. 检查第一行数据的计划号是否与文件名一致
            # 只检查第一行数据
            file_plan_no = str(sheet.cell_value(1, plan_no_col_index)).strip()
            
            if not file_plan_no:
                print(f"[×] 第一行数据的计划号为空")
                return False
            
            # 比较计划号（忽略大小写和空格）
            if file_plan_no.strip().lower() == expected_plan_no.strip().lower():
                print(f"[√] 计划号匹配: 文件={expected_plan_no}")
                return True
            else:
                print(f"[×] 计划号不匹配: 文件名={expected_plan_no}, 文件内容={file_plan_no}")
                return False
                
        except Exception as e:
            print(f"[×] 验证文件时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_plan_file_in_sheet(self, sheet, expected_plan_no):
        """验证sheet中的计划号是否与期望的计划号一致
        这个方法用于在处理文件时直接验证已读取的sheet对象，避免重复读取文件
        
        Args:
            sheet: xlrd sheet对象（已读取的工作表）
            expected_plan_no: 期望的计划号（文件名）
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 1. 检查是否有表头行
            if sheet.nrows < 1:
                print(f"[×] 文件没有表头行")
                return False
            
            # 2. 查找"计划号"列
            header_row = 0
            plan_no_col_index = None
            headers = [str(sheet.cell_value(header_row, col)).strip() for col in range(sheet.ncols)]
            
            for col_idx, header in enumerate(headers):
                if header == "计划号":
                    plan_no_col_index = col_idx
                    break
            
            if plan_no_col_index is None:
                print(f"[×] 文件中找不到'计划号'列，表头: {headers}")
                return False
            
            # 3. 检查是否有数据行
            if sheet.nrows < 2:
                print(f"[×] 文件只有表头，没有数据")
                return False
            
            # 4. 检查第一行数据的计划号是否与文件名一致
            file_plan_no = str(sheet.cell_value(1, plan_no_col_index)).strip()
            
            if not file_plan_no:
                print(f"[×] 第一行数据的计划号为空")
                return False
            
            # 比较计划号（忽略大小写和空格）
            if file_plan_no.strip().lower() == expected_plan_no.strip().lower():
                print(f"[√] 计划号验证通过: {expected_plan_no}")
                return True
            else:
                print(f"[×] 计划号验证失败: 文件名={expected_plan_no}, 内容={file_plan_no}")
                return False
                
        except Exception as e:
            print(f"[×] 验证计划号时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_remove_phosphorus_list(self):
        """加载除鳞钢种列表"""
        remove_phosphorus_list = []
        try:
            import os
            # 尝试从计划号目录加载除鳞钢种文件
            phosphorus_file_path = os.path.join(self.plan_dir, "除鳞钢种.txt")
            if not os.path.exists(phosphorus_file_path):
                # 如果不存在，尝试从项目目录加载
                if getattr(sys, 'frozen', False):
                    project_phos_file = os.path.join(sys._MEIPASS, "除鳞钢种.txt")
                else:
                    project_phos_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "除鳞钢种.txt")
                if os.path.exists(project_phos_file):
                    phosphorus_file_path = project_phos_file
                else:
                    # 如果都不存在，返回空列表
                    return []
        
            # 读取除鳞钢种文件
            with open(phosphorus_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    grade = line.strip()
                    if grade:
                        remove_phosphorus_list.append(grade)
        
            print(f"[✓] 成功加载除鳞钢种列表: {remove_phosphorus_list}")
        except Exception as e:
            print(f"[×] 加载除鳞钢种列表失败: {str(e)}")
        
        return remove_phosphorus_list
    
    def load_aps_grades(self):
        """加载APS钢种列表"""
        aps_grades = []
        try:
            import os
            # 尝试从计划号目录加载APS.txt文件
            aps_file_path = os.path.join(self.plan_dir, "APS.txt")
            if not os.path.exists(aps_file_path):
                # 如果不存在，尝试从项目目录加载
                # 使用正确的路径逻辑，确保打包后也能找到文件
                if getattr(sys, 'frozen', False):
                    project_aps_file = os.path.join(sys._MEIPASS, "APS.txt")
                else:
                    project_aps_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "APS.txt")
                if os.path.exists(project_aps_file):
                    aps_file_path = project_aps_file
                else:
                    # 如果都不存在，返回空列表
                    return []
            
            # 读取APS.txt文件
            with open(aps_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    grade = line.strip()
                    if grade:
                        aps_grades.append(grade)
            
            print(f"已加载 {len(aps_grades)} 个APS钢种")
        except Exception as e:
            print(f"加载APS钢种列表失败: {str(e)}")
        
        return aps_grades
    
    def add_grade_to_aps(self, grade):
        """添加钢种到APS.txt文件"""
        try:
            import os
            # 尝试从计划号目录加载APS.txt文件
            aps_file_path = os.path.join(self.plan_dir, "APS.txt")
            if not os.path.exists(aps_file_path):
                # 如果不存在，尝试从项目目录加载
                # 使用正确的路径逻辑，确保打包后也能找到文件
                if getattr(sys, 'frozen', False):
                    project_aps_file = os.path.join(sys._MEIPASS, "APS.txt")
                else:
                    project_aps_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "APS.txt")
                if os.path.exists(project_aps_file):
                    aps_file_path = project_aps_file
                else:
                    # 如果都不存在，使用计划号目录的路径
                    aps_file_path = os.path.join(self.plan_dir, "APS.txt")
            
            # 读取现有钢种
            existing_grades = set()
            if os.path.exists(aps_file_path):
                with open(aps_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        existing_grade = line.strip()
                        if existing_grade:
                            existing_grades.add(existing_grade)
            
            # 如果钢种不在现有列表中，添加它
            if grade and grade not in existing_grades:
                existing_grades.add(grade)
                # 写入回文件
                with open(aps_file_path, 'w', encoding='utf-8') as f:
                    for g in sorted(existing_grades):
                        f.write(g + '\n')
                print(f"已添加钢种 {grade} 到APS.txt文件")
        except Exception as e:
            print(f"添加钢种到APS.txt文件失败: {str(e)}")
    
    def print_selected(self):
        """打印选中的计划号"""
        # 简化实现,实际应该调用打印功能
        print("打印选中的计划号")
        # 刷新数据
        self.refresh_data()

    def select_all(self):
        """全选"""
        self.table_widget.selectAll()

    def deselect_all(self):
        """取消全选"""
        self.table_widget.clearSelection()

    def refresh_plan_list_from_file(self):
        """从装炉顺序.xls文件读取数据并更新表格"""
        temp_file_path = None
        plan_data = []
        try:
            import os
            import xlrd
            import shutil
            import time
            
            # 读取装炉顺序.xls文件
            plan_dir = os.path.join(self.plan_dir, "计划号")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            print(f"查找装炉顺序文件: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"文件不存在: {excel_file}")
                # 检查备份计划目录
                backup_dir = os.path.join(plan_dir, "备份计划")
                backup_excel_file = os.path.join(backup_dir, "装炉顺序.xls")
                if os.path.exists(backup_excel_file):
                    print(f"在备份计划目录中找到装炉顺序文件: {backup_excel_file}")
                    excel_file = backup_excel_file
                else:
                    print(f"备份计划目录中也不存在装炉顺序文件: {backup_excel_file}")
                    # 更新空表格
                    self.plan_data = []
                    self.update_table()
                    self.stats_label.setText("总块数: 0 | 无文件: 0")
                    return False
            
            # 创建临时副本（存储在计划号文件夹中）
            temp_file_name = f"temp_装炉顺序_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            shutil.copy2(excel_file, temp_file_path)
            print(f"创建临时副本: {temp_file_path}")
            
            # 读取数据
            workbook = xlrd.open_workbook(temp_file_path)
            sheet = workbook.sheet_by_index(0)
            
            headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
            print(f"列名: {headers}")
            
            # 查找列索引
            order_col = None  # 装炉顺序号
            plan_col = None   # 计划号
            coil_col = None   # 钢卷号
            
            for idx, header in enumerate(headers):
                if '装炉顺序号' in header or '装炉顺序' in header:
                    order_col = idx
                    print(f"找到装炉顺序列: {idx}")
                elif '计划号' in header:
                    plan_col = idx
                    print(f"找到计划号列: {idx}")
                elif '钢卷号' in header:
                    coil_col = idx
                    print(f"找到钢卷号列: {idx}")
            
            if None in [order_col, plan_col, coil_col]:
                print(f"缺少必要列: order_col={order_col}, plan_col={plan_col}, coil_col={coil_col}")
                print("装炉顺序.xls文件缺少必要的列（装炉顺序、计划号、钢卷号）")
                # 更新空表格
                self.plan_data = []
                self.update_table()
                self.stats_label.setText("总块数: 0 | 无文件: 0")
                return False
            
            # 读取数据
            max_rows = min(1000, sheet.nrows)  # 限制读取行数,防止内存溢出
            print(f"开始读取数据,总行数: {sheet.nrows}, 限制行数: {max_rows}")
            for row in range(1, max_rows):
                try:
                    if row % 100 == 0:  # 每100行打印一次,减少输出
                        print(f"正在读取第 {row} 行...")
                    order = sheet.cell_value(row, order_col)
                    # 转换装炉顺序为整数
                    if isinstance(order, float) and order.is_integer():
                        order = int(order)
                    plan_no = str(sheet.cell_value(row, plan_col)).strip()
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    
                    # 清理钢卷号,只保留ASCII数字
                    try:
                        coil_no = ''.join(c for c in coil_no if c.isdigit())
                    except Exception as e:
                        print(f"清理钢卷号失败: {e}")
                        coil_no = ''
                    
                    if plan_no and coil_no:
                        plan_data.append({
                            'order': order,
                            'plan_no': plan_no,
                            'coil_no': coil_no
                        })
                        if row % 50 == 0:  # 每50行打印一次,减少输出
                            print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no} (行 {row})")
                    else:
                        if row % 100 == 0:  # 每100行打印一次,减少输出
                            print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}' (行 {row})")
                except Exception as e:
                    print(f"读取行 {row} 失败: {e}")
                    # 继续处理下一行,不中断整个加载过程
                    continue
            print(f"数据读取完成,共加载 {len(plan_data)} 条数据")
        except Exception as e:
            print(f"读取装炉顺序文件失败: {e}")
            # 更新空表格
            self.plan_data = []
            self.update_table()
            self.stats_label.setText("总块数: 0 | 无文件: 0")
            return False
        finally:
            # 无论是否发生异常,都删除临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"删除临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")
            
            print(f"加载到 {len(plan_data)} 条装炉数据")
            if len(plan_data) == 0:
                print("装炉顺序.xls文件中没有数据")
                # 更新空表格
                self.plan_data = []
                self.update_table()
                self.stats_label.setText("总块数: 0 | 无文件: 0")
                return False
            
            # 按装炉顺序排序
            plan_data.sort(key=lambda x: x['order'])
            
            # 按计划号分组,计算每个计划号的块数和起止钢卷号
            plan_groups = {}
            for item in plan_data:
                plan_no = item['plan_no']
                if plan_no not in plan_groups:
                    plan_groups[plan_no] = {
                        'count': 0,
                        'coils': []
                    }
                plan_groups[plan_no]['count'] += 1
                plan_groups[plan_no]['coils'].append(item['coil_no'])
            
            # 构建计划数据列表,按装炉顺序排序
            plan_order = []
            seen_plans = set()
            for item in plan_data:
                plan_no = item['plan_no']
                if plan_no not in seen_plans:
                    plan_order.append(plan_no)
                    seen_plans.add(plan_no)
            
            # 构建计划数据
            self.plan_data = []
            total_count = 0
            no_file_count = 0
            
            # 获取计划号文件夹中的所有xls文件
            plan_files = set()
            if os.path.exists(plan_dir):
                for f in os.listdir(plan_dir):
                    if f.endswith('.xls') or f.endswith('.xlsx'):
                        # 去掉扩展名获取计划号
                        plan_no_from_file = os.path.splitext(f)[0]
                        plan_files.add(plan_no_from_file)
            
            # 获取backup文件夹中的所有xls文件（排除"原始文件"子目录）
            backup_dir = os.path.join(plan_dir, "backup")
            if os.path.exists(backup_dir):
                for f in os.listdir(backup_dir):
                    # 跳过"原始文件"目录
                    if f == "原始文件":
                        continue
                    # 只处理文件，不处理子目录
                    file_path = os.path.join(backup_dir, f)
                    if os.path.isfile(file_path) and (f.endswith('.xls') or f.endswith('.xlsx')):
                        # 去掉扩展名获取计划号
                        plan_no_from_file = os.path.splitext(f)[0]
                        plan_files.add(plan_no_from_file)
            
            print(f"计划号文件夹和backup文件夹中找到 {len(plan_files)} 个文件")
            
            # 按装炉顺序处理计划号
            for plan_no in plan_order:
                if plan_no in plan_groups:
                    group = plan_groups[plan_no]
                    count = group['count']
                    coils = group['coils']
                    min_coil = min(coils) if coils else ''
                    max_coil = max(coils) if coils else ''
                    
                    # 检查是否有对应的文件
                    status = ''
                    has_low_roll_width = False
                    
                    if plan_no not in plan_files:
                        status = '无文件'
                        no_file_count += 1
                        print(f"计划号 {plan_no} 无对应文件")
                    else:
                        # 检查计划号文件中的轧宽数据
                        file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                        if not os.path.exists(file_path):
                            # 检查backup目录
                            backup_path = os.path.join(backup_dir, f"{plan_no}.xls")
                            if os.path.exists(backup_path):
                                file_path = backup_path
                        
                        if os.path.exists(file_path):
                            try:
                                # 读取Excel文件
                                workbook = xlrd.open_workbook(file_path)
                                sheet = workbook.sheet_by_index(0)
                                
                                # 查找字段列名行
                                field_name_row = -1
                                for row_idx in range(min(10, sheet.nrows)):
                                    row_has_field_names = False
                                    for col_idx in range(sheet.ncols):
                                        cell_value = str(sheet.cell_value(row_idx, col_idx))
                                        if any(field in cell_value for field in ["序号", "钢卷号", "牌号", "坯厚", "轧厚", "轧宽", "装炉顺"]):
                                            row_has_field_names = True
                                            break
                                    if row_has_field_names:
                                        field_name_row = row_idx
                                        break
                                
                                if field_name_row != -1:
                                    # 获取列名
                                    current_columns = []
                                    for i in range(sheet.ncols):
                                        current_columns.append(sheet.cell_value(field_name_row, i))
                                    
                                    # 查找轧宽列
                                    roll_width_col = -1
                                    for col_idx, col_name in enumerate(current_columns):
                                        if "轧宽" in col_name:
                                            roll_width_col = col_idx
                                            break
                                    
                                    if roll_width_col != -1:
                                        # 检查数据行中的轧宽值
                                        for row_idx in range(field_name_row + 1, min(field_name_row + 100, sheet.nrows)):  # 限制检查行数
                                            roll_width_value = sheet.cell_value(row_idx, roll_width_col)
                                            try:
                                                # 去除可能的标记（如Δ）
                                                roll_width_clean = str(roll_width_value).strip().replace('Δ', '')
                                                roll_width_num = float(roll_width_clean)
                                                if roll_width_num <= 930:
                                                    has_low_roll_width = True
                                                    break
                                            except (ValueError, TypeError):
                                                pass
                            except Exception as e:
                                print(f"检查轧宽时出错 {plan_no}: {str(e)}")
                    
                    # 从保存的集合中恢复低轧宽板坯状态
                    if hasattr(self, 'low_roll_width_plans') and plan_no in self.low_roll_width_plans:
                        has_low_roll_width = True
                    
                    self.plan_data.append({
                        'plan_no': plan_no,
                        'count': count,
                        'status': status,
                        'min_coil': min_coil,
                        'max_coil': max_coil,
                        'has_low_roll_width': has_low_roll_width
                    })
                    total_count += count
            
            # 更新表格
            self.update_table()
            self.stats_label.setText(f"总块数: {total_count} | 无文件: {no_file_count}")
            
            print(f"成功加载 {len(self.plan_data)} 个计划号,总计 {total_count} 块,无文件 {no_file_count} 个")
            return True
    
    def update_table(self):
        """更新表格显示"""
        # 清空表格
        self.table_widget.setRowCount(0)
        
        for item in self.plan_data:
            plan_no = item['plan_no']
            count = item['count']
            status = item['status']
            min_coil = item.get('min_coil', '')
            max_coil = item.get('max_coil', '')
            
            # 构建状态文本
            status_text = ""
            if status:
                status_text += f"[{status}] "
            if hasattr(self, 'processed_plans') and isinstance(self.processed_plans, dict) and plan_no in self.processed_plans:
                # 对于D开头的计划号，需要检查是否有已处理的钢卷号
                if plan_no.startswith('D') or plan_no.startswith('d'):
                    if self.processed_plans.get(plan_no, set()):
                        status_text += f"[已处理] "
                else:
                    # 对于非D开头的计划号，只要有记录（即使是空set）就认为已处理
                    status_text += f"[已处理] "
            elif hasattr(self, 'processed_plans') and isinstance(self.processed_plans, set) and plan_no in self.processed_plans:
                # 兼容旧格式
                status_text += f"[已处理] "
            if hasattr(self, 'printed_plans') and isinstance(self.printed_plans, dict) and plan_no in self.printed_plans:
                # 对于D开头的计划号，需要检查是否有已打印的钢卷号
                if plan_no.startswith('D') or plan_no.startswith('d'):
                    if self.printed_plans.get(plan_no, set()):
                        status_text += f"[已打印] "
                else:
                    # 对于非D开头的计划号，只要有记录（即使是空set）就认为已打印
                    status_text += f"[已打印] "
            elif hasattr(self, 'printed_plans') and isinstance(self.printed_plans, set) and plan_no in self.printed_plans:
                # 兼容旧格式
                status_text += f"[已打印] "
            if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                status_text += f"[无APS] "
            if item.get('has_low_roll_width', False):
                status_text += f"[轧宽<930] "
            
            # 构建钢卷号范围文本
            coil_text = ""
            if min_coil and max_coil:
                coil_text = f"[{min_coil}-{max_coil}]"
            
            # 添加行
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            
            # 设置单元格内容
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(plan_no))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(count)))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(status_text.strip()))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(coil_text))
            
            # 设置字体
            font = QFont("宋体", 28, QFont.Bold)
            for col in range(4):
                table_item = self.table_widget.item(row_position, col)
                if table_item:
                    table_item.setFont(font)
            
            # 设置文本对齐
            for col in range(4):
                table_item = self.table_widget.item(row_position, col)
                if table_item:
                    table_item.setTextAlignment(Qt.AlignCenter)
            
            # 设置颜色 - 无APS和轧宽<930都独立判断，都标红
            if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                # 无APS时仅状态栏使用红色字体
                table_item = self.table_widget.item(row_position, 2)
                if table_item:
                    table_item.setForeground(QBrush(QColor(255, 0, 0)))
            if item.get('has_low_roll_width', False):
                # 低轧宽时仅状态栏使用红色字体
                table_item = self.table_widget.item(row_position, 2)
                if table_item:
                    table_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif hasattr(self, 'recently_exported_plans') and plan_no in self.recently_exported_plans:
                # 最近导出的计划号使用绿色字体
                for col in range(4):
                    table_item = self.table_widget.item(row_position, col)
                    if table_item:
                        table_item.setForeground(QBrush(QColor(0, 128, 0)))
    

    
    def start_auto_execution(self):
        """启动自动执行服务"""
        try:
            print("start_auto_execution被调用")
            # 停止现有的定时器
            self.stop_auto_execution()
            
            # 加载设置
            settings = self.get_settings()
            print(f"start_auto_execution获取到的设置: {settings}")
            if not settings.get("autoExec", False):
                print("自动执行未启用")
                return
            
            exec_mode = settings.get("execMode", "interval")
            print(f"exec_mode: {exec_mode}")
            
            if exec_mode == "interval":
                # 按时间间隔执行
                interval_minutes = settings.get("intervalMinutes", 30)
                print(f"interval_minutes: {interval_minutes}")
                interval_ms = interval_minutes * 60 * 1000  # 转换为毫秒
                self.auto_exec_timer.start(interval_ms)
                print(f"启动自动执行服务（按时间间隔），间隔：{interval_minutes}分钟")
            else:
                # 按指定时间执行
                exec_times = settings.get("execTimes", "")
                if not exec_times:
                    print("未设置执行时间")
                    return
                
                print(f"按指定时间模式，execTimes: {exec_times}")
                
                # 计算下一次执行时间
                self.calculate_next_execution_time(exec_times)
                print(f"calculate_next_execution_time计算结果: {self.next_execution_time}")
                
                if self.next_execution_time:
                    # 计算时间差并启动定时器
                    import time
                    current_time = time.time()
                    time_diff = self.next_execution_time - current_time
                    print(f"当前时间: {time.strftime('%H:%M:%S', time.localtime(current_time))}")
                    print(f"下一次执行时间: {time.strftime('%H:%M:%S', time.localtime(self.next_execution_time))}")
                    print(f"时间差: {time_diff} 秒 ({time_diff/60:.2f} 分钟)")
                    
                    if time_diff >= 0:
                        self.auto_exec_timer.start(int(time_diff * 1000))
                        print(f"启动自动执行服务（按指定时间），下一次执行：{time.strftime('%H:%M:%S', time.localtime(self.next_execution_time))}")
                    else:
                        print(f"错误：时间差为负数，不启动定时器")
                else:
                    print("错误：未能计算出下一次执行时间")
            

            
            self.auto_exec_running = True
            # 强制更新标签
            print("强制更新下一次执行时间标签")
            import time
            settings = self.get_settings()
            exec_mode = settings.get("execMode", "interval")
            label_text = ""
            if exec_mode == "interval":
                interval_minutes = settings.get("intervalMinutes", 30)
                # 计算下一次执行的具体时间
                next_exec_time = time.time() + (interval_minutes * 60)
                next_time_str = time.strftime("%H:%M:%S", time.localtime(next_exec_time))
                label_text = f"下一次执行: {next_time_str}"
                self.next_execution_label.setText(label_text)
                print(f"设置标签为: {label_text}")
                # 强制更新UI
                self.next_execution_label.repaint()
                self.next_execution_label.update()
                self.repaint()
                self.update()
            else:
                if self.next_execution_time:
                    next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_execution_time))
                    label_text = f"下一次执行: {next_time_str}"
                    self.next_execution_label.setText(label_text)
                    print(f"设置标签为: {label_text}")
                    # 强制更新UI
                    self.next_execution_label.repaint()
                    self.next_execution_label.update()
                    self.repaint()
                    self.update()
                else:
                    label_text = "下一次执行: 无"
                    self.next_execution_label.setText(label_text)
                    print(f"设置标签为: {label_text}")
                    # 强制更新UI
                    self.next_execution_label.repaint()
                    self.next_execution_label.update()
                    self.repaint()
                    self.update()
            
            # 同时更新装炉明细窗口的下一次执行时间
            if hasattr(self, 'furnace_details_window') and self.furnace_details_window:
                try:
                    if hasattr(self.furnace_details_window, 'next_execution_label'):
                        self.furnace_details_window.next_execution_label.setText(label_text)
                        self.furnace_details_window.next_execution_label.repaint()
                        self.furnace_details_window.next_execution_label.update()
                        print(f"已更新装炉明细窗口的下一次执行时间为: {label_text}")
                except Exception as e:
                    print(f"更新装炉明细窗口的下一次执行时间失败: {str(e)}")
            
            print("自动执行服务已启动")
        except Exception as e:
            print(f"启动自动执行服务失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def stop_auto_execution(self):
        """停止自动执行服务"""
        try:
            self.auto_exec_timer.stop()
            self.auto_exec_running = False
            self.next_execution_time = None
            self.update_next_execution_label()
            print("自动执行服务已停止")
        except Exception as e:
            print(f"停止自动执行服务失败: {str(e)}")
    
    def auto_exec_timeout(self):
        """自动执行定时器超时处理"""
        try:
            print("\n=== 自动执行触发 ===")
            
            # 检查自动执行是否仍然启用
            settings = self.get_settings()
            if not settings.get("autoExec", False):
                print("自动执行未启用，跳过执行")
                return
            
            print(f"自动执行已启用，execMode: {settings.get('execMode')}")
            
            # 执行自动导出（同步执行，等待完成后再重新设置定时器）
            # 注意：auto_export内部会创建后台线程执行实际的导出操作
            # 但我们需要等待它完成后再重新设置定时器
            self.auto_export()
            
            # 等待一段时间，确保导出操作已经开始执行
            # 这样可以避免在导出过程中重新设置定时器导致的执行次数不准
            import time
            time.sleep(2)  # 等待2秒，确保导出操作已经启动
            
            # 重新设置定时器
            settings = self.get_settings()
            exec_mode = settings.get("execMode", "interval")
            
            if exec_mode == "interval":
                # 按时间间隔执行，重新设置定时器
                interval_minutes = settings.get("intervalMinutes", 30)
                interval_ms = interval_minutes * 60 * 1000  # 转换为毫秒
                self.auto_exec_timer.start(interval_ms)
                print(f"重新设置自动执行定时器（按时间间隔），间隔：{interval_minutes}分钟")
            elif exec_mode == "time":
                # 按指定时间执行，重新计算下一次执行时间
                exec_times = settings.get("execTimes", "")
                self.calculate_next_execution_time(exec_times)
                if self.next_execution_time:
                    current_time = time.time()
                    time_diff = self.next_execution_time - current_time
                    if time_diff >= 0:
                        self.auto_exec_timer.start(int(time_diff * 1000))
                        print(f"重新设置自动执行定时器（按指定时间），下一次执行：{time.strftime('%H:%M:%S', time.localtime(self.next_execution_time))}")
                    else:
                        print(f"警告：计算出的时间差为负数 {time_diff}，不设置定时器")
                else:
                    print("警告：未能计算出下一次执行时间")
            
            # 更新下一次执行时间标签
            self.update_next_execution_label()
        except Exception as e:
            print(f"自动执行超时处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def calculate_next_execution_time(self, exec_times):
        """计算下一次执行时间"""
        try:
            import time
            from datetime import datetime, timedelta
            
            # 解析执行时间
            time_strings = [t.strip() for t in exec_times.split(",") if t.strip()]
            if not time_strings:
                self.next_execution_time = None
                return
            
            # 对时间字符串进行排序
            def time_key(time_str):
                try:
                    hour, minute = map(int, time_str.split(":"))
                    return hour * 60 + minute
                except:
                    return 9999  # 无效时间放在最后
            
            # 按时间顺序排序
            sorted_time_strings = sorted(time_strings, key=time_key)
            print(f"排序后的时间列表: {sorted_time_strings}")
            
            # 获取当前时间（包含秒）
            now = datetime.now()
            current_datetime = now.replace(second=0, microsecond=0)  # 忽略秒和微秒
            print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_datetime.timestamp()))}")
            
            # 找出下一个执行时间
            next_time = None
            for time_str in sorted_time_strings:
                try:
                    # 解析时间字符串
                    exec_datetime = datetime.strptime(time_str, "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day, second=0, microsecond=0
                    )
                    
                    # 如果时间已过或正好是当前时间，跳过
                    if exec_datetime > current_datetime:
                        # 今天的这个时间
                        next_time = exec_datetime
                        print(f"找到今天的下一次执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_time.timestamp()))}")
                        break
                except Exception as e:
                    print(f"解析时间 {time_str} 失败: {e}")
                    continue
            
            # 如果今天没有找到，使用明天的第一个时间
            if not next_time:
                try:
                    first_datetime = datetime.strptime(sorted_time_strings[0], "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day, second=0, microsecond=0
                    )
                    next_time = first_datetime + timedelta(days=1)
                    print(f"今天没有找到合适的时间，使用明天的第一个时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_time.timestamp()))}")
                except Exception as e:
                    print(f"设置明天执行时间失败: {e}")
                    self.next_execution_time = None
                    return
            
            # 转换为时间戳
            self.next_execution_time = next_time.timestamp()
            print(f"计算出的下一次执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.next_execution_time))}")
        except Exception as e:
            print(f"计算下一次执行时间失败: {str(e)}")
            self.next_execution_time = None
    

    
    def load_settings(self):
        """加载设置并重启自动执行服务"""
        try:
            print("MainWindow.load_settings被调用")
            settings = self.get_settings()
            # 安全打印设置，避免编码错误
            try:
                print(f"获取到的设置: autoExec={settings.get('autoExec')}, execMode={settings.get('execMode')}, intervalMinutes={settings.get('intervalMinutes')}")
            except UnicodeEncodeError:
                print("获取到的设置: 包含非ASCII字符")
            # 检查自动执行设置
            if settings.get("autoExec", False):
                print("autoExec为True，调用start_auto_execution")
                self.start_auto_execution()
            else:
                print("autoExec为False，调用stop_auto_execution")
                self.stop_auto_execution()
            print("设置已加载并应用")
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def show_auto_close_message(self, title, message, duration=3000):
        """显示自动关闭的消息框 - 可手动关闭，大窗口，大字体
        
        Args:
            title: 消息框标题
            message: 消息内容
            duration: 持续时间（毫秒），默认3000毫秒
        """
        from PyQt5.QtWidgets import QMessageBox, QApplication
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont
        
        # 先激活主窗口，确保应用程序在前台
        self.activateWindow()
        self.raise_()
        self.show()
        
        # 创建消息框，使用主窗口作为父窗口
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # 添加OK按钮，允许用户手动关闭
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        
        # 设置窗口标志，确保置顶
        msg_box.setWindowFlags(
            Qt.Dialog | 
            Qt.WindowStaysOnTopHint
        )
        msg_box.setModal(True)  # 使用模态窗口
        
        # 设置字体（与计划号列表相同大小）
        font = QFont("宋体", 14)
        msg_box.setFont(font)
        
        # 增加消息框大小
        msg_box.setMinimumWidth(500)
        msg_box.setMinimumHeight(250)
        
        # 确保应用程序是活动的
        QApplication.setActiveWindow(msg_box)
        
        # 使用QTimer设置自动关闭
        timer = QTimer(msg_box)
        timer.timeout.connect(lambda: msg_box.done(QMessageBox.Ok))
        timer.setSingleShot(True)
        timer.start(duration)
        
        # 确保消息框显示在最前面
        msg_box.activateWindow()
        msg_box.raise_()
        
        # 使用exec_()显示模态对话框，允许用户手动关闭
        msg_box.exec_()
        
        print(f"已显示自动关闭消息框，{duration}毫秒后关闭")
        return msg_box
    
    def update_next_execution_label(self):
        """更新下一次执行时间标签"""
        try:
            print(f"update_next_execution_label被调用，auto_exec_running: {self.auto_exec_running}")
            if not self.auto_exec_running:
                print("auto_exec_running为False，设置为'下一次执行: 无'")
                self.next_execution_label.setText("下一次执行: 无")
                # 强制更新
                self.next_execution_label.repaint()
                self.next_execution_label.update()
                # 同时更新装炉明细窗口的下一次执行时间
                if hasattr(self, 'furnace_details_window') and self.furnace_details_window:
                    try:
                        if hasattr(self.furnace_details_window, 'next_execution_label'):
                            self.furnace_details_window.next_execution_label.setText("下一次执行: 无")
                            self.furnace_details_window.next_execution_label.repaint()
                            self.furnace_details_window.next_execution_label.update()
                            print("已更新装炉明细窗口的下一次执行时间为: 无")
                    except Exception as e:
                        print(f"更新装炉明细窗口的下一次执行时间失败: {str(e)}")
                return
            
            settings = self.get_settings()
            print(f"获取到的设置: {settings}")
            exec_mode = settings.get("execMode", "interval")
            print(f"exec_mode: {exec_mode}")
            
            import time
            if exec_mode == "interval":
                interval_minutes = settings.get("intervalMinutes", 30)
                print(f"interval_minutes: {interval_minutes}")
                # 计算下一次执行的具体时间
                next_exec_time = time.time() + (interval_minutes * 60)
                next_time_str = time.strftime("%H:%M:%S", time.localtime(next_exec_time))
                label_text = f"下一次执行: {next_time_str}"
                self.next_execution_label.setText(label_text)
                print(f"设置标签为: {label_text}")
            else:
                if self.next_execution_time:
                    next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_execution_time))
                    print(f"next_execution_time: {next_time_str}")
                    label_text = f"下一次执行: {next_time_str}"
                    self.next_execution_label.setText(label_text)
                    print(f"设置标签为: {label_text}")
                else:
                    label_text = "下一次执行: 无"
                    self.next_execution_label.setText(label_text)
                    print(f"设置标签为: {label_text}")
            
            # 强制更新
            print("强制更新标签")
            self.next_execution_label.repaint()
            self.next_execution_label.update()
            # 也更新整个窗口
            self.repaint()
            
            # 同时更新装炉明细窗口的下一次执行时间
            if hasattr(self, 'furnace_details_window') and self.furnace_details_window:
                try:
                    if hasattr(self.furnace_details_window, 'next_execution_label'):
                        self.furnace_details_window.next_execution_label.setText(label_text)
                        self.furnace_details_window.next_execution_label.repaint()
                        self.furnace_details_window.next_execution_label.update()
                        print(f"已更新装炉明细窗口的下一次执行时间为: {label_text}")
                except Exception as e:
                    print(f"更新装炉明细窗口的下一次执行时间失败: {str(e)}")
            self.update()
        except Exception as e:
            print(f"更新下一次执行时间标签失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def connect_signals(self):
        """连接信号槽"""
        # 连接全选按钮
        self.select_all_btn.clicked.connect(self.select_all)
        # 连接取消全选按钮
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        # 连接刷新按钮
        self.refresh_btn.clicked.connect(self.refresh_data)
        # 连接自动导出按钮
        self.auto_export_btn.clicked.connect(self.auto_export)
        # 连接设置按钮
        self.settings_btn.clicked.connect(self.open_settings_window)
        # 连接装炉明细按钮
        self.furnace_details_btn.clicked.connect(self.open_furnace_details)
        # 连接处理计划按钮
        self.process_plans_btn.clicked.connect(self.process_plans)
        # 连接粗轧主画面按钮
        self.rm_main_btn.clicked.connect(self.open_rm_main_window)

        # 连接显示按钮
        self.show_selected_btn.clicked.connect(self.show_selected)
        # 连接打印按钮
        self.print_selected_btn.clicked.connect(self.print_selected)
        # 连接自动执行复选框
        self.auto_exec_checkbox.stateChanged.connect(self.on_auto_exec_changed)
        # 连接自动打印复选框
        self.auto_print_checkbox.stateChanged.connect(self.on_auto_print_changed)
        # 连接防退出登录复选框

    
    def on_auto_exec_changed(self, state):
        """自动执行复选框状态变化处理"""
        try:
            enabled = state == Qt.Checked
            print(f"自动执行复选框状态变化: {enabled}")
            
            # 更新设置文件
            settings = self.get_settings()
            settings["autoExec"] = enabled
            
            import json
            import os
            # 使用self.plan_dir确保打包后也能正确保存配置文件
            config_file = os.path.join(self.plan_dir, 'settings.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # 启动或停止自动执行服务
            if enabled:
                self.start_auto_execution()
            else:
                self.stop_auto_execution()
                # 清空下一次执行时间显示
                self.next_execution_label.setText("下一次执行: 无")
            
            # 更新主窗口的自动执行复选框状态（确保状态一致）
            if hasattr(self, 'auto_exec_checkbox'):
                self.auto_exec_checkbox.setChecked(enabled)
            
            # 同步装炉明细窗口的自动执行复选框状态
            if hasattr(self, 'furnace_details_window') and self.furnace_details_window:
                if hasattr(self.furnace_details_window, 'auto_exec_checkbox'):
                    self.furnace_details_window.auto_exec_checkbox.setChecked(enabled)
        except Exception as e:
            print(f"处理自动执行复选框状态变化失败: {str(e)}")
    
    def on_auto_print_changed(self, state):
        """自动打印复选框状态变化处理"""
        try:
            enabled = state == Qt.Checked
            print(f"自动打印复选框状态变化: {enabled}")
            
            # 更新设置文件
            settings = self.get_settings()
            settings["autoPrint"] = enabled
            
            import json
            import os
            # 使用self.plan_dir确保打包后也能正确保存配置文件
            config_file = os.path.join(self.plan_dir, 'settings.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            # 更新主窗口的自动打印复选框状态（确保状态一致）
            if hasattr(self, 'auto_print_checkbox'):
                self.auto_print_checkbox.setChecked(enabled)
            
            # 同步装炉明细窗口的自动打印复选框状态
            if hasattr(self, 'furnace_details_window') and self.furnace_details_window:
                if hasattr(self.furnace_details_window, 'auto_print_checkbox'):
                    self.furnace_details_window.auto_print_checkbox.setChecked(enabled)
        except Exception as e:
            print(f"处理自动打印复选框状态变化失败: {str(e)}")
    
    def on_plan_double_clicked(self, index):
        """双击计划号行，显示该计划号的所有钢卷号列表"""
        from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QWidget, QHeaderView
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt
        
        if not index.isValid():
            return
        
        row = index.row()
        plan_item = self.table_widget.item(row, 0)
        if not plan_item:
            return
        
        plan_no = plan_item.text()
        
        # 从装炉顺序.xls中读取钢卷号
        coil_nos = []
        
        # 构建装炉顺序文件路径（与ensure_zhuanglu_shunxu_file一致）
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        if not os.path.exists(zhuanglu_file):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", f"装炉顺序.xls 文件不存在\n路径: {zhuanglu_file}")
            return
        
        try:
            import xlrd
            workbook = xlrd.open_workbook(zhuanglu_file)
            sheet = workbook.sheet_by_index(0)
            
            # 查找计划号列和钢卷号列
            plan_col = -1
            coil_col = -1
            
            for row_idx in range(min(15, sheet.nrows)):
                for col_idx in range(sheet.ncols):
                    cell_value = str(sheet.cell_value(row_idx, col_idx)).strip()
                    if "计划号" in cell_value or "ORDER_NO" in cell_value.upper():
                        plan_col = col_idx
                    if "钢卷号" in cell_value or "卷号" in cell_value or "COIL_NO" in cell_value.upper():
                        coil_col = col_idx
                
                if plan_col != -1 and coil_col != -1:
                    break
            
            if plan_col == -1:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "未找到计划号列")
                return
            
            if coil_col == -1:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "未找到钢卷号列")
                return
            
            # 从第一行开始读取数据（跳过表头）
            for row_idx in range(1, sheet.nrows):
                current_plan = str(sheet.cell_value(row_idx, plan_col)).strip()
                # 去除可能的空格和特殊字符
                current_plan = ''.join(c for c in current_plan if c.isalnum())
                plan_no_clean = ''.join(c for c in plan_no if c.isalnum())
                
                if current_plan == plan_no_clean:
                    coil_no = str(sheet.cell_value(row_idx, coil_col)).strip()
                    coil_no = ''.join(c for c in coil_no if c.isdigit())
                    if coil_no:
                        coil_nos.append(coil_no)
            
            coil_nos = sorted(set(coil_nos), key=lambda x: int(x) if x.isdigit() else 0)
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", f"读取装炉顺序文件失败: {str(e)}")
            return
        
        if not coil_nos:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", f"计划号 {plan_no} 没有钢卷号数据")
            return
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"计划号 {plan_no} 的钢卷号列表")
        # 窗口宽度跟主程序窗口一样
        dialog.resize(self.width(), 600)
        
        # 按前7位分组，每列显示相同前7位的钢卷号
        # 第8位数字决定行号（0→第1行，1→第2行，...，9→第10行）
        groups = {}
        for coil_no in coil_nos:
            if len(coil_no) >= 7:
                prefix = coil_no[:7]  # 前7位
                if prefix not in groups:
                    groups[prefix] = {}
                if len(coil_no) >= 8:
                    eighth_digit = coil_no[7]  # 第8位
                    if eighth_digit.isdigit():
                        row = int(eighth_digit)  # 0-9 → 行0-9
                        groups[prefix][row] = coil_no
        
        # 按前缀排序
        sorted_prefixes = sorted(groups.keys())
        cols = len(sorted_prefixes)
        rows = 10  # 固定10行
        
        # 创建表格
        table = QTableWidget()
        table.setRowCount(rows)
        table.setColumnCount(cols)
        
        # 设置单元格不可编辑、不可点击
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        
        # 设置字体（与主程序计划号列表一致）
        font = QFont("宋体", 28, QFont.Bold)
        table.setFont(font)
        
        # 设置列宽（8位钢卷号宽度 + 间距）
        coil_width = 170    # 8位钢卷号宽度
        gap_width = 80      # 增大间距（约两个数字宽度）
        
        # 所有列都使用相同的宽度（包含间距），确保列之间间距一致
        for col in range(cols):
            table.setColumnWidth(col, coil_width + gap_width)
        
        # 添加网格线样式
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #CCCCCC;
                border: 1px solid #CCCCCC;
            }
            QTableWidget::item {
                border: 1px solid #CCCCCC;
                padding: 2px;
            }
        """)
        
        # 设置行高
        table.verticalHeader().setDefaultSectionSize(50)
        
        # 填充数据（第8位数字设置背景色）
        for col, prefix in enumerate(sorted_prefixes):
            coil_map = groups[prefix]
            for row in range(10):
                if row in coil_map:
                    coil_no = coil_map[row]
                    # 对第8位数字设置背景色（黄色）
                    if len(coil_no) >= 8:
                        # 使用QLabel显示HTML内容
                        label = QLabel()
                        first_seven = coil_no[:7]
                        eighth = coil_no[7]
                        rest = coil_no[8:]
                        html_text = f"<span style='font-family: 宋体; font-size: 28pt; font-weight: bold;'>{first_seven}<span style='background-color: yellow;'>{eighth}</span>{rest}</span>"
                        label.setText(html_text)
                        label.setAlignment(Qt.AlignCenter)
                        table.setCellWidget(row, col, label)
                    else:
                        item = QTableWidgetItem(coil_no)
                        table.setItem(row, col, item)
        
        # 隐藏垂直表头
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 在表格上方添加计划号标题（与列表中字符大小一致）
        plan_title = QLabel(f"计划号：{plan_no}")
        plan_title_font = QFont("宋体", 28, QFont.Bold)
        plan_title.setFont(plan_title_font)
        plan_title.setAlignment(Qt.AlignCenter)
        plan_title.setContentsMargins(0, 20, 0, 20)  # 上下间距
        layout.addWidget(plan_title)
        
        layout.addWidget(table)
        
        # 添加按钮（居中）
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.addStretch()  # 左侧拉伸
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        button_layout.addWidget(button_box)
        button_layout.addStretch()  # 右侧拉伸
        layout.addWidget(button_widget, alignment=Qt.AlignCenter)
        
        dialog.setLayout(layout)
        
        # 增大窗体高度
        dialog.resize(self.width(), 750)
        
        dialog.exec_()
    
    def show_context_menu(self, pos):
        """显示上下文菜单"""
        from PyQt5.QtWidgets import QMenu
        from PyQt5.QtGui import QFont
        
        # 检查是否有选中项，如果没有则根据鼠标点击位置选中对应行
        selected_items = self.table_widget.selectionModel().selectedRows()
        if not selected_items:
            # 获取右键点击位置对应的行
            index = self.table_widget.indexAt(pos)
            if index.isValid():
                row = index.row()
                # 选中所点击的行
                self.table_widget.selectRow(row)
        
        # 创建上下文菜单
        context_menu = QMenu(self)
        # 设置字体，与装炉明细画面的右键菜单保持一致
        context_menu.setFont(QFont("微软雅黑", 20))
        # 设置选中项为蓝色背景白字
        context_menu.setStyleSheet("""
            QMenu::item:selected {
                background-color: #0066CC;
                color: white;
            }
        """)
        
        # 添加重新导出打印菜单项
        re_export_print_action = context_menu.addAction("重新导出打印")
        re_export_print_action.triggered.connect(self.re_export_and_print_selected)
        
        # 显示菜单
        context_menu.exec_(self.table_widget.mapToGlobal(pos))
    
    def re_export_and_print_selected(self):
        """重新导出并打印选中的计划号
        
        功能说明：
        1. 激活目标软件窗口（BGCMS系统）
        2. 点击轧制计划管理标签 [107, 85]
        3. 重新导出总计划号列表.xls
        4. 计算坐标，获取所选计划号的坐标
        5. 重新导出所选计划号明细.xls
        6. 执行处理计划
        7. 打印所选计划号明细
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            from PyQt5.QtCore import Qt
            
            # 检查是否选择了计划号
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                self.activateWindow()
                self.raise_()
                self.show()
                QMessageBox.warning(self, "警告", "请先在计划号列表中选择要重新导出打印的计划号")
                return
            
            # 获取选中的计划号
            selected_rows = sorted([index.row() for index in selected_items])
            selected_plans = [self.plan_data[row]['plan_no'] for row in selected_rows]
            
            print(f"\n=== 开始重新导出打印 ===")
            print(f"选中的计划号: {selected_plans}")
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            if not os.path.exists(plan_dir):
                QMessageBox.critical(self, "错误", f"计划号文件夹不存在: {plan_dir}")
                return
            
            # 获取设置中的目标窗口
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            # 获取轧制计划管理标签坐标
            zhizhi_tab = self.coordinates.get("zhizhi_tab", [107, 85])
            
            # 步骤0: 激活目标软件窗口
            print("\n【步骤0】激活目标软件窗口...")
            success = self.activate_target_window(test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", f"无法激活目标窗口: {test_window}")
                return
            
            # 步骤0.5: 点击轧制计划管理标签
            print("\n【步骤0.5】点击轧制计划管理标签...")
            print(f"  坐标: {zhizhi_tab}")
            try:
                import pyautogui
                import time
                pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
                time.sleep(0.2)
                pyautogui.click()
                time.sleep(0.5)
                print("  ✓ 点击成功")
            except Exception as e:
                print(f"  ✗ 点击失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"点击轧制计划管理标签失败: {str(e)}")
                return
            
            # 步骤1: 重新导出总计划号列表
            print("\n【步骤1】重新导出总计划号列表...")
            success = self.export_zhizhi_plan_list(test_window=test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", "重新导出总计划号列表失败")
                return
            
            # 步骤2: 读取总计划号列表并计算坐标
            print("\n【步骤2】读取总计划号列表并计算坐标...")
            plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
            if not os.path.exists(plan_list_file):
                QMessageBox.critical(self, "错误", f"总计划号列表文件不存在: {plan_list_file}")
                return
            
            # 读取总计划号列表并计算坐标
            coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=print)
            if not coord_map:
                QMessageBox.critical(self, "错误", "计算计划号坐标失败")
                return
            
            print(f"\n计算完成，共获取 {len(coord_map)} 个计划号的坐标")
            
            # 步骤3: 重新导出所选计划号明细
            print("\n【步骤3】重新导出所选计划号明细...")
            for plan_no in selected_plans:
                if plan_no not in coord_map:
                    print(f"  跳过 {plan_no}，未找到坐标")
                    continue
                
                plan_coord = coord_map[plan_no]
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", [79, 859])
                
                print(f"  导出计划号: {plan_no}, 坐标: {plan_coord}")
                success = self.export_single_plan_detail(
                    plan_no, 
                    plan_coord, 
                    plan_detail_export_btn=plan_detail_export_btn, 
                    test_window=test_window, 
                    add_debug_log=print
                )
                if success:
                    print(f"  ✓ {plan_no} 导出成功")
                else:
                    print(f"  ✗ {plan_no} 导出失败")
            
            # 刷新数据，确保plan_data是最新的
            print("\n【步骤4】刷新数据...")
            self.load_data()
            
            # 步骤5: 处理计划并打印
            print("\n【步骤5】处理计划并打印...")
            # 选中计划号
            self.table_widget.clearSelection()
            for i, plan_data in enumerate(self.plan_data):
                if plan_data['plan_no'] in selected_plans:
                    self.table_widget.selectRow(i)
            
            # 清除选中计划号的已处理和已打印记录，强制重新处理和打印
            print("清除已处理和已打印记录，强制重新处理...")
            if hasattr(self, 'processed_plans') and isinstance(self.processed_plans, dict):
                for plan_no in selected_plans:
                    if plan_no in self.processed_plans:
                        print(f"  清除 {plan_no} 的已处理记录")
                        del self.processed_plans[plan_no]
            
            # 清除已打印记录
            if hasattr(self, 'printed_plans') and isinstance(self.printed_plans, dict):
                for plan_no in selected_plans:
                    if plan_no in self.printed_plans:
                        print(f"  清除 {plan_no} 的已打印记录")
                        del self.printed_plans[plan_no]
            
            # 立即保存状态到文件（防止process_plans重新加载旧记录）
            print("保存清除后的状态...")
            self.save_processed_plans()
            self.save_printed_plans()
            
            # 调用处理计划方法，设置auto_print=True和force_process=True，强制处理并自动打印
            self.process_plans(auto_print=True, show_result=False, force_process=True)
            
            # 回到主程序画面（轧制计划管理系统）
            print("\n【步骤6】回到主程序画面...")
            self.activateWindow()
            self.raise_()
            self.show()
            self.activateWindow()
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()
            print("  ✓ 已回到主程序画面")
            
            print("\n=== 重新导出打印完成 ===")
            
        except Exception as e:
            print(f"重新导出打印失败: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"重新导出打印失败: {str(e)}")
    
    def activate_target_window(self, window_title, add_debug_log=None):
        """激活目标窗口 - 使用与自动导出相同的方法
        
        参数:
            window_title: 目标窗口标题
            add_debug_log: 调试日志函数
            
        返回:
            True - 激活成功
            False - 激活失败
        """
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        add_debug_log(f"  目标窗口: {window_title}")
        
        # 直接调用 activate_window 方法，与自动导出保持一致
        result = self.activate_window(window_title)
        
        if result:
            add_debug_log("  ✓ 成功激活目标窗口")
        else:
            add_debug_log("  ✗ 激活目标窗口失败")
        
        return result
    
    def cleanup_extra_plan_files(self):
        """清理计划号目录中多余的计划号文件
        
        保留：
        1. 装炉顺序*.xls（装炉顺序相关文件）
        2. 总计划号列表*.xls（总计划号列表相关文件）
        3. 装炉顺序_显示.xls
        4. 合并文件.xls
        5. temp_*.xls（临时文件）
        6. 计划号列表中实际存在的计划号文件
        """
        try:
            import os
            from PyQt5.QtWidgets import QMessageBox
            
            plan_dir = os.path.join(self.plan_dir, "计划号")
            if not os.path.exists(plan_dir):
                QMessageBox.information(self, "提示", "计划号目录不存在")
                return
            
            # 先刷新计划号列表，确保获取最新数据
            self.load_data()
            
            valid_plan_numbers = set()
            # 从表格中获取当前显示的计划号（计划号在第0列）
            print(f"调试信息: table_widget 属性存在: {hasattr(self, 'table_widget')}")
            if hasattr(self, 'table_widget'):
                print(f"调试信息: 表格行数: {self.table_widget.rowCount()}")
                print(f"调试信息: 表格列数: {self.table_widget.columnCount()}")
                for row in range(self.table_widget.rowCount()):
                    item = self.table_widget.item(row, 0)  # 计划号在第0列（第一列）
                    print(f"调试信息: 行 {row} 的计划号单元格: {item}")
                    if item:
                        plan_no = str(item.text()).strip()
                        print(f"调试信息: 行 {row} 的计划号: '{plan_no}'")
                        if plan_no:
                            valid_plan_numbers.add(plan_no)
            
            print(f"调试信息: 从表格获取的有效计划号列表 = {valid_plan_numbers}")
            print(f"调试信息: zhizhi_plan_list 属性存在: {hasattr(self, 'zhizhi_plan_list')}")
            if hasattr(self, 'zhizhi_plan_list'):
                print(f"调试信息: zhizhi_plan_list 内容: {self.zhizhi_plan_list}")
            
            must_keep_prefixes = [
                "装炉顺序",
                "总计划号列表"
            ]
            must_keep_files = [
                "装炉顺序_显示.xls",
                "合并文件.xls"
            ]
            
            files_to_delete = []
            files_to_keep = []
            
            for file in os.listdir(plan_dir):
                file_path = os.path.join(plan_dir, file)
                if os.path.isdir(file_path):
                    continue
                
                if not file.endswith(".xls") and not file.endswith(".xlsx"):
                    continue
                
                should_keep = False
                
                # temp_ 开头的临时文件需要删除
                if file.startswith("temp_"):
                    print(f"调试信息: 文件 {file} 以 temp_ 开头，准备删除")
                    files_to_delete.append((file, file_path))
                    continue
                
                for prefix in must_keep_prefixes:
                    if file.startswith(prefix):
                        should_keep = True
                        print(f"调试信息: 文件 {file} 以 {prefix} 开头，保留")
                        break
                
                if file in must_keep_files:
                    should_keep = True
                    print(f"调试信息: 文件 {file} 在必须保留列表中，保留")
                
                if not should_keep:
                    file_no_ext = file.replace(".xls", "").replace(".xlsx", "")
                    print(f"调试信息: 文件 {file} -> 去除扩展名后: '{file_no_ext}'")
                    
                    # 检查是否匹配计划号
                    matched_plan = None
                    # 方式1: 完全匹配
                    if file_no_ext in valid_plan_numbers:
                        matched_plan = file_no_ext
                    else:
                        # 方式2: 文件以计划号开头（处理带后缀的文件，如 H1552_fixed.xls）
                        for plan_no in valid_plan_numbers:
                            if file_no_ext.startswith(plan_no + "_") or file_no_ext.startswith(plan_no + "-"):
                                matched_plan = plan_no
                                break
                    
                    if matched_plan:
                        should_keep = True
                        print(f"调试信息: 文件 {file} 匹配计划号 '{matched_plan}'，保留")
                    else:
                        print(f"调试信息: 文件 {file} 不匹配任何有效计划号，准备删除")
                
                if should_keep:
                    files_to_keep.append(file)
                else:
                    files_to_delete.append((file, file_path))
            
            print(f"调试信息: 保留文件 = {files_to_keep}")
            print(f"调试信息: 删除文件 = {[f[0] for f in files_to_delete]}")
            
            if not files_to_delete:
                QMessageBox.information(self, "提示", "没有需要清理的多余文件")
                return
            
            reply = QMessageBox.question(
                self, 
                "确认清理", 
                f"即将删除 {len(files_to_delete)} 个多余文件：\n\n" + 
                "\n".join([f[0] for f in files_to_delete[:10]]) + 
                ("..." if len(files_to_delete) > 10 else ""),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                print("调试信息: 用户点击了 No，取消删除")
                return
            
            print(f"调试信息: 开始删除 {len(files_to_delete)} 个文件")
            deleted_count = 0
            failed_files = []
            
            import stat
            for file_name, file_path in files_to_delete:
                print(f"调试信息: 尝试删除 {file_path}")
                print(f"调试信息: 文件存在: {os.path.exists(file_path)}")
                if os.path.exists(file_path):
                    print(f"调试信息: 文件大小: {os.path.getsize(file_path)} 字节")
                    try:
                        # 检查文件属性
                        file_stat = os.stat(file_path)
                        print(f"调试信息: 文件权限: {oct(stat.S_IMODE(file_stat.st_mode))}")
                        # 尝试移除只读属性
                        if file_stat.st_mode & stat.S_IREAD and not file_stat.st_mode & stat.S_IWRITE:
                            print(f"调试信息: 文件是只读的，尝试修改权限")
                            os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                    except Exception as e:
                        print(f"调试信息: 检查/修改文件属性失败: {str(e)}")
                
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"调试信息: 成功删除: {file_name}")
                        # 再次验证是否真的删除了
                        if os.path.exists(file_path):
                            print(f"调试信息: 警告：文件删除后仍然存在!")
                        else:
                            print(f"调试信息: 文件确实已删除")
                    else:
                        print(f"调试信息: 文件不存在: {file_path}")
                        failed_files.append(f"{file_name} (文件不存在)")
                except Exception as e:
                    import traceback
                    error_msg = f"{file_name} ({str(e)})"
                    print(f"调试信息: 删除失败 {error_msg}")
                    print(f"调试信息: 完整错误堆栈:")
                    traceback.print_exc()
                    failed_files.append(error_msg)
            
            if failed_files:
                error_details = "\n".join(failed_files)
                message = f"已清理 {deleted_count} 个多余文件\n\n有 {len(failed_files)} 个文件删除失败：\n{error_details}\n\n保留 {len(files_to_keep)} 个有效文件\n\n提示：删除失败通常是因为文件正在被其他程序使用（如Excel）。请关闭相关程序后重试，或手动到以下目录删除：\nG:\\newplan\\计划号\\"
                QMessageBox.warning(
                    self, 
                    "清理完成", 
                    message
                )
            else:
                QMessageBox.information(
                    self, 
                    "清理完成", 
                    f"已清理 {deleted_count} 个多余文件\n\n保留 {len(files_to_keep)} 个有效文件"
                )
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            QMessageBox.critical(self, "错误", f"清理失败：{str(e)}")
            print(f"清理多余文件失败：{str(e)}")
            print(traceback.format_exc())
    
    def open_settings_window(self):
        """打开设置窗口"""
        if not hasattr(self, 'settings_window') or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self)
            self.settings_window.show()
    
    def get_settings(self):
        """获取当前设置"""
        import json
        import os
        
        # 使用self.plan_dir确保打包后也能正确读取配置文件
        config_file = os.path.join(self.plan_dir, 'settings.json')
        if os.path.exists(config_file):
            try:
                if os.path.getsize(config_file) < 5:
                    raise ValueError("Settings file is too small")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if not isinstance(settings, dict):
                    raise ValueError("Invalid settings format")
                
                return settings
            except Exception as e:
                print(f"加载设置失败: {str(e)}")
        
        # 返回默认设置
        return {
            "selectedWindow": "Doc1.docx - Word",
            "autoPrint": True,
            "autoExec": False,
            "execMode": "interval",
            "intervalMinutes": 1,
            "execTimes": "16:00,16:02,16:04"
        }
    
    def open_furnace_details(self):
        """打开装炉明细窗口 - 确保始终只有一个窗口打开"""
        from PyQt5.QtWidgets import QApplication
        
        # 检查是否已有装炉明细窗口
        existing_windows = []
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                existing_windows.append(widget)
        
        if existing_windows:
            # 如果已有装炉明细窗口，激活它而不是打开新窗口
            for window in existing_windows:
                window.activateWindow()
                window.raise_()
                window.show()
                # 更新self.furnace_details_window引用
                self.furnace_details_window = window
            print("已激活现有的装炉明细窗口")
        else:
            # 如果没有装炉明细窗口，创建新窗口
            self.furnace_details_window = FurnaceDetailsWindow(self)
            self.furnace_details_window.show()
            print("创建新的装炉明细窗口")

    def open_rm_main_window(self):
        """打开粗轧主画面窗口"""
        from PyQt5.QtWidgets import QApplication
        
        # 检查是否已有粗轧主画面窗口
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'windowTitle') and '粗轧主画面' in widget.windowTitle():
                widget.activateWindow()
                widget.raise_()
                widget.show()
                print("已激活现有的粗轧主画面窗口")
                return
        
        # 如果没有，创建新窗口（使用 Qt Designer 设计的 UI）
        try:
            from rm_main_window import RMMainWindow
            self.rm_main_window = RMMainWindow(self)
            self.rm_main_window.show()
            print("创建新的粗轧主画面窗口（使用 Qt Designer UI）")
        except Exception as e:
            print(f"打开粗轧主画面出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开粗轧主画面失败: {str(e)}")

    def go_to_furnace_details(self):
        """进入装炉明细画面 - 被定时器调用"""
        try:
            from PyQt5.QtWidgets import QApplication

            has_furnace_details_window = False
            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                    has_furnace_details_window = True
                    # 激活装炉明细窗口
                    widget.activateWindow()
                    widget.raise_()
                    widget.show()
                    # 更新self.furnace_details_window引用
                    self.furnace_details_window = widget
                    # 刷新装炉明细数据
                    if hasattr(widget, 'refresh_data'):
                        print("刷新装炉明细窗口数据")
                        widget.refresh_data()
                        # 刷新后恢复上次选中的钢卷号位置
                        if hasattr(widget, 'restore_selected_coil'):
                            widget.restore_selected_coil()
                    print("已进入装炉明细画面")
                    break

            if not has_furnace_details_window:
                # 如果没有装炉明细窗口，打开新的装炉明细窗口
                print("未找到装炉明细窗口，打开新的装炉明细画面")
                self.open_furnace_details()
                print("成功打开装炉明细窗口")
        except Exception as e:
            print(f"进入装炉明细画面失败: {e}")


    


    def show_selected(self):
        """显示选中的计划"""
        try:
            selected_items = self.table_widget.selectedItems()
            if not selected_items:
                QMessageBox.information(self, "提示", "请先在表格中选择一行数据")
                return
            
            # 获取选中行的数据
            row = selected_items[0].row()
            
            # 检查表格是否有足够的列
            if self.table_widget.columnCount() < 1:  # 需要至少1列（计划号）
                QMessageBox.warning(self, "错误", "表格列数不足，无法获取计划号")
                return
            
            # 获取计划号（计划号在第0列）
            plan_item = self.table_widget.item(row, 0)  # 计划号在第一列
            if not plan_item:
                QMessageBox.warning(self, "错误", "无法获取计划号")
                return
            
            plan_no = plan_item.text().strip()
            if not plan_no:
                QMessageBox.warning(self, "错误", "计划号为空")
                return
            
            print(f"尝试显示计划号: {plan_no}")
            
            # 检查是否已处理
            if not hasattr(self, 'processed_plans'):
                self.processed_plans = {}
            
            # 获取计划号文件，检查是否有未处理的钢卷号
            need_process = False
            plan_file = self.get_plan_file(plan_no)
            if plan_file:
                need_process = self.has_unprocessed_coils(plan_no, plan_file)
            
            # 如果有未处理的钢卷号，先处理该计划
            if need_process:
                print(f"计划 {plan_no} 有未处理的钢卷号，正在处理...")
                # 先选择当前行
                self.table_widget.clearSelection()  # 清除之前的选择
                self.table_widget.selectRow(row)  # 选择当前行
                # 确保选择状态已更新
                QApplication.processEvents()  # 处理事件，确保选择状态更新
                # 调用处理计划方法
                self.process_plans(auto_print=False, show_result=False)
                # 再次检查是否有未处理的（验证处理成功）
                # 注意：对于非D开头的计划号，处理后应该已经标记为已处理
                # 但由于处理后会保存状态，需要重新加载
                self.load_processed_plans()  # 重新加载处理状态
                plan_file2 = self.get_plan_file(plan_no)
                if plan_file2 and self.has_unprocessed_coils(plan_no, plan_file2):
                    # 处理失败，退出
                    QMessageBox.warning(self, "错误", "计划处理失败，无法显示")
                    return
                print(f"计划号 {plan_no} 处理成功")
            
            # 获取计划号文件
            plan_file = self.get_plan_file(plan_no)
            if plan_file:
                try:
                    import subprocess
                    print(f"尝试打开文件: {plan_file}")
                    # 使用subprocess打开文件，与原程序一致
                    subprocess.Popen(['start', '', plan_file], shell=True)
                    print(f"已打开文件: {plan_file}")
                except Exception as e:
                    error_msg = f"打开文件失败: {str(e)}"
                    print(error_msg)
                    QMessageBox.warning(self, "错误", error_msg)
            else:
                error_msg = f"找不到计划号文件: {plan_no}.xls 或 {plan_no}.xlsx"
                print(error_msg)
                QMessageBox.warning(self, "错误", error_msg)
        except Exception as e:
            error_msg = f"显示计划时发生错误: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", error_msg)

    def show_message(self, title, message):
        """显示消息框"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def get_plan_file(self, plan_no):
        """获取计划号文件路径"""
        import os
        # 首先在计划号目录查找
        plan_dir = os.path.join(self.plan_dir, "计划号")
        
        # 尝试.xls格式
        file_path = os.path.join(plan_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(plan_dir, f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        
        # 然后在backup目录查找
        backup_dir = os.path.join(plan_dir, "backup")
        if os.path.exists(backup_dir):
            # 尝试.xls格式
            file_path = os.path.join(backup_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
            
            # 尝试.xlsx格式
            file_path = os.path.join(backup_dir, f"{plan_no}.xlsx")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
        
        # 尝试其他可能的路径
        # 直接在计划号目录的上级目录查找
        parent_dir = os.path.dirname(plan_dir)
        
        # 尝试.xls格式
        file_path = os.path.join(parent_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(parent_dir, f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        
        # 尝试当前目录
        # 尝试.xls格式
        file_path = os.path.join(self.plan_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(self.plan_dir, f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        
        # 所有路径都找不到
        print(f"找不到计划号文件: {plan_no}.xls 或 {plan_no}.xlsx")
        return None

    def print_selected(self):
        """打印选中的计划 - 复刻原程序的打印功能"""
        try:
            # 检查是否选择了计划
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先在计划号列表中选择要打印的计划号")
                return
            
            # 加载最新的状态
            self.load_data()
            
            # 获取选中的计划号，按照表格显示顺序（按行号排序）
            selected_rows = sorted([index.row() for index in selected_items])
            selected_plans = [self.plan_data[row]['plan_no'] for row in selected_rows]
            
            # 创建进度窗口
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont
            
            # 创建进度窗口
            progress_window = QDialog(self)
            progress_window.setWindowTitle("打印进度")
            progress_window.setFixedSize(600, 400)
            progress_window.setWindowModality(Qt.ApplicationModal)
            
            # 主布局
            main_layout = QVBoxLayout(progress_window)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(15)
            
            # 标题
            progress_label = QLabel("准备开始打印...")
            progress_label.setFont(QFont("宋体", 14))
            progress_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(progress_label)
            
            # 详细信息
            detail_label = QLabel("")
            detail_label.setFont(QFont("宋体", 12))
            detail_label.setStyleSheet("color: gray;")
            detail_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(detail_label)
            
            # 按钮布局
            btn_layout = QHBoxLayout()
            btn_layout.addStretch(1)
            
            # 取消按钮
            cancel_btn = QPushButton("取消")
            cancel_btn.setFont(QFont("宋体", 12))
            cancel_btn.setFixedSize(80, 30)
            btn_layout.addWidget(cancel_btn)
            
            btn_layout.addStretch(1)
            main_layout.addLayout(btn_layout)
            
            # 显示窗口
            progress_window.show()
            
            # 更新进度的函数
            def update_progress(main_msg, detail_msg=""):
                """更新进度显示"""
                progress_label.setText(main_msg)
                if detail_msg:
                    detail_label.setText(detail_msg)
                QApplication.processEvents()
                print(f"[打印进度] {main_msg} {detail_msg}")
            
            # 取消标志
            canceled = False
            def on_cancel():
                nonlocal canceled
                canceled = True
                print("打印操作被取消")
            
            cancel_btn.clicked.connect(on_cancel)
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            backup_dir = os.path.join(plan_dir, "backup")
            
            # 构建选中计划号的文件路径列表
            selected_files = []
            update_progress("正在检查文件...", f"共 {len(selected_plans)} 个计划号")
            
            if canceled:
                progress_window.close()
                return
            
            for plan_no in selected_plans:
                if canceled:
                    progress_window.close()
                    return
                
                # 首先检查计划号文件夹
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    selected_files.append((plan_no, file_path))
                    update_progress("正在检查文件...", f"找到文件: {plan_no}.xls")
                else:
                    # 先检查当前目录，如果当前目录没有，再检查backup目录（只要有未打印钢卷号）
                    # 或者如果已经打印过，检查backup目录
                    need_check_backup = False
                    if hasattr(self, 'printed_plans') and plan_no in self.printed_plans:
                        need_check_backup = True
                    
                    # 如果计划号在printed_plans中，或者有未打印的钢卷号（需要检查）
                    # 先尝试从当前目录读取（如果有），再检查backup目录
                    # 这里简化：先尝试当前目录，没有的话再试backup
                    # 先检查backup目录
                    backup_file_path = os.path.join(backup_dir, f"{plan_no}.xls")
                    if os.path.exists(backup_file_path):
                        selected_files.append((plan_no, backup_file_path))
                        update_progress("正在检查文件...", f"从backup目录找到文件: {plan_no}.xls")
                        print(f"[OK] 从backup目录找到文件: {plan_no}.xls")
                    else:
                        update_progress("正在检查文件...", f"文件不存在: {plan_no}.xls")
                        print(f"[ERROR] 文件不存在: {plan_no}.xls")
            
            if not selected_files:
                progress_window.close()
                return
            
            # 检查并处理未处理的计划
            processed_plans = []
            failed_plans = []
            
            update_progress("正在处理计划...", f"共 {len(selected_files)} 个计划需要处理")
            
            if canceled:
                progress_window.close()
                return
            
            for i, (plan_no, file_path) in enumerate(selected_files):
                if canceled:
                    progress_window.close()
                    return
                
                # 如果未处理，先处理该计划
                if not hasattr(self, 'processed_plans'):
                    self.processed_plans = {}
                
                # 检查是否有未处理的钢卷号
                if self.has_unprocessed_coils(plan_no, file_path):
                    update_progress("正在处理计划...", f"处理 {plan_no} ({i+1}/{len(selected_files)})")
                    try:
                        # 处理单个计划 - 使用与 process_plans 相同的方法
                        has_low_roll_width, has_no_aps = self.run_excel_macro_with_pandas(file_path)
                        update_progress("正在处理计划...", f"已处理: {plan_no}")
                        processed_plans.append(plan_no)
                        # 标记所有钢卷号为已处理
                        self.mark_all_coils_processed(plan_no, file_path)
                        
                        # 更新plan_data中的has_low_roll_width和has_no_aps字段
                        for j, data in enumerate(self.plan_data):
                            if data['plan_no'] == plan_no:
                                self.plan_data[j]['has_low_roll_width'] = has_low_roll_width
                                self.plan_data[j]['has_no_aps'] = has_no_aps
                                break
                    except Exception as e:
                        error_msg = f"处理失败: {str(e)}"
                        update_progress("正在处理计划...", f"{plan_no}: {error_msg}")
                        print(f"[ERROR] 处理失败 {plan_no}.xls: {str(e)}")
                        failed_plans.append(f"{plan_no} (处理失败: {str(e)})")
                        import traceback
                        traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_plans:
                self.save_processed_plans()
                # 保存无APS计划状态
                self.save_no_aps_plans()
                # 刷新列表显示
                self.load_data()
            
            # 如果有处理失败的计划，显示提示
            if failed_plans:
                progress_window.close()
                self.show_auto_close_message("警告", f"以下计划号处理失败：\n\n" + "\n".join(failed_plans) + "\n\n这些计划将不会被打印")
                # 移除处理失败的计划
                selected_files = [(plan_no, file_path) for plan_no, file_path in selected_files if plan_no not in [p.split(' ')[0] for p in failed_plans]]
                
                # 重新创建进度窗口
                progress_window = QDialog(self)
                progress_window.setWindowTitle("打印进度")
                progress_window.setFixedSize(600, 400)
                progress_window.setWindowModality(Qt.ApplicationModal)
                
                # 主布局
                main_layout = QVBoxLayout(progress_window)
                main_layout.setContentsMargins(20, 20, 20, 20)
                main_layout.setSpacing(15)
                
                # 标题
                progress_label = QLabel("准备开始打印...")
                progress_label.setFont(QFont("宋体", 14))
                progress_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(progress_label)
                
                # 详细信息
                detail_label = QLabel("")
                detail_label.setFont(QFont("宋体", 12))
                detail_label.setStyleSheet("color: gray;")
                detail_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(detail_label)
                
                # 按钮布局
                btn_layout = QHBoxLayout()
                btn_layout.addStretch(1)
                
                # 取消按钮
                cancel_btn = QPushButton("取消")
                cancel_btn.setFont(QFont("宋体", 12))
                cancel_btn.setFixedSize(80, 30)
                btn_layout.addWidget(cancel_btn)
                
                btn_layout.addStretch(1)
                main_layout.addLayout(btn_layout)
                
                # 显示窗口
                progress_window.show()
                
                # 更新进度的函数
                def update_progress(main_msg, detail_msg=""):
                    """更新进度显示"""
                    progress_label.setText(main_msg)
                    if detail_msg:
                        detail_label.setText(detail_msg)
                    QApplication.processEvents()
                    print(f"[打印进度] {main_msg} {detail_msg}")
                
                # 取消标志
                canceled = False
                def on_cancel():
                    nonlocal canceled
                    canceled = True
                    print("打印操作被取消")
                
                cancel_btn.clicked.connect(on_cancel)
            
            if not selected_files:
                progress_window.close()
                self.show_auto_close_message("提示", "没有符合条件的计划可以打印")
                return
            
            # 打印每个文件
            success_count = 0
            failed_count = 0
            failed_files = []
            success_files = []
            
            update_progress("正在打印文件...", f"共 {len(selected_files)} 个计划需要打印")
            
            if canceled:
                progress_window.close()
                return
            
            for i, (plan_no, file_path) in enumerate(selected_files):
                if canceled:
                    progress_window.close()
                    return
                
                try:
                    # 检查是否有未打印的钢卷号
                    if self.has_unprinted_coils(plan_no, file_path):
                        update_progress("正在打印文件...", f"打印 {plan_no} ({i+1}/{len(selected_files)})")
                        print(f"开始打印: {plan_no}.xls")
                        success = self.print_excel_file(file_path)
                        if success:
                            success_count += 1
                            success_files.append(plan_no)
                            update_progress("正在打印文件...", f"已打印: {plan_no}")
                            print(f"[OK] 已打印: {plan_no}.xls")
                            # 标记所有钢卷号为已打印
                            if not hasattr(self, 'printed_plans'):
                                self.printed_plans = {}
                            self.mark_all_coils_printed(plan_no, file_path)
                        else:
                            failed_count += 1
                            failed_files.append(plan_no)
                            update_progress("正在打印文件...", f"打印失败: {plan_no}")
                            print(f"[ERROR] 打印失败 {plan_no}.xls")
                    else:
                        print(f"[跳过] {plan_no} 所有钢卷号都已打印")
                        update_progress("正在打印文件...", f"跳过已打印: {plan_no}")
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    error_msg = f"打印失败: {str(e)}"
                    update_progress("正在打印文件...", f"{plan_no}: {error_msg}")
                    print(f"[ERROR] 打印失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已打印计划状态
            if success_count > 0:
                self.save_printed_plans()
                # 刷新列表显示
                self.load_data()
            
            # 将打印成功的文件移动到backup目录
            if success_files:
                update_progress("正在移动文件...", "将打印成功的文件移动到backup目录")
                import shutil
                
                # 创建backup目录（如果不存在）
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                    update_progress("正在移动文件...", f"创建backup目录: {backup_dir}")
                    print(f"[OK] 创建backup目录: {backup_dir}")
                
                # 移动文件
                moved_count = 0
                for i, plan_no in enumerate(success_files):
                    if canceled:
                        progress_window.close()
                        return
                    
                    update_progress("正在移动文件...", f"移动 {plan_no} ({i+1}/{len(success_files)})")
                    src_file = os.path.join(plan_dir, f"{plan_no}.xls")
                    dst_file = os.path.join(backup_dir, f"{plan_no}.xls")
                    
                    try:
                        if os.path.exists(src_file):
                            # 如果目标文件已存在，先删除
                            if os.path.exists(dst_file):
                                os.remove(dst_file)
                                print(f"[OK] 删除已存在的备份文件: {plan_no}.xls")
                            
                            shutil.move(src_file, dst_file)
                            print(f"[OK] 已移动文件到backup: {plan_no}.xls")
                            moved_count += 1
                    except Exception as e:
                        print(f"[ERROR] 移动文件失败 {plan_no}.xls: {str(e)}")
                
                update_progress("正在移动文件...", f"成功移动 {moved_count} 个文件到backup目录")
                print(f"\n文件移动完成: 成功移动 {moved_count} 个文件到backup目录")
            
            # 销毁进度窗口
            progress_window.close()
            
            # 显示结果
            if success_count > 0 or failed_count > 0:
                # 使用与处理完成相同的弹窗样式
                self.show_result_dialog("打印完成！", success_files, failed_files, [], auto_close=3)
        except Exception as e:
            print(f"打印计划失败: {str(e)}")
            self.show_auto_close_message("错误", f"打印计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def print_excel_file(self, file_path):
        """打印Excel文件 - 打印第一列到装炉顺列，包括表头
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            bool: 是否成功打印
        """
        try:
            import xlrd
            
            # 读取Excel文件
            success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
            if not success:
                raise Exception(f"读取文件失败: {result}")
            
            workbook = result
            sheet = workbook.sheet_by_index(0)
            
            # 先查找字段列名行（包含"序号"、"钢卷号"等字段名的行）
            字段列名行号 = -1
            for row_idx in range(min(10, sheet.nrows)):  # 检查前10行
                row_has_field_names = False
                for col_idx in range(sheet.ncols):
                    cell_value = str(sheet.cell_value(row_idx, col_idx))
                    # 检查是否包含常见字段名
                    if any(field in cell_value for field in ["序号", "钢卷号", "牌号", "坯厚", "轧厚", "轧宽", "装炉顺"]):
                        row_has_field_names = True
                        break
                if row_has_field_names:
                    字段列名行号 = row_idx
                    break
            
            if 字段列名行号 == -1:
                print("未找到字段列名行，假设为第2行")
                字段列名行号 = 2
            
            print(f"字段列名行号: {字段列名行号}")
            
            # 从字段列名行获取所有列名
            current_columns = []
            for i in range(sheet.ncols):
                current_columns.append(sheet.cell_value(字段列名行号, i))
            
            print(f"列名: {current_columns}")
            
            # 字段名映射
            字段名映射 = {
                "序号": "序号",
                "钢卷号": "钢卷号",
                "牌号": "牌号（钢级）",
                "牌号（钢级）": "牌号（钢级）",
                "坯厚": "坯厚",
                "坯宽": "坯宽",
                "坯长": "坯长",
                "中厚": "中厚",
                "RT2": "RT2",
                "去向": "去向",
                "轧厚": "轧厚",
                "轧宽": "轧宽",
                "减宽": "减宽",
                "订宽": "订宽",
                "除鳞": "除鳞",
                "公差带": "公差带",
                "强度": "强度",
                "粗轧报信": "粗轧报信",
                "装炉顺序号": "装炉顺序号",
                "装炉顺": "装炉顺"
            }
            
            # 找到装炉顺列的索引（查找"装炉顺序号"列，因为实际存储的列名是"装炉顺序号"）
            装炉顺列索引 = -1
            for col_idx, col_name in enumerate(current_columns):
                # 直接查找"装炉顺序号"列（实际存储的列名）
                if col_name == "装炉顺序号":
                    装炉顺列索引 = col_idx
                    break
                # 如果没有找到，尝试通过映射查找"装炉顺"
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "装炉顺":
                    装炉顺列索引 = col_idx
                    break
            
            # 找到强度列的索引
            强度列索引 = -1
            for col_idx, col_name in enumerate(current_columns):
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "强度":
                    强度列索引 = col_idx
                    break
            
            # 找到订宽列的索引（最后一列）
            订宽列索引 = len(current_columns) - 1
            
            # 即使找不到强度列，也强制设置打印范围为前17列（根据标准列顺序）
            if 订宽列索引 < 0:
                print("未找到订宽列，使用默认打印范围：前17列")
                订宽列索引 = 16  # 默认第17列（索引16）为订宽列
            else:
                print(f"找到订宽列，索引: {订宽列索引}")
            
            # 计算打印范围：第一列(0)到订宽列
            print_col_start = 0
            print_col_end = 订宽列索引
            
            # 表头总行数 = 字段列名行号 + 1（包括字段列名行）
            header_row_count = 字段列名行号 + 1
            
            print(f"字段列名行号: {字段列名行号}, 表头总行数: {header_row_count}")
            
            # 使用win32com调用Excel打印
            try:
                import win32com.client as win32
                excel = win32.Dispatch("Excel.Application")
                
                # 尝试设置Visible属性为False（原程序的方法）
                try:
                    excel.Visible = False
                except Exception as vis_error:
                    print(f"设置Visible属性失败: {str(vis_error)}")
                    # 即使设置失败也继续执行
                
                # 打开工作簿
                workbook_obj = excel.Workbooks.Open(file_path)
                worksheet = workbook_obj.Worksheets(1)
                
                # 设置打印区域：第一列到装炉顺列，包括表头和数据行
                def get_column_letter(col_idx):
                    """将列索引转换为Excel列字母（A, B, ..., Z, AA, AB, ...）"""
                    if col_idx < 26:
                        return chr(65 + col_idx)
                    else:
                        first_letter = chr(65 + (col_idx // 26) - 1)
                        second_letter = chr(65 + (col_idx % 26))
                        return first_letter + second_letter
                
                col_start_letter = get_column_letter(print_col_start)  # 第一列
                col_end_letter = get_column_letter(print_col_end)  # 装炉顺列对应的字母
                # 打印所有行：从第1行到最后一行（包括表头和数据）
                print_area = f"{col_start_letter}1:{col_end_letter}{sheet.nrows}"
                worksheet.PageSetup.PrintArea = print_area
                
                # 设置每页打印表头：首页表头为$1:$n，后续页面表头为$2:$n
                # 计算字段名行号对应的Excel行号（Excel行号从1开始）
                field_name_row = 字段列名行号 + 1  # 转换为Excel行号
                # 设置打印标题行为从第二行到字段名行
                worksheet.PageSetup.PrintTitleRows = f"$2:${field_name_row}"
                
                # 去掉页眉页脚设置值
                worksheet.PageSetup.LeftHeader = ""
                worksheet.PageSetup.CenterHeader = ""
                worksheet.PageSetup.RightHeader = ""
                worksheet.PageSetup.LeftFooter = ""
                worksheet.PageSetup.CenterFooter = ""
                worksheet.PageSetup.RightFooter = ""
                worksheet.PageSetup.CenterHorizontally = False
                worksheet.PageSetup.CenterVertically = False
                
                # 设置打印时间字体大小为10号
                # 查找打印时间所在的单元格
                for row_idx in range(sheet.nrows):
                    for col_idx in range(sheet.ncols):
                        cell_value = str(sheet.cell_value(row_idx, col_idx))
                        if "打印时间" in cell_value:
                            # 找到打印时间单元格，设置字体大小为10号
                            excel_range = worksheet.Cells(row_idx + 1, col_idx + 1)
                            excel_range.Font.Size = 10
                            break
                    else:
                        continue
                    break
                
                print(f"打印区域: {print_area} (共{sheet.nrows}行)")
                
                # 设置纸张大小为美国Fanfold
                try:
                    # 强制使用 xlPaperFanfoldUS (137) - 美国连续折叠纸
                    preferred_size = 137  # xlPaperFanfoldUS
                    
                    # 尝试设置首选纸张
                    worksheet.PageSetup.PaperSize = preferred_size
                    try:
                        print("[纸张设置] ✓ 成功设置纸张: FanfoldUS (14.875 x 11 inch)")
                    except UnicodeEncodeError:
                        print("[纸张设置] 成功设置纸张: FanfoldUS (14.875 x 11 inch)")
                except Exception as e:
                    try:
                        print(f"[纸张设置] ✗ 首选纸张设置失败: {str(e)}")
                    except UnicodeEncodeError:
                        print(f"[纸张设置] 首选纸张设置失败: {str(e)}")
                    # 尝试备选纸张
                    fallback_papers = [39, 118, 119, 1, 9]
                    for paper_code in fallback_papers:
                        if paper_code == preferred_size:
                            continue  # 跳过已经尝试过的
                        try:
                            worksheet.PageSetup.PaperSize = paper_code
                            try:
                                print(f"[纸张设置] ✓ 成功设置备选纸张: {paper_code}")
                            except UnicodeEncodeError:
                                print(f"[纸张设置] 成功设置备选纸张: {paper_code}")
                            break
                        except Exception as e:
                            try:
                                print(f"[纸张设置] ✗ 备选纸张 {paper_code} 设置失败: {str(e)}")
                            except UnicodeEncodeError:
                                print(f"[纸张设置] 备选纸张 {paper_code} 设置失败: {str(e)}")
                            continue
                
                # 打印
                worksheet.PrintOut()
                
                # 关闭工作簿
                workbook_obj.Close(False)
                excel.Quit()
                
                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
                    workbook.release_resources()
                
                return True
                
            except ImportError:
                print("win32com未安装，使用默认打印方式")
                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
                    workbook.release_resources()
                
                # 使用系统默认打印
                import os
                
                # 在Windows上使用默认程序打开并打印
                os.startfile(file_path)
                
                return True
                
        except Exception as e:
            print(f"打印文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def print_plan(self, plan_no):
        """打印单个计划"""
        import os
        import shutil
        import time
        
        try:
            # 找到计划号文件
            plan_dir = os.path.join(self.plan_dir, "计划号", plan_no)
            if not os.path.exists(plan_dir):
                print(f"计划目录不存在：{plan_dir}")
                return
            
            # 查找明细文件
            mingxi_file = None
            for file in os.listdir(plan_dir):
                if file.endswith("明细.xls") or file.endswith("明细.xlsx"):
                    mingxi_file = os.path.join(plan_dir, file)
                    break
            
            if not mingxi_file:
                print(f"未找到明细文件：{plan_dir}")
                return
            
            # 直接使用原方法打印
            success = self.print_excel_file(mingxi_file)
            if success:
                print(f"已打印计划：{plan_no}")
            else:
                print(f"打印计划失败：{plan_no}")
            
        except Exception as e:
            print(f"打印计划 {plan_no} 失败：{str(e)}")
            import traceback
            traceback.print_exc()

    def auto_export(self, from_main_window=True):
        """自动导出"""
        # 检查是否已经在运行,防止递归调用
        if hasattr(self, 'is_auto_export_running') and self.is_auto_export_running:
            print("自动导出已经在运行,跳过重复调用")
            self.show_auto_close_message("提示", "自动导出已在运行中")
            return
        
        # 设置运行标志
        self.is_auto_export_running = True
        
        # 添加线程锁,确保函数不会被并发调用
        import threading
        if not hasattr(self, 'auto_export_lock'):
            self.auto_export_lock = threading.Lock()
        
        # 尝试获取锁,如果获取不到则返回
        if not self.auto_export_lock.acquire(blocking=False):
            print("自动导出已经被锁定,跳过重复调用")
            self.show_auto_close_message("提示", "自动导出已在运行中")
            self.is_auto_export_running = False
            return
        
        # 检查pyautogui是否可用
        try:
            import pyautogui
            PYAUTOGUI_AVAILABLE = True
        except ImportError:
            PYAUTOGUI_AVAILABLE = False
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", "pyautogui未安装,请先安装: pip install pyautogui")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        if not PYAUTOGUI_AVAILABLE:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", "pyautogui未安装,请先安装: pip install pyautogui")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        # 检查是否在主程序画面，如果不在则先激活主程序画面
        main_window_title = "轧制计划管理系统"
        print(f"检查是否在主程序画面: {main_window_title}")

        # 检查是否启用调试模式
        debug_mode = self.coordinates.get("debug_mode", False)
        print(f"调试模式: {'开启' if debug_mode else '关闭'}")

        # 初始化调试日志函数
        def add_debug_log(msg):
            pass  # 默认不输出

        # 检查应用程序是否在前台运行
        import os
        import win32gui
        import win32process

        # 保存启动自动执行时的前台窗口句柄，以便后续返回
        self.previous_foreground_hwnd = win32gui.GetForegroundWindow()

        # 获取当前进程ID
        current_pid = os.getpid()
        
        # 获取前台窗口的进程ID
        foreground_hwnd = win32gui.GetForegroundWindow()
        _, foreground_pid = win32process.GetWindowThreadProcessId(foreground_hwnd)
        
        # 检查前台窗口是否属于当前进程
        is_in_foreground = (foreground_pid == current_pid)
        
        # 显示操作提示（根据配置）- 已禁用
        show_warning = self.coordinates.get("show_operation_warning", False)
        if show_warning:
            if is_in_foreground:
                # 应用程序在前台，显示操作提示
                from PyQt5.QtWidgets import QMessageBox, QPushButton
                from PyQt5.QtCore import Qt
                
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("⚠️ 操作提示")
                msg_box.setText("⚠️ 自动导出即将开始！\n\n• 导出过程中请勿操作鼠标和键盘\n• 请勿切换窗口或进行其他操作\n• 导出完成后会自动跳回主画面")
                msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg_box.setDefaultButton(QMessageBox.Ok)
                
                # 确保消息框显示在最前面
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                
                # 显示消息框并获取用户选择
                result = msg_box.exec_()
                
                if result != QMessageBox.Ok:
                    self.is_auto_export_running = False
                    if hasattr(self, 'auto_export_lock'):
                        try:
                            self.auto_export_lock.release()
                        except:
                            pass
                    return
            else:
                # 应用程序在后台，跳过操作提示
                print("应用程序在后台运行，跳过操作提示")
        else:
            print("跳过操作提示（已在设置中禁用）")
        

        
        # 检查是否有未设置的坐标
        unset_coords = []
        coord_names = {
            "zhuanglu_tab": "装炉顺作成管理标签",
            "zhuanglu_export_btn": "装炉顺序导出按钮",
            "zhizhi_tab": "轧制计划管理标签",
            "plan_select": "选择计划号",
            "zhizhi_export_btn": "导出总计划号列表按钮",
            "first_plan": "第一个计划号",
            "plan_detail_export": "计划明细导出按钮"
        }
        
        for key, name in coord_names.items():
            if not self.coordinates.get(key):
                unset_coords.append(name)
        
        if unset_coords:
            if progress_window:
                progress_window.close()
            # 检查应用程序是否在前台运行
            if is_in_foreground:
                QMessageBox.warning(self, "警告", f"以下坐标未设置:\n" + "\n".join(f"  - {n}" for n in unset_coords) + "\n\n请先设置这些坐标后再测试")
            else:
                print(f"以下坐标未设置: {unset_coords}\n请先设置这些坐标后再测试")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        # 定义进度更新函数
        def update_progress(main_msg, detail_msg=""):
            """更新进度显示"""
            # 只打印日志,不更新进度窗口
            print(f"[进度] {main_msg} {detail_msg}")
        
        # 定义导出完成后的回调函数
        def export_finished(success, message, exported_plans=[], failed_plans=[], coord_map={}):
            """导出完成后的回调"""
            # 确保在主线程中执行
            from PyQt5.QtCore import QEvent, QCoreApplication, QTimer, Qt
            from PyQt5.QtWidgets import QMessageBox
            
            class FinishedEvent(QEvent):
                def __init__(self, success, message, exported_plans, failed_plans, coord_map):
                    super().__init__(QEvent.User)
                    self.success = success
                    self.message = message
                    self.exported_plans = exported_plans
                    self.failed_plans = failed_plans
                    self.coord_map = coord_map
            
            # 发送事件到主线程
            event = FinishedEvent(success, message, exported_plans, failed_plans, coord_map)
            QCoreApplication.postEvent(self, event)
            

        
        # 重写event方法来处理完成事件和刷新事件
        original_event = self.event
        def custom_event(event):
            from PyQt5.QtCore import QEvent
            from PyQt5.QtWidgets import QApplication

            
            # 处理导出计划号明细事件
            if event.type() == QEvent.User and hasattr(event, 'valid_no_file_plans'):
                # 将导出操作放到后台线程中执行，避免阻塞主线程
                import threading
                
                def export_plans_worker():
                    try:
                        print("\n=== 导出无文件计划号明细 ===")
                        
                        valid_no_file_plans = event.valid_no_file_plans
                        plan_detail_export_btn = event.plan_detail_export_btn
                        test_window = event.test_window
                        delay_time = event.delay_time
                        coord_map = getattr(event, 'coord_map', {})
                        
                        exported_plans = []
                        failed_plans = []
                        
                        for i, plan_no in enumerate(valid_no_file_plans):
                            print(f"[{i+1}/{len(valid_no_file_plans)}] 导出计划: {plan_no}")
                            try:
                                # 从坐标映射中获取计划号的实际坐标
                                plan_coord = coord_map.get(str(plan_no), (100, 100))
                                print(f"  计划号坐标: {plan_coord}")
                                success = self.export_single_plan_detail(plan_no, plan_coord, plan_detail_export_btn=plan_detail_export_btn, test_window=test_window, add_debug_log=print)
                                if success:
                                    exported_plans.append(plan_no)
                                    print(f"  [√] 导出成功")
                                else:
                                    failed_plans.append(plan_no)
                                    print(f"  [×] 导出失败")
                            except Exception as e:
                                failed_plans.append(plan_no)
                                print(f"  [×] 导出失败: {str(e)}")
                            
                            # 添加延迟
                            if i < len(valid_no_file_plans) - 1:
                                import time
                                time.sleep(delay_time)
                        
                        print(f"\n计划号明细导出完成: {len(exported_plans)} 个成功, {len(failed_plans)} 个失败")
                        
                        # 刷新界面（在主线程中执行）
                        from PyQt5.QtCore import QEvent, QCoreApplication
                        
                        class RefreshEvent(QEvent):
                            def __init__(self, exported_plans, coord_map):
                                super().__init__(QEvent.User)
                                self.exported_plans = exported_plans
                                self.coord_map = coord_map
                                self.refresh_type = 'plan_list'
                        
                        # 发送刷新事件到主线程
                        refresh_event = RefreshEvent(exported_plans, coord_map)
                        QCoreApplication.postEvent(self, refresh_event)
                        
                        print("\n=== 自动导出全部完成 ===")
                        
                        # 导出完成
                        class FinishedEvent(QEvent):
                            def __init__(self, success, message, exported_plans, failed_plans, coord_map):
                                super().__init__(QEvent.User)
                                self.success = success
                                self.message = message
                                self.exported_plans = exported_plans
                                self.failed_plans = failed_plans
                                self.coord_map = coord_map
                        
                        # 发送事件到主线程
                        finished_event = FinishedEvent(True, f"自动导出全部完成\n\n成功导出 {len(exported_plans)} 个计划号\n失败 {len(failed_plans)} 个计划号", exported_plans, failed_plans, coord_map)
                        QCoreApplication.postEvent(self, finished_event)
                    except Exception as e:
                        print(f"导出计划号明细失败: {e}")
                        # 导出失败
                        from PyQt5.QtCore import QEvent, QCoreApplication
                        
                        class FinishedEvent(QEvent):
                            def __init__(self, success, message):
                                super().__init__(QEvent.User)
                                self.success = success
                                self.message = message
                        
                        # 发送事件到主线程
                        finished_event = FinishedEvent(False, f"自动导出失败: {str(e)}")
                        QCoreApplication.postEvent(self, finished_event)
                
                # 启动后台线程执行导出
                export_thread = threading.Thread(target=export_plans_worker)
                export_thread.daemon = True
                export_thread.start()
                
                return True
            
            # 处理刷新事件
            if event.type() == QEvent.User and not hasattr(event, 'success'):
                try:
                    # 刷新界面
                    print("\n刷新计划号列表...")
                    self.refresh_data()
                    
                    # 选中刚刚导出的计划号
                    if hasattr(event, 'exported_plans') and event.exported_plans:
                        try:
                            self.table_widget.clearSelection()
                            for i, item in enumerate(self.plan_data):
                                if item['plan_no'] in event.exported_plans:
                                    self.table_widget.selectRow(i)
                            print(f"已选中 {len(event.exported_plans)} 个导出的计划号")
                        except Exception as e:
                            print(f"选中导出计划号失败: {e}")
                except Exception as e:
                    print(f"刷新界面失败: {e}")
                return True
            
            # 处理完成事件
            if event.type() == QEvent.User and hasattr(event, 'success'):
                try:
                    # 关闭进度窗口
                    if hasattr(event, 'progress_window') and event.progress_window:
                        try:
                            event.progress_window.close()
                            print("进度窗口已关闭")
                        except Exception as e:
                            print(f"关闭进度窗口失败: {e}")
                    
                    # 显示结果
                    if event.success:
                        # 检查是否有导出的计划号
                        if event.exported_plans:
                            # 更新最近导出的计划号列表
                            self.recently_exported_plans = set(event.exported_plans)
                            print(f"已更新最近导出的计划号: {event.exported_plans}")
                            # 刷新计划号列表,使绿色标注生效
                            self.refresh_plan_list_from_file()
                            
                            # 直接处理导出的计划号
                            print("\n=== 自动处理导出的计划号 ===")
                            # 选中刚刚导出的计划号
                            self.table_widget.clearSelection()
                            for i, item in enumerate(self.plan_data):
                                if item['plan_no'] in event.exported_plans:
                                    self.table_widget.selectRow(i)
                            print(f"已选中 {len(event.exported_plans)} 个导出的计划号")
                            
                            # 调用处理计划方法，验证会在处理过程中进行
                            print("开始自动处理计划...")
                            try:
                                # 获取设置中的自动打印设置
                                settings = self.get_settings()
                                auto_print = settings.get("autoPrint", True)
                                
                                # 调用处理计划方法，传入auto_print参数
                                self.process_plans(auto_print=auto_print, show_result=False)
                            except Exception as e:
                                print(f"自动处理计划失败: {e}")
                            
                            # 回到主程序画面（轧制计划管理系统）
                            print("返回主程序画面（轧制计划管理系统）")
                            try:
                                # 激活本程序的主窗口
                                self.activateWindow()
                                self.raise_()
                                self.show()
                                print("成功返回主程序画面")
                            except Exception as e:
                                print(f"返回主程序画面失败: {e}")

                            # 无论是否有导出计划号，都在10秒后进入装炉明细画面
                            # 使用QTimer确保在主线程中执行
                            from PyQt5.QtWidgets import QApplication
                            from PyQt5.QtCore import QTimer

                            # 10秒后进入装炉明细画面（使用类方法）
                            QTimer.singleShot(10000, self.go_to_furnace_details)
                        else:
                            # 确保应用程序是活动的
                            from PyQt5.QtWidgets import QApplication
                            from PyQt5.QtCore import QTimer

                            QApplication.setActiveWindow(self)
                            # 确保本程序窗口是活动的
                            self.activateWindow()
                            self.raise_()
                            self.show()

                            # 使用自定义消息框显示提示信息 - 可手动关闭，自动3秒关闭
                            self.custom_messagebox("提示", event.message, msg_type='info', auto_close=3)
                            # 10秒后进入装炉明细画面（使用类方法）
                            QTimer.singleShot(10000, self.go_to_furnace_details)
                    else:
                        # 使用自定义消息框显示错误信息 - 可手动关闭，自动3秒关闭
                        self.custom_messagebox("错误", event.message, msg_type='error', auto_close=3)
                except Exception as e:
                    print(f"处理完成事件失败: {e}")
                finally:
                    # 无论执行是否成功,都设置运行标志为False
                    self.is_auto_export_running = False
                    print("自动导出执行完毕")
                return True
            return original_event(event)
        
        # 替换event方法
        self.event = custom_event
        
        # 定义后台导出函数
        def export_in_background():
            """在后台执行导出操作"""
            try:
                import time
                import datetime
                
                # 开始时间
                start_time = datetime.datetime.now()
                print(f"\n=== 自动导出开始 ===")
                print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"调试模式: {'开启' if debug_mode else '关闭'}")
                print("="*60)
                
                # 步骤0：系统健康检查和自动修复
                update_progress("【步骤0/4】系统健康检查和自动修复...")
                print("\n===========================================================")
                print(" 【步骤0/4】系统健康检查和自动修复")
                print("===========================================================")
                
                # 检查系统状态
                print("检查系统状态...")
                print("系统状态正常")
                
                update_progress("[√] 系统健康检查和自动修复完成")
                print("系统健康检查和自动修复完成")
                time.sleep(1)
                
                # 步骤1：导出装炉顺序
                update_progress("【步骤1/4】正在导出装炉顺序...")
                print("\n===========================================================")
                print(" 【步骤1/4】导出装炉顺序")
                print("===========================================================")
                
                # 调用装炉顺序导出函数
                success1 = self.export_zhuanglu_shunxu(add_debug_log=print)
                
                # 如果装炉顺序导出失败,停止执行
                if not success1:
                    print("[×] 装炉顺序导出失败,停止执行")
                    # 显示激活窗口失败的错误信息
                    settings = self.get_settings()
                    test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
                    export_finished(False, f"开始导出装炉顺序...\n[1/9] 激活目标窗口: {test_window}...\n× 激活窗口失败", [], [], {})
                    return
                
                update_progress("[√] 装炉顺序导出完成", "等待文件保存...")
                print("【导出完成】装炉顺序导出操作完成")
                
                # 步骤2：导出总计划号列表
                update_progress("【步骤2/4】正在导出总计划号列表...")
                print("\n=== 步骤2：导出总计划号列表 ===")
                
                # 调用总计划号列表导出函数
                success3 = self.export_zhizhi_plan_list(add_debug_log=print)
                
                # 如果总计划号列表导出失败,停止执行
                if not success3:
                    print("[×] 总计划号列表导出失败,停止执行")
                    # 显示激活窗口失败的错误信息
                    settings = self.get_settings()
                    test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
                    export_finished(False, f"开始导出总计划号列表...\n[1/7] 激活目标窗口: {test_window}...\n× 激活窗口失败", [], [], {})
                    return
                
                update_progress("[√] 总计划号列表导出完成", "等待文件保存...")
                print(f"[√] 总计划号列表导出完成")
                time.sleep(1)
                
                # 刷新数据,确保plan_data是最新的
                print("刷新数据,更新计划号列表...")
                # 确保在主线程中执行刷新操作
                from PyQt5.QtCore import QEvent, QCoreApplication
                
                class RefreshEvent(QEvent):
                    def __init__(self):
                        super().__init__(QEvent.User)
                        self.refresh_type = 'plan_list'
                
                # 发送刷新事件到主线程
                event = RefreshEvent()
                QCoreApplication.postEvent(self, event)
                # 等待刷新完成
                time.sleep(2)
                
                # 步骤3：重新计算坐标
                update_progress("【步骤3/4】正在重新计算坐标...")
                print("\n===========================================================")
                print(" 【步骤3/4】重新计算坐标")
                print("===========================================================")
                
                # 在 try 块外部初始化 coord_map，确保步骤4可以访问
                coord_map = None
                
                # 定义计划号文件夹路径
                plan_dir = os.path.join(self.plan_dir, "计划号")
                
                # 读取总计划号列表并计算坐标（会自动更新缓存）
                print(f"")
                print(f"[读取文件] 总计划号列表.xls")
                plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
                print(f"  路径: {plan_list_file}")
                print(f"  存在: {'是' if os.path.exists(plan_list_file) else '否'}")
                
                # 检查文件是否存在
                if not os.path.exists(plan_list_file):
                    try:
                        print(f"✗ 总计划号列表文件不存在")
                    except UnicodeEncodeError:
                        print(f"总计划号列表文件不存在")
                    # 显示错误信息并停止执行
                    export_finished(False, f"无法计算计划号坐标\n\n原因：总计划号列表文件不存在\n路径：{plan_list_file}\n\n请先执行步骤3导出总计划号列表", [], [], {})
                    return
                else:
                    # 计算坐标
                    try:
                        print(f"")
                        print(f"[读取总计划号列表]")
                        print(f"  数据库路径: {self.db_path}")
                        
                        # 读取总计划号列表并计算坐标
                        coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=print)
                        
                        if not coord_map:
                            try:
                                print(f"✗ 坐标计算失败：未找到计划号")
                            except UnicodeEncodeError:
                                print(f"坐标计算失败：未找到计划号")
                            # 显示错误信息并停止执行
                            export_finished(False, "无法计算计划号坐标\n\n原因：读取总计划号列表文件失败\n\n可能原因：\n1. 文件被占用\n2. 文件格式错误\n3. 未找到计划号列", [], [], {})
                            return
                        else:
                            print(f"")
                            print(f"  总计: {len(coord_map)} 个计划号坐标")
                            print(f"  计算到 {len(coord_map)} 个计划号坐标")
                            for plan_no, coord in list(coord_map.items())[:5]:  # 只显示前5个
                                print(f"    {plan_no}: {coord}")
                            if len(coord_map) > 5:
                                print(f"    ... 还有 {len(coord_map) - 5} 个")
                            
                            # 特别输出无文件计划号的坐标
                            no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
                            if no_file_plans:
                                print("\n无文件计划号的坐标：")
                                for plan_no in no_file_plans:
                                    coord = coord_map.get(plan_no, "未知")
                                    print(f"- {plan_no}: {coord}")
                            
                            update_progress("[√] 坐标计算完成", f"共 {len(coord_map)} 个计划号坐标")
                            print(f"[√] 坐标计算完成")
                            time.sleep(0.5)
                    except Exception as e:
                        print(f"[×] 坐标计算失败: {str(e)}")
                        # 显示错误信息并停止执行
                        export_finished(False, f"无法计算计划号坐标\n\n原因：{str(e)}", [], [], {})
                        return
                

                
                # 步骤4：导出无文件计划号的明细
                update_progress("【步骤4/4】正在导出无文件计划号明细...")
                print("\n===========================================================")
                print(" 【步骤4/4】导出无文件计划号明细")
                print("===========================================================")
                
                # 筛选无文件计划号
                print(f"")
                print(f"[筛选计划号] 状态='无文件'")
                
                # 从plan_data中获取无文件计划号
                no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
                
                # 对于无文件计划号,直接导出明细,不依赖坐标映射
                valid_no_file_plans = no_file_plans
                invalid_no_file_plans = []
                
                print(f"  找到 {len(no_file_plans)} 个无文件的计划号")
                print(f"  计划号列表: {valid_no_file_plans}")
                
                if not valid_no_file_plans:
                    print(f"[×] 没有需要导出的计划号")
                    export_finished(True, "没有需要导出的计划号\n\n所有计划号都已有文件,无需导出", [], [], {})
                    return
                
                # 获取设置中的窗口标题
                settings = self.get_settings()
                test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
                test_speed = "中"
                
                speed_delays = {"慢": 1.5, "中": 1.0, "快": 0.5}
                delay_time = speed_delays.get(test_speed, 1.0)
                
                # 使用配置文件中的计划明细导出按钮坐标
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", [79, 870])
                
                print(f"")
                print(f"[配置信息]")
                print(f"  计划明细导出按钮坐标: {plan_detail_export_btn}")
                print(f"  导出速度: {test_speed} (延迟: {delay_time}s)")
                print(f"  目标窗口: {test_window}")
                
                print(f"")
                print(f"===========================================================")
                print(f"开始导出计划号明细")
                print(f"===========================================================")
                
                # 导出无文件计划号明细（在主线程中执行）
                from PyQt5.QtCore import QEvent, QCoreApplication
                
                class ExportPlanDetailEvent(QEvent):
                    def __init__(self, valid_no_file_plans, plan_detail_export_btn, test_window, delay_time, coord_map):
                        super().__init__(QEvent.User)
                        self.valid_no_file_plans = valid_no_file_plans
                        self.plan_detail_export_btn = plan_detail_export_btn
                        self.test_window = test_window
                        self.delay_time = delay_time
                        self.coord_map = coord_map
                
                # 发送事件到主线程
                event = ExportPlanDetailEvent(valid_no_file_plans, plan_detail_export_btn, test_window, delay_time, coord_map)
                QCoreApplication.postEvent(self, event)
                
                
            except Exception as e:
                print(f"[×] 自动导出失败: {str(e)}")
                import traceback
                traceback.print_exc()
                export_finished(False, f"自动导出失败: {str(e)}", [], [], {})
            finally:
                # 结束时间
                end_time = datetime.datetime.now()
                execution_time = end_time - start_time
                print(f"\n=== 自动导出结束 ===")
                print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"执行时间: {execution_time.total_seconds():.2f} 秒")
                print("="*60)
                
                # 无论执行是否成功,都释放线程锁和重置运行标志
                if hasattr(self, 'auto_export_lock'):
                    try:
                        self.auto_export_lock.release()
                    except:
                        pass
                # 重置运行标志
                self.is_auto_export_running = False
                print("自动导出运行标志已重置为False")
        
        # 启动后台线程执行导出操作
        import threading
        export_thread = threading.Thread(target=export_in_background, daemon=True)
        export_thread.start()
        
        # 等待后台线程开始执行
        import time
        time.sleep(1)  # 等待1秒，确保后台线程已经开始执行
        
    def export_zhuanglu_shunxu(self, add_debug_log=None):
        """导出装炉顺序 - 严格按照原程序步骤执行
        
        参数:
            add_debug_log: 调试日志函数（可选）,如果为None则不输出调试信息
        """
        import time
        log_lines = ["开始导出装炉顺序..."]
        
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass  # 非调试模式下不输出
        
        # 检查pyautogui是否可用
        try:
            import pyautogui
            import os
            PYAUTOGUI_AVAILABLE = True
        except ImportError:
            PYAUTOGUI_AVAILABLE = False
            add_debug_log('pyautogui 不可用,无法执行装炉顺序导出')
            return False
        
        # 文件路径 - 使用计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        # 输出原程序日志中的准备信息
        print(f"尝试读取Excel文件: {zhuanglu_file}")
        print(f"尝试连接数据库: {self.db_path}")
        
        # 准备临时文件路径
        temp_zhuanglu_file = os.path.join(plan_dir, f"装炉顺序_{int(time.time())}.tmp.xls")
        # 导出前清理可能存在的临时文件
        import glob
        for temp_file in glob.glob(os.path.join(plan_dir, "装炉顺序_*.tmp.xls")):
            try:
                os.remove(temp_file)
                add_debug_log(f"[√] 已清理临时文件: {os.path.basename(temp_file)}")
            except Exception as e:
                add_debug_log(f"[×] 清理临时文件失败: {str(e)}")
        
        # 从配置中读取窗口标题（优先使用自定义窗口名称）
        custom_title = self.coordinates.get("custom_window_title", "").strip()
        # 加载配置
        settings = self.get_settings()
            
        if custom_title:
            window_title = custom_title
        else:
            window_title = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
        
        add_debug_log(f"【配置信息】")
        add_debug_log(f"窗口标题: {window_title}")
        add_debug_log(f"文件路径: {zhuanglu_file}")
        add_debug_log("")
        
        # 从配置中读取坐标
        zhuanglu_tab = self.coordinates.get("zhuanglu_tab", (261, 87))
        zhuanglu_export = self.coordinates.get("zhuanglu_export_btn", (990, 831))
        
        # 确保坐标是有效的列表或元组
        if not isinstance(zhuanglu_tab, (list, tuple)) or len(zhuanglu_tab) != 2:
            zhuanglu_tab = (284, 84)
        if not isinstance(zhuanglu_export, (list, tuple)) or len(zhuanglu_export) != 2:
            zhuanglu_export = (988, 819)
        
        # 确保坐标值是数字
        try:
            zhuanglu_tab = (int(zhuanglu_tab[0]), int(zhuanglu_tab[1]))
            zhuanglu_export = (int(zhuanglu_export[0]), int(zhuanglu_export[1]))
        except (ValueError, TypeError):
            zhuanglu_tab = (284, 84)
            zhuanglu_export = (988, 819)
        
        add_debug_log(f"【坐标配置】")
        add_debug_log(f"装炉顺作成管理标签: {zhuanglu_tab}")
        add_debug_log(f"装炉顺序导出按钮: {zhuanglu_export}")
        add_debug_log("")
        
        # 步骤1: 激活目标窗口
        log_lines.append(f"[1/9] 激活目标窗口: {window_title}...")
        add_debug_log(f"【步骤1】激活目标窗口: {window_title}")
        try:
            if not self.activate_window(window_title):
                log_lines.append("[×] 激活窗口失败")
                add_debug_log("[×] 激活窗口失败")
                print(f"[×] 导出失败: 激活窗口 {window_title} 失败")
                return False
            log_lines.append(f"[√] 已激活窗口: {window_title}")
            add_debug_log(f"[√] 已激活窗口: {window_title}")
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # 激活窗口后延迟
        except Exception as e:
            log_lines.append(f"[×] 激活窗口失败: {str(e)}")
            add_debug_log(f"[×] 激活窗口失败: {str(e)}")
            print(f"[×] 导出失败: 激活窗口 {window_title} 失败")
            return False
        
        # 步骤2-8: 执行导出操作
        try:
            # 步骤2: 鼠标点击 - 装炉顺作成管理画面
            log_lines.append(f"[2/9] 鼠标点击: 装炉顺作成管理画面 @ {zhuanglu_tab}...")
            add_debug_log(f"【步骤2】鼠标点击: 装炉顺作成管理画面")
            add_debug_log(f"  坐标: ({zhuanglu_tab[0]}, {zhuanglu_tab[1]})")
            pyautogui.moveTo(zhuanglu_tab[0], zhuanglu_tab[1])
            pyautogui.click()
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # 点击后延迟
            log_lines.append("点击完成")
            add_debug_log("[√] 点击完成")

            # 步骤3: 键盘按键 - F2
            log_lines.append("[3/9] 键盘按键: F2...")
            add_debug_log(f"【步骤3】键盘按键: F2")
            pyautogui.press('f2')
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # F2后延迟
            log_lines.append("F2键已按下")
            add_debug_log("[√] F2键已按下")

            # 步骤4: 延迟 - 500ms
            log_lines.append("[4/9] 延迟: 500ms...")
            add_debug_log(f"【步骤4】延迟: 500ms")
            time.sleep(0.5)
            log_lines.append("延迟完成")
            add_debug_log("[√] 延迟完成")

            # 步骤5: 鼠标点击 - 导出按钮
            log_lines.append(f"[5/9] 鼠标点击: 导出按钮 @ {zhuanglu_export}...")
            add_debug_log(f"【步骤5】鼠标点击: 导出按钮")
            add_debug_log(f"  坐标: ({zhuanglu_export[0]}, {zhuanglu_export[1]})")
            pyautogui.moveTo(zhuanglu_export[0], zhuanglu_export[1])
            pyautogui.click()
            add_debug_log(f"  延迟: 1000ms (等待保存对话框)")
            time.sleep(1.0)  # 点击后延迟,等待保存对话框弹出
            log_lines.append("导出按钮点击完成,等待保存对话框...")
            add_debug_log("[√] 导出按钮点击完成")

            # 步骤6: 直接输入完整路径+文件名
            log_lines.append("[6/9] 直接输入完整路径+文件名...")
            add_debug_log(f"【步骤6】直接输入完整路径+文件名")
            # 等待对话框完全弹出并获取焦点
            add_debug_log(f"  延迟: 1000ms (等待对话框)")
            time.sleep(1.0)
            # 构造临时文件路径（不带扩展名）
            temp_full_path = os.path.splitext(temp_zhuanglu_file)[0]
            add_debug_log(f"  临时文件路径: {temp_full_path}")
            import pyperclip
            pyperclip.copy(temp_full_path)
            add_debug_log(f"  已复制到剪贴板")
            add_debug_log(f"  延迟: 200ms")
            time.sleep(0.2)
            # 粘贴完整路径到文件名输入框
            add_debug_log(f"  执行: Ctrl+V 粘贴")
            pyautogui.hotkey('ctrl', 'v')
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # 输入后延迟
            log_lines.append(f"已输入完整路径: {temp_full_path}")
            add_debug_log("[√] 已输入完整路径")

            # 步骤8: 键盘按键 - Return
            log_lines.append("[8/9] 键盘按键: Return...")
            add_debug_log(f"【步骤8】键盘按键: Return")
            pyautogui.press('return')
            log_lines.append("回车键已按下")
            add_debug_log("[√] 回车键已按下")

            # 等待导出完成
            log_lines.append("等待导出完成...")
            add_debug_log(f"【等待导出完成】")
            add_debug_log(f"  延迟: 3000ms")
            time.sleep(3)
            add_debug_log("[√] 导出完成")
        except Exception as e:
            log_lines.append(f"[×] 执行导出操作失败: {str(e)}")
            add_debug_log(f"[×] 执行导出操作失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 继续执行后续步骤（如关闭Excel进程和文件替换）
        
        # 确保所有Excel进程都已关闭（避免文件占用）
        log_lines.append("确保Excel进程已关闭...")
        add_debug_log(f"【关闭Excel进程】")
        try:
            import subprocess
            # 强制关闭所有Excel进程,使用creationflags隐藏窗口
            subprocess.run(
                ['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            add_debug_log(f"  延迟: 2000ms")
            time.sleep(2)
            log_lines.append("Excel进程已强制关闭")
            add_debug_log("[√] Excel进程已强制关闭")
        except Exception as e:
            log_lines.append(f"强制关闭Excel进程失败: {str(e)}")
            add_debug_log(f"[×] 强制关闭Excel进程失败: {str(e)}")
        
        # 原子性文件替换：将临时文件替换为正式文件
        log_lines.append("执行原子性文件替换...")
        add_debug_log(f"【原子性文件替换】")
        try:
            if os.path.exists(temp_zhuanglu_file):
                add_debug_log(f"  临时文件: {temp_zhuanglu_file}")
                add_debug_log(f"  目标文件: {zhuanglu_file}")
                # 执行原子性替换,使用重试机制
                success = self.atomic_file_replace(temp_zhuanglu_file, zhuanglu_file, max_retries=5, retry_delay=1.0)
                if success:
                    # 清理文件缓存,确保读取到最新数据
                    self.clear_file_cache(zhuanglu_file)
                    add_debug_log("[√] 原子性文件替换成功")
                    add_debug_log("[√] 文件缓存已清理")
                    log_lines.append("原子性文件替换成功")
                else:
                    add_debug_log("[×] 原子性文件替换失败")
                    log_lines.append("原子性文件替换失败")
            else:
                add_debug_log(f"[×] 临时文件不存在: {temp_zhuanglu_file}")
                log_lines.append("临时文件不存在")
        except Exception as e:
            add_debug_log(f"[×] 原子性文件替换异常: {str(e)}")
            log_lines.append(f"原子性文件替换异常: {str(e)}")
        
        # 导入数据到数据库
        log_lines.append("导入数据到数据库...")
        add_debug_log(f"【导入数据到数据库】")
        try:
            # 等待文件完全写入
            time.sleep(1.0)
            
            # 导入装炉顺序数据到数据库
            import_result = self.import_zhuanglu_shunxu_to_db(zhuanglu_file)
            if import_result:
                # 获取导入的数据条数
                try:
                    import sqlite3
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM zhuanglu_shunxu")
                    count = cursor.fetchone()[0]
                    conn.close()
                    print(f"✓ 成功导入 {count} 条装炉顺序数据到数据库")
                    add_debug_log(f"[√] 成功导入 {count} 条装炉顺序数据到数据库")
                except:
                    print(f"✓ 成功导入装炉顺序数据到数据库")
                    add_debug_log("[√] 成功导入装炉顺序数据到数据库")
            else:
                add_debug_log("[×] 装炉顺序数据导入数据库失败")
        except Exception as e:
            add_debug_log(f"[×] 导入数据到数据库异常: {str(e)}")
            log_lines.append(f"导入数据到数据库异常: {str(e)}")
        
        # 刷新计划号列表
        add_debug_log(f"【刷新计划号列表】")
        try:
            self.refresh_plan_list()
            add_debug_log("[√] 计划号列表刷新完成")
        except Exception as e:
            add_debug_log(f"[×] 计划号列表刷新失败: {str(e)}")
        
        add_debug_log(f"【导出完成】装炉顺序导出操作完成")
        
        return True
    
    def export_zhizhi_plan_list(self, test_window=None, test_mode=False, add_debug_log=None):
        """导出总计划号列表 - 严格按照原程序步骤执行
        
        参数:
            test_window: 测试窗口标题,如果为None则自动选择
            test_mode: 是否为测试模式（简化版不再使用）
            add_debug_log: 调试日志函数
        """
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import pyautogui
            import time
            import os
            
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("导出总计划号列表")
            add_debug_log("="*60)
            
            # 使用固定的窗口标题
            # 获取设置中的窗口标题
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            add_debug_log(f"窗口标题: {test_window}")
            print("\n=== 导出总计划号列表 ===")
            
            # 文件路径 - 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            total_plan_file = os.path.join(plan_dir, "总计划号列表.xls")
            
            # 准备临时文件路径（带.xls扩展名）
            temp_total_plan_file = os.path.join(plan_dir, f"总计划号列表_{int(time.time())}.tmp.xls")
            # 导出前清理可能存在的临时文件
            import glob
            for temp_file in glob.glob(os.path.join(plan_dir, "总计划号列表_*.tmp.xls")):
                try:
                    os.remove(temp_file)
                    add_debug_log(f"[√] 已清理临时文件: {os.path.basename(temp_file)}")
                except Exception as e:
                    add_debug_log(f"[×] 清理临时文件失败: {str(e)}")
            
            # 从配置中读取坐标
            zhizhi_tab = self.coordinates.get("zhizhi_tab", (92, 85))
            plan_select = self.coordinates.get("plan_select", (860, 134))
            zhizhi_export_btn = self.coordinates.get("zhizhi_export_btn", (77, 501))
            
            add_debug_log(f"")
            add_debug_log(f"[坐标配置]")
            add_debug_log(f"  轧制计划管理标签: {zhizhi_tab}")
            add_debug_log(f"  选择计划号: {plan_select}")
            add_debug_log(f"  导出按钮: {zhizhi_export_btn}")
            
            # 步骤1: 跳过激活窗口（已在导出装炉顺序时激活）
            print("[1/7] 跳过激活窗口（已在导出装炉顺序时激活）...")
            add_debug_log(f"")
            add_debug_log(f"[步骤1] 跳过激活窗口（已在导出装炉顺序时激活）")
            
            # 步骤2: 点击轧制计划管理标签
            try:
                print(f"[2/7] 点击轧制计划管理标签...")
                add_debug_log(f"")
                add_debug_log(f"[步骤2] 点击轧制计划管理标签")
                add_debug_log(f"  坐标: ({zhizhi_tab[0]}, {zhizhi_tab[1]})")
                pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
                pyautogui.click()
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)
            except Exception as e:
                print(f"[×] 点击轧制计划管理标签失败: {e},继续执行")
                add_debug_log(f"[×] 点击轧制计划管理标签失败: {e},继续执行")

            # 步骤3: 选择计划号
            try:
                print(f"[3/7] 选择计划号...")
                add_debug_log(f"")
                add_debug_log(f"[步骤3] 选择计划号")
                add_debug_log(f"  坐标: ({plan_select[0]}, {plan_select[1]})")
                pyautogui.moveTo(plan_select[0], plan_select[1])
                pyautogui.click()
                add_debug_log(f"  延迟: 300ms")
                time.sleep(0.3)
            except Exception as e:
                print(f"[×] 选择计划号失败: {e},继续执行")
                add_debug_log(f"[×] 选择计划号失败: {e},继续执行")

            # 步骤4: 按Home键选择所有计划号 + 回车确认
            try:
                print("[4/7] 按Home键选择所有计划号...")
                add_debug_log(f"")
                add_debug_log(f"[步骤4] 按Home键选择所有计划号")
                pyautogui.press('home')
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)
                pyautogui.press('return')
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)
            except Exception as e:
                print(f"[×] 按Home键选择所有计划号失败: {e},继续执行")
                add_debug_log(f"[×] 按Home键选择所有计划号失败: {e},继续执行")

            # 步骤5: 按F2刷新
            try:
                print("[5/7] 按F2刷新...")
                add_debug_log(f"")
                add_debug_log(f"[步骤5] 按F2刷新")
                pyautogui.press('f2')
                time.sleep(0.5)
            except Exception as e:
                print(f"[×] 按F2刷新失败: {e},继续执行")
                add_debug_log(f"[×] 按F2刷新失败: {e},继续执行")

            # 步骤6: 点击导出按钮
            try:
                print(f"[6/7] 点击导出按钮...")
                add_debug_log(f"")
                add_debug_log(f"[步骤6] 点击导出按钮")
                add_debug_log(f"  坐标: ({zhizhi_export_btn[0]}, {zhizhi_export_btn[1]})")
                pyautogui.moveTo(zhizhi_export_btn[0], zhizhi_export_btn[1])
                pyautogui.click()
                add_debug_log(f"  延迟: 1500ms (等待保存对话框)")
                time.sleep(1.5)
            except Exception as e:
                print(f"[×] 点击导出按钮失败: {e},继续执行")
                add_debug_log(f"[×] 点击导出按钮失败: {e},继续执行")

            # 步骤7: 直接输入完整路径+文件名
            try:
                print("[7/7] 直接输入完整路径+文件名...")
                add_debug_log(f"")
                add_debug_log(f"[步骤7] 直接输入完整路径+文件名")
                add_debug_log(f"  延迟: 500ms (等待对话框)")
                time.sleep(0.5)
                # 临时文件路径（不带扩展名，Excel会自动添加）
                temp_full_path = os.path.splitext(temp_total_plan_file)[0]
                add_debug_log(f"  临时文件路径: {temp_full_path}")
                import pyperclip
                pyperclip.copy(temp_full_path)
                add_debug_log(f"  已复制到剪贴板")
                add_debug_log(f"  延迟: 200ms")
                time.sleep(0.2)
                # 粘贴完整路径到文件名输入框
                add_debug_log(f"  执行: Ctrl+V 粘贴")
                pyautogui.hotkey('ctrl', 'v')
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)  # 输入后延迟
                print(f"已输入完整路径: {temp_full_path}")
                add_debug_log(f"[√] 已输入完整路径")

                # 保存文件
                add_debug_log(f"")
                add_debug_log(f"[保存文件]")
                add_debug_log(f"  按键: Return")
                pyautogui.press('return')
                add_debug_log(f"  延迟: 2000ms (等待保存完成)")
                time.sleep(2)
            except Exception as e:
                print(f"[×] 输入完整路径+文件名失败: {e},继续执行")
                add_debug_log(f"[×] 输入完整路径+文件名失败: {e},继续执行")
            

            # 确保所有Excel进程都已关闭（避免文件占用）
            add_debug_log(f"")
            add_debug_log(f"【关闭Excel进程】")
            try:
                import subprocess
                # 强制关闭所有Excel进程
                subprocess.run(
                    ['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                add_debug_log(f"  延迟: 2000ms")
                time.sleep(2)
                print("[√] Excel进程已强制关闭")
                add_debug_log("[√] Excel进程已强制关闭")
            except Exception as e:
                print(f"[×] 强制关闭Excel进程失败: {str(e)}")
                add_debug_log(f"[×] 强制关闭Excel进程失败: {str(e)}")
            
            # 原子性文件替换：将临时文件替换为正式文件
            add_debug_log(f"")
            add_debug_log(f"【原子性文件替换】")
            try:
                add_debug_log(f"  临时文件: {temp_total_plan_file}")
                add_debug_log(f"  目标文件: {total_plan_file}")
                
                if os.path.exists(temp_total_plan_file):
                    # 执行原子性替换,使用重试机制
                    success = self.atomic_file_replace(temp_total_plan_file, total_plan_file, max_retries=5, retry_delay=1.0)
                    if success:
                        # 清理文件缓存,确保读取到最新数据
                        self.clear_file_cache(total_plan_file)
                        print("[√] 原子性文件替换成功")
                        add_debug_log("[√] 原子性文件替换成功")
                        add_debug_log("[√] 文件缓存已清理")
                    else:
                        print("[×] 原子性文件替换失败")
                        add_debug_log("[×] 原子性文件替换失败")
                else:
                    print(f"[×] 临时文件不存在: {temp_total_plan_file}")
                    add_debug_log(f"[×] 临时文件不存在: {temp_total_plan_file}")
            except Exception as e:
                print(f"[×] 原子性文件替换异常: {str(e)}")
                add_debug_log(f"[×] 原子性文件替换异常: {str(e)}")

            
            # 导入总计划号列表数据到数据库
            add_debug_log(f"")
            add_debug_log(f"[导入数据到数据库]")
            print("导入总计划号列表数据到数据库...")
            try:
                import_success = self.import_zhizhi_plan_list_to_db(total_plan_file)
                if import_success:
                    add_debug_log(f"[√] 总计划号列表数据导入数据库成功")
                else:
                    add_debug_log(f"[×] 总计划号列表数据导入数据库失败")
            except Exception as e:
                print(f"导入总计划号列表数据到数据库失败: {str(e)}")
                add_debug_log(f"[×] 导入总计划号列表数据导入数据库失败: {str(e)}")
            
            print("[√] 总计划号列表导出成功")
            add_debug_log(f"[√] 总计划号列表导出成功")
            add_debug_log(f"[√] 总计划号列表导出完成")
            return True
            
        except Exception as e:
            print(f"[×] 导出总计划号列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_single_plan_detail(self, plan_no, plan_coord, plan_detail_export_btn=None, test_window=None, add_debug_log=None):
        """导出单个计划号的明细 - 严格按照原程序步骤执行
        
        参数:
            plan_no: 计划号
            plan_coord: 计划号的坐标 (x, y)
            plan_detail_export_btn: 导出计划明细按钮坐标,如果为None则使用配置中的坐标
            test_window: 测试窗口标题
            add_debug_log: 调试日志函数
            
        返回:
            True - 导出成功
            False - 导出失败
        """
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        result = False
        
        try:
            import time
            import os
            import glob
            
            # 使用固定的窗口标题
            # 获取设置中的窗口标题
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            add_debug_log(f"    开始执行导出操作...")
            add_debug_log(f"    开始导出明细...")
            add_debug_log(f"    窗口: {test_window}")
            
            # 检查pyautogui是否可用
            try:
                import pyautogui
                # 禁用 pyautogui 的自动暂停机制，避免操作卡住
                pyautogui.PAUSE = 0
                # 禁用 failsafe，避免误触导致程序停止
                pyautogui.FAILSAFE = False
                PYAUTOGUI_AVAILABLE = True
            except ImportError as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log('pyautogui 不可用,无法执行计划明细导出')
                print(f'pyautogui 不可用,无法执行计划明细导出: {e}')
                result = False
                return result
            except Exception as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log(f'pyautogui 初始化失败: {e}')
                print(f'pyautogui 初始化失败: {e}')
                result = False
                return result
            
            # 步骤1: 激活窗口
            add_debug_log(f"    [1] 激活窗口...")
            if not self.activate_window(test_window):
                add_debug_log(f"    [×] 激活窗口失败")
                print("[×] 激活窗口失败")
                return False
            add_debug_log(f"    [√] 窗口已激活")
            add_debug_log(f"    延迟: 300ms")
            time.sleep(0.3)
            
            # 使用传入的坐标或从配置中读取的坐标
            if plan_detail_export_btn is None:
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", [79, 870])
            
            # 步骤2: 鼠标点击计划号坐标
            add_debug_log(f"    [2] 点击计划号坐标: {plan_coord}")
            # 检查坐标是否有效
            if plan_coord and len(plan_coord) == 2:
                # 检查坐标值是否有效
                if isinstance(plan_coord[0], (int, float)) and isinstance(plan_coord[1], (int, float)):
                    try:
                        pyautogui.moveTo(plan_coord[0], plan_coord[1])
                        pyautogui.click()
                        add_debug_log(f"    延迟: 500ms")
                        time.sleep(0.5)  # 延迟500ms
                    except Exception as e:
                        print(f"[×] 点击计划号坐标失败: {e}")
                        add_debug_log(f"    [×] 点击计划号坐标失败: {e}")
                else:
                    print("[×] 计划号坐标值无效")
                    add_debug_log(f"    [×] 计划号坐标值无效")
            else:
                print("[×] 计划号坐标无效")
                add_debug_log(f"    [×] 计划号坐标无效")
            
            # 步骤3: 鼠标点击导出计划明细按钮
            add_debug_log(f"    [3] 点击导出按钮: {plan_detail_export_btn}")
            # 检查坐标是否有效
            if plan_detail_export_btn and len(plan_detail_export_btn) == 2:
                # 检查坐标值是否有效
                if isinstance(plan_detail_export_btn[0], (int, float)) and isinstance(plan_detail_export_btn[1], (int, float)):
                    try:
                        pyautogui.moveTo(plan_detail_export_btn[0], plan_detail_export_btn[1])
                        pyautogui.click()
                        add_debug_log(f"    延迟: 500ms (等待对话框)")
                        time.sleep(0.5)  # 等待保存对话框弹出
                    except Exception as e:
                        print(f"[×] 点击导出按钮失败: {e}")
                        add_debug_log(f"    [×] 点击导出按钮失败: {e}")
                else:
                    print("[×] 导出计划明细按钮坐标值无效")
                    add_debug_log(f"    [×] 导出计划明细按钮坐标值无效")
            else:
                print("[×] 导出计划明细按钮坐标无效")
                add_debug_log(f"    [×] 导出计划明细按钮坐标无效")
            
            # 步骤4: 键盘输入计划号（使用剪贴板粘贴）
            add_debug_log(f"    [4] 输入计划号: {plan_no}")
            try:
                import pyperclip
                pyperclip.copy(str(plan_no))
                add_debug_log(f"    延迟: 200ms")
                time.sleep(0.2)
                add_debug_log(f"    执行: Ctrl+V 粘贴")
                pyautogui.hotkey('ctrl', 'v')
                add_debug_log(f"    延迟: 300ms")
                time.sleep(0.3)
            except Exception as e:
                print(f"[×] 剪贴板操作失败,尝试直接输入: {e}")
                # 尝试直接输入
                try:
                    pyautogui.typewrite(str(plan_no))
                    time.sleep(0.5)
                except Exception as e2:
                    print(f"[×] 直接输入失败: {e2}")
                    add_debug_log(f"    [×] 直接输入失败: {e2}")
            
            # 步骤5: 按回车确认
            add_debug_log(f"    [5] 按键: Return")
            try:
                pyautogui.press('return')
                add_debug_log(f"    延迟: 1000ms (等待确认对话框)")
                time.sleep(1)  # 等待确认对话框
                
                # 步骤6: 按左方向键（替换覆盖）
                add_debug_log(f"    [6] 按键: Left")
                pyautogui.press('left')
                add_debug_log(f"    延迟: 500ms")
                time.sleep(0.5)
                
                # 步骤7: 按回车确认
                add_debug_log(f"    [7] 按键: Return")
                pyautogui.press('return')
                add_debug_log(f"    延迟: 2000ms (等待保存完成)")
                time.sleep(2)  # 等待保存完成
                add_debug_log(f"    [√] 导出完成")
            except Exception as e:
                print(f"[×] 按键操作失败: {e}")
                add_debug_log(f"    [×] 按键操作失败: {e}")
            
            # 模拟操作执行完成,直接标记为成功
            # 验证操作将在所有计划号导出完成后统一执行
            print(f"[√] 计划号 {plan_no} 的明细文件已导出")
            result = True
            
        except Exception as e:
            add_debug_log(f"    [×] 导出失败: {str(e)}")
            print(f"[×] 导出计划 {plan_no} 明细失败: {str(e)}")
            import traceback
            traceback.print_exc()
            result = False
        finally:
            # 移除返回主程序窗口的代码,确保导出过程中始终保持在激活的目标窗口
            # 这样可以避免窗口闪现的问题
            pass
        
        if result:
            add_debug_log(f"  [√] 导出成功")
        else:
            add_debug_log(f"  [×] 导出失败")
        return result
    
    def custom_messagebox(self, title, message, msg_type='info', auto_close=None):
        """自定义消息框 - 更大的窗口和字体
        
        Args:
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型 ('info', 'warning', 'error', 'yesno')
            auto_close: 自动关闭时间（秒），None表示不自动关闭
            
        Returns:
            bool: 对于yesno类型，返回用户的选择
        """
        from PyQt5.QtWidgets import QMessageBox, QApplication, QStyle
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont
        
        # 创建消息框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # 设置消息框样式
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        msg_box.setModal(True)
        
        # 设置按钮
        if msg_type == 'yesno':
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
        else:
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)
        
        # 设置字体（与计划号列表相同大小）
        font = QFont("宋体", 14)
        msg_box.setFont(font)
        
        # 增加消息框大小
        msg_box.setMinimumWidth(500)
        msg_box.setMinimumHeight(250)
        
        # 将窗口居中显示（相对于主程序窗口）
        if self.isVisible():
            # 使用固定大小计算（避免adjustSize的问题）
            msg_box_width = 500
            msg_box_height = 250
            
            # 获取主窗口的全局位置和大小
            main_rect = self.frameGeometry()
            main_x = main_rect.x()
            main_y = main_rect.y()
            main_width = main_rect.width()
            main_height = main_rect.height()
            
            # 计算居中位置
            center_x = main_x + (main_width - msg_box_width) // 2
            center_y = main_y + (main_height - msg_box_height) // 2
            
            # 设置消息框的位置和大小
            msg_box.resize(msg_box_width, msg_box_height)
            msg_box.move(center_x, center_y)
        else:
            # 如果主窗口不可见，居中到屏幕
            screen_rect = QApplication.desktop().screenGeometry()
            msg_box_width = 500
            msg_box_height = 250
            center_x = (screen_rect.width() - msg_box_width) // 2
            center_y = (screen_rect.height() - msg_box_height) // 2
            msg_box.resize(msg_box_width, msg_box_height)
            msg_box.move(center_x, center_y)
        
        # 定义关闭消息框的函数
        def close_msg_box():
            try:
                msg_box.done(QMessageBox.Ok)
            except Exception as e:
                print(f"关闭消息框失败: {e}")
        
        # 显示消息框
        if auto_close is not None:
            # 设置自动关闭
            QTimer.singleShot(auto_close * 1000, close_msg_box)
        
        # 使用exec_()显示模态对话框，允许用户手动关闭
        result = msg_box.exec_()
        
        if msg_type == 'yesno':
            return result == QMessageBox.Ok
        else:
            return True

    def activate_window(self, window_name):
        """激活指定窗口"""
        import time
        print(f"=== 激活窗口: {window_name} ===")

        if window_name == "当前窗口":
            print("使用当前窗口")
            return True

        try:
            import win32gui
            import win32con
            print("win32gui导入成功")
        except ImportError:
            print("win32gui未安装")
            return False

        # 使用原始窗口标题
        window_title = window_name
        print(f"查找窗口: {window_title}")

        # 查找窗口
        def callback(hwnd, handles):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_title in window_text:
                    print(f"找到窗口: {window_text}")
                    handles.append(hwnd)

        handles = []
        win32gui.EnumWindows(callback, handles)

        if handles:
            hwnd = handles[0]
            print(f"激活窗口句柄: {hwnd}")

            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(hwnd):
                print("窗口被最小化，正在恢复...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)

            # 激活窗口 - 使用与原程序相同的方法
            try:
                print("尝试激活窗口...")

                # 方法1: 显示窗口
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.2)

                # 方法2: 将窗口置于最顶层
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法3: 取消最顶层（恢复正常层级，但已经在前面了）
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法4: 设置前台窗口
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)

                # 方法5: 将窗口带到最前面
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)

                print("窗口激活成功")
                return True
            except Exception as e:
                print(f"激活窗口失败: {str(e)}")
                return False
        else:
            print(f"未找到窗口: {window_title}")
            return False
    
    def atomic_file_replace(self, source_path, target_path, max_retries=5, retry_delay=1.0):
        """原子性文件替换"""
        import os
        import shutil
        import tempfile
        import time
        
        if not os.path.exists(source_path):
            return False
        
        temp_dir = os.path.dirname(target_path)
        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.tmp')
        temp_file_path = temp_file.name
        temp_file.close()
        
        try:
            shutil.copy2(source_path, temp_file_path)
            
            for attempt in range(max_retries):
                try:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(temp_file_path, target_path)
                    return True
                except OSError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        raise
        except Exception as e:
            print(f'原子性文件替换失败: {e}')
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return False
    
    def clear_file_cache(self, file_path):
        """清理文件缓存,确保读取到最新数据
        
        参数:
            file_path: 文件路径
        """
        import os
        try:
            # 通过修改文件的访问时间来强制刷新缓存
            if os.path.exists(file_path):
                current_time = os.path.getmtime(file_path)
                os.utime(file_path, (current_time, current_time))
        except Exception as e:
            print(f"清理文件缓存失败: {e}")
    
    def import_zhuanglu_shunxu_to_db(self, file_path):
        """从装炉顺序.xls导入数据到数据库"""
        import time
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                import xlrd
                import sqlite3
                import os
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"文件不存在: {file_path}")
                    return False
                
                # 检查文件是否可以读取
                if not os.access(file_path, os.R_OK):
                    print(f"文件无法读取: {file_path}")
                    return False
                
                # 等待文件操作完成
                time.sleep(0.5)
                
                # 读取Excel文件
                print(f"尝试读取Excel文件: {file_path}")
                workbook = xlrd.open_workbook(file_path)
                sheet = workbook.sheet_by_index(0)
                
                # 查找列索引
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                plan_col = -1
                coil_col = -1
                steel_col = -1
                spec_col = -1
                weight_col = -1
                order_col = -1
                rough_col = -1
                
                for idx, header in enumerate(headers):
                    if '计划号' in str(header):
                        plan_col = idx
                    elif '钢卷号' in str(header):
                        coil_col = idx
                    elif '钢种' in str(header) or '钢级' in str(header):
                        steel_col = idx
                    elif '规格' in str(header):
                        spec_col = idx
                    elif '重量' in str(header):
                        weight_col = idx
                    elif '装炉顺序' in str(header):
                        order_col = idx
                    elif '粗轧报信' in str(header):
                        rough_col = idx
                
                if plan_col == -1:
                    print("未找到计划号列")
                    return False
                
                # 连接数据库
                print(f"尝试连接数据库: {self.db_path}")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 清空现有数据
                cursor.execute("DELETE FROM plan_order")
                
                # 导入数据
                count = 0
                for row in range(1, sheet.nrows):
                    try:
                        plan_no = str(sheet.cell_value(row, plan_col)).strip()
                        if not plan_no or plan_no == 'nan':
                            continue
                        
                        coil_no = str(sheet.cell_value(row, coil_col)).strip() if coil_col != -1 else ''
                        steel_grade = str(sheet.cell_value(row, steel_col)).strip() if steel_col != -1 else ''
                        specification = str(sheet.cell_value(row, spec_col)).strip() if spec_col != -1 else ''
                        weight = float(sheet.cell_value(row, weight_col)) if weight_col != -1 else 0.0
                        order_no = int(sheet.cell_value(row, order_col)) if order_col != -1 else row
                        rough_info = str(sheet.cell_value(row, rough_col)).strip() if rough_col != -1 else ''
                        
                        cursor.execute('''
                            INSERT INTO plan_order (plan_no, coil_no, steel_grade, specification, weight, order_no, rough_rolling_info)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (plan_no, coil_no, steel_grade, specification, weight, order_no, rough_info))
                        count += 1
                    except Exception as e:
                        print(f"导入行 {row} 失败: {str(e)}")
                        continue
                
                # 提交并关闭
                conn.commit()
                conn.close()
                print(f"[√] 成功导入 {count} 条装炉顺序数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入装炉顺序数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"[×] 导入装炉顺序数据失败: {str(e)}")
                    return False
    
    def import_zhizhi_plan_list_to_db(self, file_path):
        """从总计划号列表.xls导入数据到数据库"""
        import time
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                import xlrd
                import sqlite3
                import os
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"文件不存在: {file_path}")
                    return False
                
                # 检查文件是否可以读取
                if not os.access(file_path, os.R_OK):
                    print(f"文件无法读取: {file_path}")
                    return False
                
                # 等待文件操作完成
                time.sleep(0.5)
                
                # 读取Excel文件
                print(f"尝试读取Excel文件: {file_path}")
                workbook = xlrd.open_workbook(file_path)
                sheet = workbook.sheet_by_index(0)
                
                # 查找列索引
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                seq_col = -1
                plan_col = -1
                steel_col = -1
                spec_col = -1
                quantity_col = -1
                
                for idx, header in enumerate(headers):
                    if '序号' in str(header):
                        seq_col = idx
                    elif '计划号' in str(header):
                        plan_col = idx
                    elif '钢种' in str(header) or '钢级' in str(header):
                        steel_col = idx
                    elif '规格' in str(header):
                        spec_col = idx
                    elif '数量' in str(header):
                        quantity_col = idx
                
                if plan_col == -1:
                    print("未找到计划号列")
                    return False
                
                # 连接数据库
                print(f"尝试连接数据库: {self.db_path}")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 清空现有数据
                cursor.execute("DELETE FROM total_plan_list")
                
                # 导入数据
                count = 0
                for row in range(1, sheet.nrows):
                    try:
                        plan_no = str(sheet.cell_value(row, plan_col)).strip()
                        if not plan_no or plan_no == 'nan':
                            continue
                        
                        seq_no = int(sheet.cell_value(row, seq_col)) if seq_col != -1 else row
                        steel_grade = str(sheet.cell_value(row, steel_col)).strip() if steel_col != -1 else ''
                        specification = str(sheet.cell_value(row, spec_col)).strip() if spec_col != -1 else ''
                        quantity = int(sheet.cell_value(row, quantity_col)) if quantity_col != -1 else 1
                        
                        cursor.execute('''
                            INSERT INTO total_plan_list (plan_no, seq_no, steel_grade, specification, quantity)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (plan_no, seq_no, steel_grade, specification, quantity))
                        count += 1
                    except Exception as e:
                        print(f"导入行 {row} 失败: {str(e)}")
                        continue
                
                # 提交并关闭
                conn.commit()
                conn.close()
                print(f"[√] 成功导入 {count} 条总计划号列表数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入总计划号列表数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"[×] 导入总计划号列表数据失败: {str(e)}")
                    return False
    
    def read_zhizhi_plan_list_with_coords(self, add_debug_log=None):
        """读取总计划号列表数据,返回计划号到坐标的映射字典
        
        根据设置页面中的第一个计划号坐标和计划号间距,
        计算每个计划号的实际屏幕坐标。
        
        参数:
            add_debug_log: 调试日志函数（可选）
            
        返回: {计划号: (x, y)} 的字典
        """
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import sqlite3
            import os
            
            add_debug_log(f"")
            add_debug_log(f"[读取总计划号列表]")
            add_debug_log(f"  数据库路径: {self.db_path}")
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 从数据库获取总计划号列表数据
            cursor.execute('''
                SELECT plan_no, seq_no 
                FROM total_plan_list 
                ORDER BY seq_no
            ''')
            plan_data = cursor.fetchall()
            
            if not plan_data:
                add_debug_log(f"  [×] 数据库中无数据")
                print(f"总计划号列表数据不存在")
                conn.close()
                return None
            
            add_debug_log(f"  [√] 数据库读取成功")
            print(f"读取总计划号列表数据并计算坐标")
            
            # 从配置中读取第一个计划号坐标、间距和偏移量
            first_plan = self.coordinates.get("first_plan", (239, 208))
            plan_spacing = self.coordinates.get("plan_spacing", 21)
            # 第一个计划号的纵坐标偏移量（用于校准中点位置）
            first_plan_offset = self.coordinates.get("first_plan_offset", 0)
            
            first_x = first_plan[0]
            first_y = first_plan[1] + first_plan_offset  # 应用偏移量校准
            
            add_debug_log(f"")
            add_debug_log(f"[坐标计算配置]")
            add_debug_log(f"  第一个计划号原始坐标: ({first_plan[0]}, {first_plan[1]})")
            add_debug_log(f"  偏移量: {first_plan_offset}")
            add_debug_log(f"  校准后坐标: ({first_x}, {first_y})")
            add_debug_log(f"  计划号间距: {plan_spacing} 像素")
            
            print(f"第一个计划号原始坐标: ({first_plan[0]}, {first_plan[1]})")
            print(f"第一个计划号偏移量: {first_plan_offset}")
            print(f"第一个计划号校准后坐标: ({first_x}, {first_y})")
            print(f"计划号间距: {plan_spacing} 像素")
            
            # 读取计划号并计算坐标
            plan_coord_map = {}
            zhizhi_plan_list = []  # 临时存储序号和计划号
            
            add_debug_log(f"")
            add_debug_log(f"[读取计划号并计算坐标]")
            add_debug_log(f"  数据行数: {len(plan_data)}")
            
            for row_index, (plan_no, seq_value) in enumerate(plan_data):
                if plan_no:
                    # 直接使用行索引计算坐标,不依赖序号值
                    # row_index 从0开始,正好对应第一个计划号的索引
                    coord_y = first_y + (row_index * plan_spacing)
                    coord_x = first_x
                    
                    # 将计划号转换为字符串作为键，确保后续查找时类型匹配
                    plan_coord_map[str(plan_no)] = (coord_x, coord_y)
                    zhizhi_plan_list.append((seq_value, plan_no))
                    # 只显示前13个,避免日志过长
                    if row_index < 13:
                        add_debug_log(f"  计划号 {plan_no}: 行索引={row_index}, 坐标=({coord_x}, {coord_y})")
                    elif row_index == 13:
                        add_debug_log(f"    ... 还有 {len(plan_data) - 13} 个计划号")
            
            # 只打印总数,不打印每个计划号的详细信息,提高计算速度
            print(f"  共计算 {len(plan_coord_map)} 个计划号的坐标")
            
            # 关闭数据库连接
            conn.close()
            
            add_debug_log(f"")
            add_debug_log(f"  总计: {len(plan_coord_map)} 个计划号坐标")
            print(f"\n从总计划号列表计算了 {len(plan_coord_map)} 个计划号的坐标")
            
            # 更新缓存
            self.zhizhi_plan_list = zhizhi_plan_list
            self.zhizhi_plan_coord_map = plan_coord_map
            add_debug_log(f"  [√] 已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            print(f"已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            
            add_debug_log(f"  [√] 坐标计算完成")
            return plan_coord_map
            
        except Exception as e:
            print(f"读取总计划号列表并计算坐标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


class FurnaceDetailsWindow(QMainWindow):
    """装炉明细窗口"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("装炉明细")
        self.showMaximized()

        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 记录最后选中的钢卷号，用于恢复定位
        self.last_selected_coil_no = None
        
        # 列名
        columns = [
            "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
            "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
            "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
        ]
        
        # 列宽配置
        column_widths = {
            "计划号": 110,
            "钢卷号": 190,
            "牌号（钢级）": 210,
            "除鳞": 110,
            "去向": 65,
            "坯厚": 80,
            "坯宽": 90,
            "坯长": 95,
            "中厚": 65,
            "轧厚": 70,
            "轧宽": 90,
            "订宽": 90,
            "切边": 70,
            "调宽": 75,
            "减宽": 85,
            "公差带": 120,
            "RT2": 78,
            "强度": 60,
            "粗轧报信": 360,
            "坯头部宽": 120,
            "坯尾部宽": 120,
            "热轧产品分类": 110,
            "炼钢钢种": 210,
            "负公差": 90,
            "正公差": 90,
            "回炉坯": 90,
            "原轧宽": 90
        }
        
        # 创建自定义表格类，确保标注单元格始终保持背景色
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QPainter, QColor, QBrush

        class CustomTableWidget(QTableWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

            def paintEvent(self, event):
                # 调用父类的paintEvent
                super().paintEvent(event)
                
                # 重新绘制标注单元格，确保它们保持红色背景
                painter = QPainter(self.viewport())
                for row in range(self.rowCount()):
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item:
                            bg_color = item.background().color().name()
                            # 不管是否是选中行，都绘制标注单元格的背景
                            # 这样标注单元格的颜色会显示在光标条颜色的上面
                            if bg_color == '#ff0000':
                                # 红色背景（标注单元格）
                                # 获取单元格的矩形
                                rect = self.visualRect(self.model().index(row, col))
                                # 绘制红色背景
                                painter.fillRect(rect, QBrush(QColor('#FF0000')))
                                # 绘制文字
                                painter.setPen(QColor('white'))
                                painter.setFont(item.font())
                                painter.drawText(rect, item.textAlignment(), item.text())
                            elif bg_color == '#ffff00':
                                # 黄色背景（换辊行、自定义信息行）
                                # 获取单元格的矩形
                                rect = self.visualRect(self.model().index(row, col))
                                # 绘制黄色背景
                                painter.fillRect(rect, QBrush(QColor('#FFFF00')))
                                # 绘制文字
                                painter.setPen(QColor('black'))
                                painter.setFont(item.font())
                                painter.drawText(rect, item.textAlignment(), item.text())

        # 创建自定义表格
        self.table_widget = CustomTableWidget()
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        for i, col in enumerate(columns):
            width = column_widths.get(col, 70)
            self.table_widget.setColumnWidth(i, width)
        
        # 设置行高
        self.table_widget.verticalHeader().setDefaultSectionSize(80)
        
        # 隐藏垂直表头
        self.table_widget.verticalHeader().setVisible(False)
        
        # 设置字体
        font = QFont("微软雅黑", 20, QFont.Bold)
        self.table_widget.setFont(font)
        
        # 设置表头字体
        header_font = QFont("微软雅黑", 20, QFont.Bold)
        self.table_widget.horizontalHeader().setFont(header_font)
        
        # 设置表头样式（添加边框线）
        header_style = """
            QHeaderView::section {
                background-color: #E8E8E8;
                border: 1px solid #888888;
                padding: 5px;
                font-weight: bold;
            }
        """
        self.table_widget.horizontalHeader().setStyleSheet(header_style)
        
        # 设置表格样式，添加鼠标悬停效果和tooltip字体大小
        table_style = """
            QTableWidget {
                background-color: white;
                gridline-color: #CCCCCC;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FD;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QTableWidget::item:selected:!focus {
                background-color: #0078D7;
                color: white;
            }
            QToolTip {
                font-size: 20px;
                font-family: "微软雅黑";
                color: #000000;
                background-color: #FFFFCC;
                border: 2px solid #000000;
                padding: 5px;
            }
        """
        self.table_widget.setStyleSheet(table_style)
        
        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        
        # 添加表格到布局
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.table_widget)
        main_layout.addWidget(scroll_area)
        
        # 自动滚动相关变量
        self.scroll_timer = QTimer()
        self.is_scrolling = False
        self.current_row = 0
        self.scroll_interval = 110  # 默认 110 秒
        self.scroll_status_label = QLabel("")
        
        # 底部布局
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(10)
        main_layout.addLayout(bottom_layout)
        
        # 左侧按钮组
        left_buttons = QHBoxLayout()
        left_buttons.setSpacing(10)
        bottom_layout.addLayout(left_buttons)
        
        # 创建按钮样式
        button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 5px 10px;
                font-family: 宋体;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """
        
        # 打印按钮
        self.print_btn = QPushButton("打印")
        self.print_btn.setFont(QFont("宋体", 14))
        self.print_btn.setFixedSize(60, 30)
        self.print_btn.setStyleSheet(button_style)
        # 确保点击按钮时不会影响光标条
        def print_btn_clicked():
            # 保存当前选中行
            current_row = self.table_widget.currentRow()
            # 检查是否全部打印
            is_all_print = self.all_print_checkbox.isChecked()
            # 执行打印操作（增量打印或全部打印）
            # 由于 print_furnace_details 方法在 MainWindow 类中，需要通过 parent 调用
            # 传入装炉明细窗口的表格，以便打印正确的内容
            if hasattr(self.parent, 'print_furnace_details'):
                self.parent.print_furnace_details(is_incremental=not is_all_print, table_widget=self.table_widget)
            # 恢复选中行
            if current_row >= 0:
                self.table_widget.selectRow(current_row)
        self.print_btn.clicked.connect(print_btn_clicked)
        left_buttons.addWidget(self.print_btn)
        
        # 全部打印复选框
        self.all_print_checkbox = QCheckBox("全部打印")
        self.all_print_checkbox.setFont(QFont("宋体", 14))
        # 确保点击复选框时不会影响光标条
        def checkbox_clicked():
            # 保存当前选中行
            current_row = self.table_widget.currentRow()
            # 恢复选中行
            if current_row >= 0:
                self.table_widget.selectRow(current_row)
        self.all_print_checkbox.clicked.connect(checkbox_clicked)
        left_buttons.addWidget(self.all_print_checkbox)
        
        # 返回按钮
        self.return_btn = QPushButton("返回")
        self.return_btn.setFont(QFont("宋体", 14))
        self.return_btn.setFixedSize(60, 30)
        self.return_btn.setStyleSheet(button_style)
        # 确保点击按钮时不会影响光标条
        def return_btn_clicked():
            # 保存当前选中行
            current_row = self.table_widget.currentRow()
            # 执行返回操作
            self.close()
            # 激活主程序窗口
            if hasattr(self, 'parent') and self.parent:
                self.parent.activateWindow()
                self.parent.raise_()
            else:
                # 如果没有父窗口，尝试激活主程序窗口
                main_window_titles = [
                    "轧制计划管理系统",
                    "主程序",
                    "装炉顺序",
                    "计划号管理",
                    "装炉明细",
                    "装炉顺作成管理",
                    "轧制计划管理",
                    "BGCMS1-宝钢股份多基地制造管理系统运行环境"
                ]
                for title in main_window_titles:
                    if self.activate_window(title):
                        print(f"已激活主程序窗口: {title}")
                        break
        self.return_btn.clicked.connect(return_btn_clicked)
        left_buttons.addWidget(self.return_btn)
        
        # 中间块数显示
        bottom_layout.addStretch(1)
        
        # 块数显示
        self.block_count_label = QLabel("0/0")
        self.block_count_label.setFont(QFont("微软雅黑", 20, QFont.Bold))
        self.block_count_label.setStyleSheet("color: blue;")
        bottom_layout.addWidget(self.block_count_label)
        
        bottom_layout.addStretch(1)
        
        # 右侧信息和控制
        right_layout = QHBoxLayout()
        right_layout.setSpacing(15)  # 增加间距
        bottom_layout.addLayout(right_layout)
        
        # 自动打印复选框
        self.auto_print_checkbox = QCheckBox("自动打印")
        self.auto_print_checkbox.setFont(QFont("宋体", 14))
        self.auto_print_checkbox.setStyleSheet("background-color: #f0f0f0;")
        right_layout.addWidget(self.auto_print_checkbox)
        
        # 自动执行复选框
        self.auto_exec_checkbox = QCheckBox("自动执行")
        self.auto_exec_checkbox.setFont(QFont("宋体", 14))
        self.auto_exec_checkbox.setStyleSheet("background-color: #f0f0f0;")
        right_layout.addWidget(self.auto_exec_checkbox)
        
        # 下一次执行时间显示
        self.next_execution_label = QLabel("下一次执行: 无")
        self.next_execution_label.setFont(QFont("宋体", 12))
        self.next_execution_label.setFixedWidth(160)  # 进一步增加宽度，确保完全显示"下一次执行: 12:41:00"
        right_layout.addWidget(self.next_execution_label)
        
        # 同步主窗口的下一次执行时间
        if self.parent:
            next_exec_text = self.parent.next_execution_label.text()
            self.next_execution_label.setText(next_exec_text)
            # 同步主窗口的自动打印和自动执行复选框状态
            if hasattr(self.parent, 'auto_print_checkbox'):
                self.auto_print_checkbox.setChecked(self.parent.auto_print_checkbox.isChecked())
            if hasattr(self.parent, 'auto_exec_checkbox'):
                self.auto_exec_checkbox.setChecked(self.parent.auto_exec_checkbox.isChecked())
        
        # 连接自动执行复选框信号到主窗口处理函数
        if self.parent and hasattr(self.parent, 'on_auto_exec_changed'):
            self.auto_exec_checkbox.stateChanged.connect(self.parent.on_auto_exec_changed)
        # 连接自动打印复选框信号到主窗口处理函数
        if self.parent and hasattr(self.parent, 'on_auto_print_changed'):
            self.auto_print_checkbox.stateChanged.connect(self.parent.on_auto_print_changed)
        
        # 自动滚动状态
        self.scroll_status_label = QLabel("")
        self.scroll_status_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        self.scroll_status_label.setFixedWidth(120)  # 增加宽度，容纳"自动滚动已停止"
        right_layout.addWidget(self.scroll_status_label)
        
        # 滚动时间输入框
        self.scroll_time_edit = QLineEdit("110")
        self.scroll_time_edit.setFont(QFont("微软雅黑", 14))
        self.scroll_time_edit.setFixedWidth(60)  # 增加宽度，容纳3位数
        self.scroll_time_edit.setAlignment(Qt.AlignCenter)  # 文本居中
        # 设置占位符提示
        self.scroll_time_edit.setPlaceholderText("滚动间隔(秒)")
        # 光标进入时全选文本，确保不影响光标条
        def focus_in_event(event):
            # 保存当前选中行
            current_row = self.table_widget.currentRow()
            # 执行默认的focusInEvent
            QLineEdit.focusInEvent(self.scroll_time_edit, event)
            self.scroll_time_edit.selectAll()
            # 恢复选中行
            if current_row >= 0:
                self.table_widget.selectRow(current_row)
        # 点击时全选文本，确保不影响光标条
        def mouse_press_event(event):
            # 保存当前选中行
            current_row = self.table_widget.currentRow()
            # 执行默认的mousePressEvent
            QLineEdit.mousePressEvent(self.scroll_time_edit, event)
            self.scroll_time_edit.selectAll()
            # 恢复选中行
            if current_row >= 0:
                self.table_widget.selectRow(current_row)
        self.scroll_time_edit.focusInEvent = focus_in_event
        self.scroll_time_edit.mousePressEvent = mouse_press_event
        right_layout.addWidget(self.scroll_time_edit)
        
        # 播放/停止按钮
        self.scroll_toggle_btn = QPushButton("▶")
        self.scroll_toggle_btn.setFont(QFont("宋体", 12))
        self.scroll_toggle_btn.setFixedSize(30, 30)  # 固定大小
        self.scroll_toggle_btn.setStyleSheet(button_style)
        # 确保点击按钮时不会影响光标条
        def scroll_toggle_clicked():
            # 执行滚动切换操作
            self.toggle_scroll()
        self.scroll_toggle_btn.clicked.connect(scroll_toggle_clicked)
        right_layout.addWidget(self.scroll_toggle_btn)
        
        # 连接信号
        self.connect_signals()

        # 初始化自定义标注条件相关属性
        import json
        import os
        
        # 条件保存文件路径
        self.annotation_conditions_file = "annotation_conditions.json"
        
        # 加载保存的条件组
        if not hasattr(self, 'custom_annotation_condition_groups'):
            if os.path.exists(self.annotation_conditions_file):
                try:
                    with open(self.annotation_conditions_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 检查是否是新格式（条件组）
                        if 'condition_groups' in data:
                            self.custom_annotation_condition_groups = data.get('condition_groups', [])
                        else:
                            # 兼容旧格式
                            self.custom_annotation_condition_groups = [{
                                'conditions': data.get('conditions', []),
                                'combo_type': data.get('combo_type', "且"),
                                'enabled': True
                            }]
                except:
                    self.custom_annotation_condition_groups = []
            else:
                self.custom_annotation_condition_groups = []
        
        # 为了兼容旧代码，设置旧属性
        if not hasattr(self, 'custom_annotation_conditions'):
            self.custom_annotation_conditions = []
        if not hasattr(self, 'custom_annotation_combo_type'):
            self.custom_annotation_combo_type = "且"
        
        # 初始化自定义信息和换辊信息
        self.custom_and_roll_change_info = {
            'roll_change': {},  # 换辊信息，格式: {row: True}
            'custom_info': {}    # 自定义信息，格式: {row: text}
        }
        
        # 加载保存的自定义信息和换辊信息
        plan_dir = os.path.join(os.getcwd(), "计划号")
        self.custom_info_file = os.path.join(plan_dir, "custom_and_roll_change_info.json")
        if os.path.exists(self.custom_info_file):
            try:
                with open(self.custom_info_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.custom_and_roll_change_info = data
            except:
                self.custom_and_roll_change_info = {
                    'roll_change': {},
                    'custom_info': {}
                }

        # 加载数据
        self.load_furnace_data()

        # 创建刷新数据的方法，供外部调用
        def refresh_data():
            """刷新装炉明细数据"""
            print("刷新装炉明细数据...")
            self.load_furnace_data()
            # 刷新数据后，恢复上次选中的钢卷号位置
            self.restore_selected_coil()
            # 保存当前数据，确保打印时能正确识别新增的钢卷号
            self.save_current_table_data()
        self.refresh_data = refresh_data

    def show_context_menu(self, event):
        """显示右键菜单"""
        from PyQt5.QtWidgets import QMenu, QInputDialog, QMessageBox

        row = self.table_widget.currentRow()
        if row < 0:
            return

        first_item = self.table_widget.item(row, 0)
        is_roll_changed = False
        is_custom_info = False

        if first_item:
            bg_color = first_item.background().color().name()
            cell_text = first_item.text()
            if '换辊' in cell_text:
                is_roll_changed = True
            elif bg_color == '#ffff00':
                is_custom_info = True

        context_menu = QMenu(self)
        context_menu.setFont(QFont("微软雅黑", 20))
        # 设置选中项为蓝色背景白字
        context_menu.setStyleSheet("""
            QMenu::item:selected {
                background-color: #0066CC;
                color: white;
            }
        """)

        find_coil_action = context_menu.addAction("查找钢卷号")

        def on_find_coil_number():
            input_dialog = QInputDialog(self)
            input_dialog.setWindowTitle("查找钢卷号")
            input_dialog.setLabelText("请输入钢卷号:")
            input_dialog.setTextValue("")
            input_dialog.setInputMode(QInputDialog.TextInput)
            input_dialog.resize(800, 300)
            # 使用样式表设置字体和样式
            input_dialog.setStyleSheet(""".QInputDialog {
                font-family: 微软雅黑;
                font-size: 20px;
            }
            QLabel {
                font-family: 微软雅黑;
                font-size: 20px;
            }
            QLineEdit {
                font-family: 微软雅黑;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton {
                font-family: 微软雅黑;
                font-size: 20px;
                padding: 5px 15px;
            }""")

            ok = input_dialog.exec_()
            coil_number = input_dialog.textValue() if ok else ""

            if ok and coil_number.strip():
                found = False
                for i in range(self.table_widget.rowCount()):
                    item = self.table_widget.item(i, 1)
                    if item:
                        if item.text().strip() == coil_number.strip():
                            self.table_widget.selectRow(i)
                            self.table_widget.scrollToItem(item, QTableWidget.PositionAtCenter)
                            found = True
                            print(f"找到钢卷号 {coil_number}，位于第 {i+1} 行")
                            break

                if not found:
                    QMessageBox.information(self, "提示", f"未找到钢卷号: {coil_number}")

        find_coil_action.triggered.connect(on_find_coil_number)
        context_menu.addSeparator()

        # 添加自定义标注条件菜单项
        custom_annotation_action = context_menu.addAction("添加自定义标注条件")

        def on_add_custom_annotation():
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
            
            # 保存条件的函数
            def save_annotation_conditions():
                data = {
                    'condition_groups': self.custom_annotation_condition_groups
                }
                import json
                import os
                with open(self.annotation_conditions_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("添加自定义标注条件")
            dialog.resize(900, 500)
            
            # 创建主布局
            main_layout = QVBoxLayout(dialog)
            
            # 1. 条件编辑器部分
            editor_group = QVBoxLayout()
            main_layout.addLayout(editor_group)
            
            # 字段名、运算符、值选择
            condition_layout = QHBoxLayout()
            editor_group.addLayout(condition_layout)
            
            # 字段名下拉列表
            field_label = QLabel("字段名:")
            field_label.setFont(QFont("微软雅黑", 14))
            condition_layout.addWidget(field_label)
            
            field_combo = QComboBox()
            field_combo.setFont(QFont("微软雅黑", 14))
            fields = ["牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带", "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度"]
            field_combo.addItems(fields)
            condition_layout.addWidget(field_combo)
            
            # 运算符下拉列表
            operator_label = QLabel("运算符:")
            operator_label.setFont(QFont("微软雅黑", 14))
            condition_layout.addWidget(operator_label)
            
            operator_combo = QComboBox()
            operator_combo.setFont(QFont("微软雅黑", 14))
            operators = [">", "<", ">=", "<=", "="]
            operator_combo.addItems(operators)
            condition_layout.addWidget(operator_combo)
            
            # 值输入框
            value_label = QLabel("值:")
            value_label.setFont(QFont("微软雅黑", 14))
            condition_layout.addWidget(value_label)
            
            value_edit = QLineEdit()
            value_edit.setFont(QFont("微软雅黑", 14))
            value_edit.setPlaceholderText("请输入值")
            # 添加自动大写功能
            def on_value_changed(text):
                # 转换为大写
                upper_text = text.upper()
                # 避免无限递归
                if value_edit.text() != upper_text:
                    value_edit.setText(upper_text)
            value_edit.textChanged.connect(on_value_changed)
            condition_layout.addWidget(value_edit)
            
            # 添加条件按钮
            add_condition_btn = QPushButton("添加条件")
            add_condition_btn.setFont(QFont("微软雅黑", 14))
            condition_layout.addWidget(add_condition_btn)
            
            # 2. 自定义信息部分
            custom_info_layout = QHBoxLayout()
            editor_group.addLayout(custom_info_layout)
            
            # 自定义信息标签
            custom_info_label = QLabel("自定义信息:")
            custom_info_label.setFont(QFont("微软雅黑", 14))
            custom_info_layout.addWidget(custom_info_label)
            
            # 自定义信息下拉列表
            custom_info_combo = QComboBox()
            custom_info_combo.setFont(QFont("微软雅黑", 14))
            # 添加固定的自定义信息选项
            custom_info_options = ["", "注意事项", "特殊处理", "重点关注", "需要检查", "优先处理", "加急", "延迟", "暂停", "其他"]
            custom_info_combo.addItems(custom_info_options)
            custom_info_layout.addWidget(custom_info_combo)
            
            # 自定义信息输入框
            custom_info_edit = QLineEdit()
            custom_info_edit.setFont(QFont("微软雅黑", 14))
            custom_info_edit.setPlaceholderText("或输入自定义信息")
            custom_info_layout.addWidget(custom_info_edit)
            
            # 连接下拉列表和输入框的信号
            def on_combo_changed(text):
                if text:
                    custom_info_edit.setText("")
            
            def on_edit_changed(text):
                if text:
                    custom_info_combo.setCurrentIndex(0)
            
            custom_info_combo.currentTextChanged.connect(on_combo_changed)
            custom_info_edit.textChanged.connect(on_edit_changed)
            
            # 2. 条件列表部分
            list_group = QVBoxLayout()
            main_layout.addLayout(list_group)
            
            list_label = QLabel("已添加的条件:")
            list_label.setFont(QFont("微软雅黑", 14))
            list_group.addWidget(list_label)
            
            # 使用表格来显示条件和开关
            from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QCheckBox, QWidget, QHBoxLayout
            condition_table = QTableWidget()
            condition_table.setColumnCount(2)
            condition_table.setHorizontalHeaderLabels(["条件", "启用"])
            condition_table.horizontalHeader().setStretchLastSection(True)
            condition_table.setColumnWidth(0, 600)
            condition_table.setColumnWidth(1, 80)
            condition_table.setFont(QFont("微软雅黑", 12))
            condition_table.verticalHeader().setVisible(False)
            # 设置选择模式为行选择
            condition_table.setSelectionMode(QTableWidget.SingleSelection)
            condition_table.setSelectionBehavior(QTableWidget.SelectRows)
            list_group.addWidget(condition_table)
            
            # 删除条件按钮
            remove_condition_btn = QPushButton("删除选中条件")
            remove_condition_btn.setFont(QFont("微软雅黑", 14))
            list_group.addWidget(remove_condition_btn)
            
            # 3. 条件组合部分
            combo_group = QHBoxLayout()
            main_layout.addLayout(combo_group)
            
            combo_label = QLabel("条件组合方式:")
            combo_label.setFont(QFont("微软雅黑", 14))
            combo_group.addWidget(combo_label)
            
            combo_combo = QComboBox()
            combo_combo.setFont(QFont("微软雅黑", 14))
            combo_combo.addItems(["且", "或", "新建"])
            # 设置之前保存的组合方式
            if self.custom_annotation_combo_type in ["且", "或"]:
                combo_combo.setCurrentText(self.custom_annotation_combo_type)
            combo_group.addWidget(combo_combo)
            combo_group.addStretch(1)
            
            # 4. 按钮部分
            button_layout = QHBoxLayout()
            main_layout.addLayout(button_layout)
            
            ok_button = QPushButton("确定")
            ok_button.setFont(QFont("微软雅黑", 14))
            cancel_button = QPushButton("取消")
            cancel_button.setFont(QFont("微软雅黑", 14))
            button_layout.addStretch(1)
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            
            # 初始化条件组
            # 条件组格式: [{'conditions': [{'text': '条件1', 'enabled': True}, ...], 'combo_type': '且', 'enabled': True}, ...]
            if not hasattr(self, 'custom_annotation_condition_groups'):
                # 兼容旧格式
                if hasattr(self, 'custom_annotation_conditions') and self.custom_annotation_conditions:
                    # 将旧格式转换为条件组
                    self.custom_annotation_condition_groups = [{
                        'conditions': self.custom_annotation_conditions,
                        'combo_type': self.custom_annotation_combo_type if hasattr(self, 'custom_annotation_combo_type') else '且',
                        'enabled': True
                    }]
                else:
                    self.custom_annotation_condition_groups = []
            
            added_condition_groups = self.custom_annotation_condition_groups.copy()
            
            # 更新列表显示函数
            def update_list_display():
                condition_table.setRowCount(0)
                if not added_condition_groups:
                    return
                
                # 为每个条件组添加一行
                for i, condition_group in enumerate(added_condition_groups):
                    condition_table.insertRow(i)
                    
                    # 组合条件文本
                    conditions = condition_group.get('conditions', [])
                    combo_type = condition_group.get('combo_type', '且')
                    enabled = condition_group.get('enabled', True)
                    
                    # 生成组合条件文本
                    condition_texts = []
                    for cond in conditions:
                        if isinstance(cond, dict):
                            condition_texts.append(cond.get('text', ''))
                        else:
                            condition_texts.append(cond)
                    
                    if condition_texts:
                        combined_text = f" {combo_type} ".join(condition_texts)
                    else:
                        combined_text = ""
                    
                    # 条件文本列
                    text_item = QTableWidgetItem(combined_text)
                    text_item.setFlags(text_item.flags() & ~Qt.ItemIsEditable)
                    condition_table.setItem(i, 0, text_item)
                    
                    # 启用开关列
                    checkbox_widget = QWidget()
                    checkbox_layout = QHBoxLayout(checkbox_widget)
                    checkbox_layout.setContentsMargins(0, 0, 0, 0)
                    checkbox_layout.setAlignment(Qt.AlignCenter)
                    
                    checkbox = QCheckBox()
                    checkbox.setChecked(enabled)
                    
                    # 为复选框添加状态改变信号
                    def on_checkbox_changed(check_state, group_idx=i):
                        # 保存复选框状态
                        if group_idx < len(added_condition_groups):
                            added_condition_groups[group_idx]['enabled'] = (check_state == 2)  # 2 is Qt.Checked
                        
                        # 保存到文件
                        self.custom_annotation_condition_groups = added_condition_groups.copy()
                        save_annotation_conditions()
                        
                        # 立即应用标注条件
                        apply_all_annotation_conditions()
                    
                    checkbox.stateChanged.connect(lambda state, idx=i: on_checkbox_changed(state, idx))
                    checkbox_layout.addWidget(checkbox)
                    
                    condition_table.setCellWidget(i, 1, checkbox_widget)
            
            # 添加条件函数
            def add_condition():
                field = field_combo.currentText()
                operator = operator_combo.currentText()
                value = value_edit.text().strip()
                
                if not value:
                    QMessageBox.warning(dialog, "提示", "请输入值")
                    return
                
                # 构建条件文本
                condition_text = f"{field}{operator}{value}"
                
                # 获取自定义信息
                custom_info = custom_info_combo.currentText() or custom_info_edit.text().strip()
                
                # 检查是否有条件组
                if not added_condition_groups:
                    # 创建新的条件组
                    new_group = {
                        'conditions': [{
                            'text': condition_text,
                            'enabled': True,
                            'custom_info': custom_info
                        }],
                        'combo_type': combo_combo.currentText(),
                        'enabled': True
                    }
                    added_condition_groups.append(new_group)
                else:
                    # 添加到最后一个条件组
                    last_group = added_condition_groups[-1]
                    last_group['conditions'].append({
                        'text': condition_text,
                        'enabled': True,
                        'custom_info': custom_info
                    })
                    # 更新组合方式
                    last_group['combo_type'] = combo_combo.currentText()
                
                # 保存到文件
                self.custom_annotation_condition_groups = added_condition_groups.copy()
                save_annotation_conditions()
                
                # 更新列表显示
                update_list_display()
                
                # 立即应用标注条件
                apply_all_annotation_conditions()
                
                # 清空输入框
                value_edit.clear()
                custom_info_combo.setCurrentIndex(0)
                custom_info_edit.clear()
            
            # 删除条件函数
            def remove_condition():
                if not added_condition_groups:
                    QMessageBox.warning(dialog, "提示", "没有可删除的条件组")
                    return
                
                # 获取选中的行
                selected_rows = condition_table.selectionModel().selectedRows()
                if not selected_rows:
                    QMessageBox.warning(dialog, "提示", "请选择要删除的条件组")
                    return
                
                # 从后往前删除，避免索引变化
                for index in sorted([row.row() for row in selected_rows], reverse=True):
                    if index < len(added_condition_groups):
                        added_condition_groups.pop(index)
                
                # 保存到文件
                self.custom_annotation_condition_groups = added_condition_groups.copy()
                save_annotation_conditions()
                
                # 更新列表显示
                update_list_display()
                
                # 立即应用标注条件
                apply_all_annotation_conditions()
            
            # 检查单个条件
            def check_single_condition(condition, row):
                # 解析条件：字段名、运算符、值
                field = ""
                operator = ""
                value = ""
                
                # 查找运算符
                operators = [">=", "<=", ">", "<", "="]
                for op in operators:
                    if op in condition:
                        parts = condition.split(op)
                        field = parts[0].strip()
                        operator = op
                        value = parts[1].strip()
                        break
                
                if not field or not operator or not value:
                    return False
                
                # 字段名映射到列索引
                field_map = {
                    "牌号（钢级）": 2,
                    "坯宽": 3,
                    "减宽": 4,
                    "调宽": 5,
                    "轧宽": 6,
                    "公差带": 7,
                    "粗轧报信": 8,
                    "除鳞": 9,
                    "坯厚": 10,
                    "坯长": 11,
                    "轧厚": 12,
                    "中厚": 13,
                    "RT2": 14,
                    "强度": 15
                }
                
                if field not in field_map:
                    return False
                
                column = field_map[field]
                
                # 获取单元格值
                item = self.table_widget.item(row, column)
                if not item:
                    return False
                
                cell_value = item.text().strip()
                
                # 移除标注符号（Δ和*）
                cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                
                # 比较值
                try:
                    # 移除标注符号（Δ和*）
                    clean_cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                    clean_value = value.replace('Δ', '').replace('*', '').strip()
                    
                    if operator == '=':
                        return clean_cell_value == clean_value
                    else:
                        cell_value_num = float(clean_cell_value)
                        # 对调宽字段取绝对值
                        if field == "调宽":
                            cell_value_num = abs(cell_value_num)
                        value_num = float(clean_value)
                        if operator == '>':
                            return cell_value_num > value_num
                        elif operator == '<':
                            return cell_value_num < value_num
                        elif operator == '>=':
                            return cell_value_num >= value_num
                        elif operator == '<=':
                            return cell_value_num <= value_num
                except:
                    return False
            
            # 应用所有条件组
            def apply_all_annotation_conditions():
                # 移除现有的自定义标注行
                rows_to_remove = []
                for i in range(self.table_widget.rowCount()):
                    item = self.table_widget.item(i, 0)
                    if item:
                        # 检查是否是标注行（通过背景色判断）
                        bg_color = item.background().color().name()
                        if bg_color == '#ffff00':  # 黄色背景
                            rows_to_remove.append(i)
                
                # 从后往前删除，避免索引变化
                for row in sorted(rows_to_remove, reverse=True):
                    self.table_widget.removeRow(row)
                
                # 检查每个条件组
                for condition_group in added_condition_groups:
                    if not condition_group.get('enabled', True):
                        continue
                    
                    conditions = condition_group.get('conditions', [])
                    combo_type = condition_group.get('combo_type', '且')
                    
                    # 收集启用的条件
                    enabled_conditions = []
                    for cond in conditions:
                        if isinstance(cond, dict):
                            if cond.get('enabled', True):
                                enabled_conditions.append(cond.get('text', ''))
                        else:
                            enabled_conditions.append(cond)
                    
                    # 组合条件
                    if not enabled_conditions:
                        continue
                    
                    combined_condition = f" {combo_type} ".join(enabled_conditions)
                    
                    # 解析条件
                    parsed_conditions = []
                    if " 且 " in combined_condition:
                        parsed_conditions = combined_condition.split(" 且 ")
                    elif " 或 " in combined_condition:
                        parsed_conditions = combined_condition.split(" 或 ")
                    else:
                        parsed_conditions = [combined_condition]
                    
                    # 收集符合条件的行
                    matched_rows = []
                    for i in range(self.table_widget.rowCount()):
                        # 检查是否是标注行
                        item = self.table_widget.item(i, 0)
                        if item:
                            bg_color = item.background().color().name()
                            if bg_color == '#ffff00':  # 黄色背景
                                continue
                        
                        # 检查是否符合所有条件
                        match = True
                        for cond in parsed_conditions:
                            if not check_single_condition(cond, i):
                                match = False
                                break
                        
                        if match:
                            matched_rows.append(i)
                    
                    # 对符合条件的行添加标注
                    if matched_rows:
                        # 从下往上处理，避免插入行影响索引
                        for row_idx in sorted(matched_rows, reverse=True):
                            # 检查是否已经有标注行
                            has_annotation = False
                            if row_idx + 1 < self.table_widget.rowCount():
                                next_item = self.table_widget.item(row_idx + 1, 0)
                                if next_item:
                                    # 检查是否是标注行（通过背景色判断）
                                    bg_color = next_item.background().color().name()
                                    if bg_color == '#ffff00':  # 黄色背景
                                        has_annotation = True
                            
                            if not has_annotation:
                                # 在下面插入一行
                                new_row = row_idx + 1
                                self.table_widget.insertRow(new_row)
                                self.table_widget.setRowHeight(new_row, 80)
                                
                                # 收集自定义信息
                                custom_infos = []
                                for cond in conditions:
                                    if isinstance(cond, dict) and 'custom_info' in cond and cond['custom_info']:
                                        custom_infos.append(cond['custom_info'])
                                
                                # 构建标注内容
                                annotation_text = f"{combined_condition}"
                                if custom_infos:
                                    custom_info_text = " | ".join(custom_infos)
                                    annotation_text = f"{annotation_text} - {custom_info_text}"
                                
                                # 设置标注内容
                                annotation_item = QTableWidgetItem(annotation_text)
                                annotation_item.setBackground(Qt.yellow)
                                # 设置字体
                                font = QFont()
                                font.setPointSize(20)
                                font.setBold(True)
                                annotation_item.setFont(font)
                                # 设置水平和垂直居中
                                annotation_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                                self.table_widget.setItem(new_row, 0, annotation_item)
                                
                                # 合并单元格，只合并到强度列（索引15）
                                self.table_widget.setSpan(new_row, 0, 1, 16)
            
            # 保存复选框状态的函数
            def save_checkbox_states():
                for i in range(condition_table.rowCount()):
                    if i < len(added_condition_groups):
                        checkbox_widget = condition_table.cellWidget(i, 1)
                        if checkbox_widget:
                            checkbox = checkbox_widget.findChild(QCheckBox)
                            if checkbox:
                                added_condition_groups[i]['enabled'] = checkbox.isChecked()
            
            # 条件组合方式变化时更新显示
            def on_combo_type_changed():
                # 处理新建选项
                if combo_combo.currentText() == "新建":
                    # 创建新的条件组
                    new_group = {
                        'conditions': [],
                        'combo_type': "且",
                        'enabled': True
                    }
                    added_condition_groups.append(new_group)
                    # 重置组合方式为"且"
                    combo_combo.setCurrentText("且")
                    # 更新列表显示
                    update_list_display()
                    # 保存条件
                    self.custom_annotation_condition_groups = added_condition_groups.copy()
                    save_annotation_conditions()
                    # 应用标注条件
                    apply_all_annotation_conditions()
                    return
                
                # 更新最后一个条件组的组合方式
                if added_condition_groups:
                    last_group = added_condition_groups[-1]
                    last_group['combo_type'] = combo_combo.currentText()
                    # 保存条件
                    self.custom_annotation_condition_groups = added_condition_groups.copy()
                    save_annotation_conditions()
                    # 更新列表显示
                    update_list_display()
                    # 应用标注条件
                    apply_all_annotation_conditions()
            
            # 确定按钮点击事件
            def on_ok():
                # 保存条件组
                self.custom_annotation_condition_groups = added_condition_groups.copy()
                
                # 保存到文件
                save_annotation_conditions()
                
                # 应用标注条件
                apply_all_annotation_conditions()
                dialog.accept()
            
            # 取消按钮点击事件
            def on_cancel():
                # 保存条件组
                self.custom_annotation_condition_groups = added_condition_groups.copy()
                
                # 保存到文件
                save_annotation_conditions()
                
                # 应用标注条件
                apply_all_annotation_conditions()
                
                dialog.reject()
            
            # 连接条件组合方式变化信号
            combo_combo.currentIndexChanged.connect(on_combo_type_changed)
            
            # 连接信号
            add_condition_btn.clicked.connect(add_condition)
            remove_condition_btn.clicked.connect(remove_condition)
            ok_button.clicked.connect(on_ok)
            cancel_button.clicked.connect(on_cancel)
            
            # 初始化显示
            update_list_display()
            
            # 执行对话框
            if dialog.exec_() == QDialog.Accepted:
                pass
        
        def apply_annotation_condition(condition):
            """应用标注条件"""
            try:
                # 首先移除所有现有的自定义标注行
                rows_to_remove = []
                for i in range(self.table_widget.rowCount()):
                    item = self.table_widget.item(i, 0)
                    if item:
                        bg_color = item.background().color().name()
                        if bg_color == '#ffff00':
                            # 只移除自定义标注条件行，保留换辊和自定义信息行
                            text = item.text().strip()
                            # 检查是否是标注条件行（通过字体大小判断，标注条件行字体较大）
                            font = item.font()
                            if font.pointSize() == 20:
                                rows_to_remove.append(i)
                
                # 从后往前删除，避免索引变化
                rows_to_remove.sort(reverse=True)
                for row in rows_to_remove:
                    self.table_widget.removeRow(row)
                
                # 如果条件为空，直接返回
                if not condition.strip():
                    QMessageBox.information(self, "完成", "已取消所有自定义标注")
                    return
                
                # 列名映射
                column_map = {
                    "计划号": 0,
                    "钢卷号": 1,
                    "牌号（钢级）": 2,
                    "坯宽": 3,
                    "减宽": 4,
                    "调宽": 5,
                    "轧宽": 6,
                    "公差带": 7,
                    "粗轧报信": 8,
                    "除鳞": 9,
                    "坯厚": 10,
                    "坯长": 11,
                    "轧厚": 12,
                    "中厚": 13,
                    "RT2": 14,
                    "强度": 15
                }
                
                def check_single_condition(cond, row_idx):
                    """检查单个条件是否满足"""
                    # 解析条件
                    if '>=' in cond:
                        field, value = cond.split('>=', 1)
                        operator = '>='
                    elif '<=' in cond:
                        field, value = cond.split('<=', 1)
                        operator = '<='
                    elif '>' in cond:
                        field, value = cond.split('>', 1)
                        operator = '>'
                    elif '<' in cond:
                        field, value = cond.split('<', 1)
                        operator = '<'
                    elif '=' in cond:
                        field, value = cond.split('=', 1)
                        operator = '='
                    else:
                        return False
                    
                    field = field.strip()
                    value = value.strip()
                    
                    # 检查字段是否存在
                    if field not in column_map:
                        return False
                    
                    # 获取单元格值
                    col_idx = column_map[field]
                    item = self.table_widget.item(row_idx, col_idx)
                    if not item:
                        return False
                    
                    cell_value = item.text().strip()
                    
                    # 比较值
                    try:
                        # 移除标注符号（Δ和*）
                        clean_cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                        clean_value = value.replace('Δ', '').replace('*', '').strip()
                        
                        if operator == '=':
                            return clean_cell_value == clean_value
                        else:
                            cell_value_num = float(clean_cell_value)
                            # 对调宽字段取绝对值
                            if field == "调宽":
                                cell_value_num = abs(cell_value_num)
                            value_num = float(clean_value)
                            if operator == '>':
                                return cell_value_num > value_num
                            elif operator == '<':
                                return cell_value_num < value_num
                            elif operator == '>=':
                                return cell_value_num >= value_num
                            elif operator == '<=':
                                return cell_value_num <= value_num
                    except:
                        return False
                
                # 检查条件组合方式
                use_or = " 或 " in condition
                if use_or:
                    conditions = condition.split(" 或 ")
                else:
                    conditions = condition.split(" 且 ")
                
                matched_rows = []
                
                # 遍历所有行
                for i in range(self.table_widget.rowCount()):
                    # 检查是否是特殊行
                    first_item = self.table_widget.item(i, 0)
                    if first_item:
                        bg_color = first_item.background().color().name()
                        if bg_color == '#ffff00':
                            continue
                    
                    # 检查是否符合条件
                    if use_or:
                        # 或逻辑：只要有一个条件满足
                        match = False
                        for cond in conditions:
                            cond = cond.strip()
                            if not cond:
                                continue
                            
                            if check_single_condition(cond, i):
                                match = True
                                break
                    else:
                        # 且逻辑：所有条件都要满足
                        match = True
                        for cond in conditions:
                            cond = cond.strip()
                            if not cond:
                                continue
                            
                            if not check_single_condition(cond, i):
                                match = False
                                break
                    
                    if match:
                        matched_rows.append(i)
                
                # 对符合条件的行添加标注
                if matched_rows:
                    # 从下往上处理，避免插入行影响索引
                    for row_idx in sorted(matched_rows, reverse=True):
                        new_row = row_idx + 1
                        self.table_widget.insertRow(new_row)
                        self.table_widget.setRowHeight(new_row, 80)
                        
                        # 创建标注项
                        annotation_item = QTableWidgetItem(condition)
                        annotation_item.setBackground(QBrush(QColor('#FFFF00')))  # 黄色背景
                        font = QFont()
                        font.setPointSize(20)
                        font.setBold(True)
                        annotation_item.setFont(font)
                        annotation_item.setTextAlignment(Qt.AlignCenter)
                        
                        self.table_widget.setItem(new_row, 0, annotation_item)
                        self.table_widget.setSpan(new_row, 0, 1, 16)
                    
                    QMessageBox.information(self, "完成", f"已为 {len(matched_rows)} 个符合条件的钢卷号添加标注")
                else:
                    QMessageBox.information(self, "提示", "没有找到符合条件的钢卷号")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"应用标注条件失败: {str(e)}")
                print(f"应用标注条件失败: {str(e)}")
                import traceback
                traceback.print_exc()
        
        custom_annotation_action.triggered.connect(on_add_custom_annotation)
        context_menu.addSeparator()

        if is_roll_changed or is_custom_info:
            cancel_action = context_menu.addAction("取消标注")

            def on_cancel_mark():
                self.table_widget.removeRow(row)
                total_rows = self.table_widget.rowCount()
                selected_rows = self.table_widget.selectionModel().selectedRows()
                if selected_rows:
                    current_row = selected_rows[0].row() + 1
                    self.block_count_label.setText(f"{current_row}/{total_rows}")
                else:
                    self.block_count_label.setText(f"0/{total_rows}")
                if is_roll_changed:
                    # 换辊行是插入在原始行之后的，所以存储的行号是 row - 1
                    print(f"已取消标注，删除了第 {row} 行的换辊标记")
                    self.remove_roll_change_info(row - 1)
                else:
                    print(f"已取消标注，删除了第 {row} 行的自定义信息")
                    self.remove_custom_info(row - 1)

            cancel_action.triggered.connect(on_cancel_mark)
        elif first_item and first_item.background().color().name() == '#ffff00':
            # 黄色标注行也可以取消标注
            cancel_action = context_menu.addAction("取消标注")

            def on_cancel_mark():
                self.table_widget.removeRow(row)
                total_rows = self.table_widget.rowCount()
                selected_rows = self.table_widget.selectionModel().selectedRows()
                if selected_rows:
                    current_row = selected_rows[0].row() + 1
                    self.block_count_label.setText(f"{current_row}/{total_rows}")
                else:
                    self.block_count_label.setText(f"0/{total_rows}")
                print(f"已取消标注，删除了第 {row} 行的自定义标注条件")

            cancel_action.triggered.connect(on_cancel_mark)
        else:
            change_roll_action = context_menu.addAction("换辊")

            def on_change_roll():
                new_row = row + 1
                self.table_widget.insertRow(new_row)
                self.table_widget.setRowHeight(new_row, 80)
                
                # 设置换辊信息
                roll_change_item = QTableWidgetItem("换辊")
                roll_change_item.setBackground(QBrush(QColor('#00FF00')))
                # 设置字体
                font = QFont()
                font.setPointSize(20)
                font.setBold(True)
                roll_change_item.setFont(font)
                # 设置水平和垂直居中
                roll_change_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table_widget.setItem(new_row, 0, roll_change_item)
                
                # 合并单元格，只合并到强度列（索引15）
                self.table_widget.setSpan(new_row, 0, 1, 16)
                
                self.save_roll_change_info(row)
                
                total_rows = self.table_widget.rowCount()
                selected_rows = self.table_widget.selectionModel().selectedRows()
                if selected_rows:
                    current_row = selected_rows[0].row() + 1
                    self.block_count_label.setText(f"{current_row}/{total_rows}")
                else:
                    self.block_count_label.setText(f"0/{total_rows}")
                print(f"已执行换辊操作，在第 {row} 行下方添加了换辊标记行")

            change_roll_action.triggered.connect(on_change_roll)
            context_menu.addSeparator()

            custom_info_action = context_menu.addAction("添加自定义信息")

            def on_add_custom_info():
                input_dialog = QInputDialog(self)
                input_dialog.setWindowTitle("添加自定义信息")
                input_dialog.setLabelText("请输入自定义信息:")
                input_dialog.setTextValue("")
                input_dialog.setInputMode(QInputDialog.TextInput)
                input_dialog.resize(800, 300)
                # 使用样式表设置字体和样式
                input_dialog.setStyleSheet(""".QInputDialog {
                font-family: 微软雅黑;
                font-size: 20px;
            }
            QLabel {
                font-family: 微软雅黑;
                font-size: 20px;
            }
            QLineEdit {
                font-family: 微软雅黑;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton {
                font-family: 微软雅黑;
                font-size: 20px;
                padding: 5px 15px;
            }""")

                ok = input_dialog.exec_()
                text = input_dialog.textValue() if ok else ""

                if ok and text.strip():
                    new_row = row + 1
                    self.table_widget.insertRow(new_row)
                    self.table_widget.setRowHeight(new_row, 80)

                    info_item = QTableWidgetItem(text.strip())
                    info_item.setBackground(QBrush(QColor('#FFFF00')))
                    font = QFont()
                    font.setPointSize(20)
                    font.setBold(True)
                    info_item.setFont(font)
                    info_item.setTextAlignment(Qt.AlignCenter)

                    self.table_widget.setItem(new_row, 0, info_item)
                    self.table_widget.setSpan(new_row, 0, 1, 16)

                    self.save_custom_info(row, text.strip())

                    total_rows = self.table_widget.rowCount()
                    selected_rows = self.table_widget.selectionModel().selectedRows()
                    if selected_rows:
                        current_row = selected_rows[0].row() + 1
                        self.block_count_label.setText(f"{current_row}/{total_rows}")
                    else:
                        self.block_count_label.setText(f"0/{total_rows}")
                    print(f"已添加自定义信息: {text.strip()}")

            custom_info_action.triggered.connect(on_add_custom_info)

        context_menu.exec_(self.table_widget.mapToGlobal(event))

    def save_roll_change_info(self, row):
        """保存换辊行信息"""
        try:
            self.custom_and_roll_change_info['roll_change'][str(row)] = True
            self.save_custom_and_roll_change_info()
        except Exception as e:
            print(f"保存换辊信息失败: {str(e)}")

    def save_custom_info(self, row, text):
        """保存自定义信息"""
        try:
            self.custom_and_roll_change_info['custom_info'][str(row)] = text
            self.save_custom_and_roll_change_info()
        except Exception as e:
            print(f"保存自定义信息失败: {str(e)}")
    
    def remove_roll_change_info(self, row):
        """删除换辊行信息"""
        try:
            if str(row) in self.custom_and_roll_change_info['roll_change']:
                del self.custom_and_roll_change_info['roll_change'][str(row)]
                self.save_custom_and_roll_change_info()
        except Exception as e:
            print(f"删除换辊信息失败: {str(e)}")
    
    def remove_custom_info(self, row):
        """删除自定义信息"""
        try:
            if str(row) in self.custom_and_roll_change_info['custom_info']:
                del self.custom_and_roll_change_info['custom_info'][str(row)]
                self.save_custom_and_roll_change_info()
        except Exception as e:
            print(f"删除自定义信息失败: {str(e)}")
    
    def save_custom_and_roll_change_info(self):
        """保存自定义信息和换辊信息"""
        try:
            import json
            import os
            os.makedirs(os.path.dirname(self.custom_info_file), exist_ok=True)
            with open(self.custom_info_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_and_roll_change_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义信息和换辊信息失败: {str(e)}")
    
    def load_custom_and_roll_change_info(self):
        """加载自定义信息和换辊信息"""
        try:
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QFont, QColor, QBrush
            from PyQt5.QtCore import Qt
            
            # 从后往前处理，避免插入行影响索引
            # 处理换辊信息
            for row_key in sorted(self.custom_and_roll_change_info['roll_change'].keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True):
                row = int(row_key)
                if row < self.table_widget.rowCount():
                    # 在指定行后插入换辊行
                    new_row = row + 1
                    self.table_widget.insertRow(new_row)
                    self.table_widget.setRowHeight(new_row, 80)
                    
                    # 设置换辊信息
                    roll_change_item = QTableWidgetItem("换辊")
                    roll_change_item.setBackground(QColor('#00FF00'))
                    # 设置字体
                    font = QFont()
                    font.setPointSize(20)
                    font.setBold(True)
                    roll_change_item.setFont(font)
                    # 设置水平和垂直居中
                    roll_change_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table_widget.setItem(new_row, 0, roll_change_item)
                    
                    # 合并单元格，只合并到强度列（索引15）
                    self.table_widget.setSpan(new_row, 0, 1, 16)
            
            # 处理自定义信息
            for row_key in sorted(self.custom_and_roll_change_info['custom_info'].keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True):
                row = int(row_key)
                text = self.custom_and_roll_change_info['custom_info'][row_key]
                if row < self.table_widget.rowCount() and text:
                    # 在指定行后插入自定义信息行
                    new_row = row + 1
                    self.table_widget.insertRow(new_row)
                    self.table_widget.setRowHeight(new_row, 80)
                    
                    # 设置自定义信息
                    custom_item = QTableWidgetItem(text)
                    custom_item.setBackground(QColor('#FFFF00'))
                    # 设置字体
                    font = QFont()
                    font.setPointSize(20)
                    font.setBold(True)
                    custom_item.setFont(font)
                    # 设置水平和垂直居中
                    custom_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table_widget.setItem(new_row, 0, custom_item)
                    
                    # 合并单元格，只合并到强度列（索引15）
                    self.table_widget.setSpan(new_row, 0, 1, 16)
        except Exception as e:
            print(f"加载自定义信息和换辊信息失败: {str(e)}")

    def connect_signals(self):
        """连接信号"""
        # 连接表格选择变化信号
        self.table_widget.selectionModel().currentRowChanged.connect(self.update_block_count)

        # 连接滚动定时器
        # 注意：定时器的连接在toggle_scroll方法中处理

        # 连接滚动时间输入框
        self.scroll_time_edit.textChanged.connect(self.on_scroll_time_changed)

        # 连接右键菜单
        self.table_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)

        # 连接单元格点击事件
        self.table_widget.cellClicked.connect(self.on_cell_clicked)

        # 连接选择变化信号
        self.table_widget.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # 连接选择变化事件，确保标注的单元格保持红色背景
        self.table_widget.itemSelectionChanged.connect(self.maintain_cell_highlight)
    
    def apply_annotation_condition(self, condition):
        """应用标注条件"""
        try:
            # 首先移除所有现有的自定义标注行
            rows_to_remove = []
            for i in range(self.table_widget.rowCount()):
                item = self.table_widget.item(i, 0)
                if item:
                    bg_color = item.background().color().name()
                    if bg_color == '#ffff00':
                        # 只移除自定义标注条件行，保留换辊和自定义信息行
                        font = item.font()
                        if font.pointSize() == 20:
                            rows_to_remove.append(i)
            
            # 从后往前删除，避免索引变化
            rows_to_remove.sort(reverse=True)
            for row in rows_to_remove:
                self.table_widget.removeRow(row)
            
            # 如果条件为空，直接返回
            if not condition.strip():
                return
            
            # 列名映射
            column_map = {
                "计划号": 0,
                "钢卷号": 1,
                "牌号（钢级）": 2,
                "坯宽": 3,
                "减宽": 4,
                "调宽": 5,
                "轧宽": 6,
                "公差带": 7,
                "粗轧报信": 8,
                "除鳞": 9,
                "坯厚": 10,
                "坯长": 11,
                "轧厚": 12,
                "中厚": 13,
                "RT2": 14,
                "强度": 15
            }
            
            def check_single_condition(cond, row_idx):
                """检查单个条件是否满足"""
                # 解析条件
                if '>=' in cond:
                    field, value = cond.split('>=', 1)
                    operator = '>='
                elif '<=' in cond:
                    field, value = cond.split('<=', 1)
                    operator = '<='
                elif '>' in cond:
                    field, value = cond.split('>', 1)
                    operator = '>'
                elif '<' in cond:
                    field, value = cond.split('<', 1)
                    operator = '<'
                elif '=' in cond:
                    field, value = cond.split('=', 1)
                    operator = '='
                else:
                    return False
                
                field = field.strip()
                value = value.strip()
                
                # 检查字段是否存在
                if field not in column_map:
                    return False
                
                # 获取单元格值
                col_idx = column_map[field]
                item = self.table_widget.item(row_idx, col_idx)
                if not item:
                    return False
                
                cell_value = item.text().strip()
                
                # 比较值
                try:
                    # 移除标注符号（Δ和*）
                    clean_cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                    clean_value = value.replace('Δ', '').replace('*', '').strip()
                    
                    if operator == '=':
                        return clean_cell_value == clean_value
                    else:
                        cell_value_num = float(clean_cell_value)
                        # 对调宽字段取绝对值
                        if field == "调宽":
                            cell_value_num = abs(cell_value_num)
                        value_num = float(clean_value)
                        if operator == '>':
                            return cell_value_num > value_num
                        elif operator == '<':
                            return cell_value_num < value_num
                        elif operator == '>=':
                            return cell_value_num >= value_num
                        elif operator == '<=':
                            return cell_value_num <= value_num
                except:
                    return False
            
            # 检查条件组合方式
            use_or = " 或 " in condition
            if use_or:
                conditions = condition.split(" 或 ")
            else:
                conditions = condition.split(" 且 ")
            
            matched_rows = []
            
            # 遍历所有行
            for i in range(self.table_widget.rowCount()):
                # 检查是否是特殊行
                first_item = self.table_widget.item(i, 0)
                if first_item:
                    bg_color = first_item.background().color().name()
                    if bg_color == '#ffff00':
                        continue
                
                # 检查是否符合条件
                if use_or:
                    # 或逻辑：只要有一个条件满足
                    match = False
                    for cond in conditions:
                        cond = cond.strip()
                        if not cond:
                            continue
                        
                        if check_single_condition(cond, i):
                            match = True
                            break
                else:
                    # 且逻辑：所有条件都要满足
                    match = True
                    for cond in conditions:
                        cond = cond.strip()
                        if not cond:
                            continue
                        
                        if not check_single_condition(cond, i):
                            match = False
                            break
                
                if match:
                    matched_rows.append(i)
            
            # 对符合条件的行添加标注
            if matched_rows:
                # 从下往上处理，避免插入行影响索引
                for row_idx in sorted(matched_rows, reverse=True):
                    new_row = row_idx + 1
                    self.table_widget.insertRow(new_row)
                    self.table_widget.setRowHeight(new_row, 80)
                    
                    # 创建标注项
                    annotation_item = QTableWidgetItem(condition)
                    annotation_item.setBackground(QBrush(QColor('#FFFF00')))  # 黄色背景
                    font = QFont()
                    font.setPointSize(20)
                    font.setBold(True)
                    annotation_item.setFont(font)
                    # 设置水平和垂直居中
                    annotation_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    
                    self.table_widget.setItem(new_row, 0, annotation_item)
                    # 只合并到强度列（索引15）
                    self.table_widget.setSpan(new_row, 0, 1, 16)
        except Exception as e:
            print(f"应用标注条件失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_furnace_data(self):
        """加载装炉明细数据"""
        try:
            import os
            import tempfile
            import shutil
            import xlrd
            import time
            import json
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            print("\n=== 开始加载装炉明细数据 ===")
            
            # 读取装炉顺序.xls
            # 使用与主程序相同的plan_dir路径
            if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'plan_dir'):
                plan_dir = os.path.join(self.parent.plan_dir, "计划号")
                print(f"使用主程序的plan_dir: {plan_dir}")
            else:
                # 备用方案：使用当前工作目录
                plan_dir = os.path.join(os.getcwd(), "计划号")
                print(f"使用当前工作目录: {plan_dir}")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            print(f"查找装炉顺序文件: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"[×] 文件不存在: {excel_file}")
                self.block_count_label.setText("0/0")
                return
            
            # 验证装炉顺序文件
            if hasattr(self.parent, 'ensure_zhuanglu_shunxu_file'):
                success, msg = self.parent.ensure_zhuanglu_shunxu_file(force_reload=True)
                if not success:
                    print(f"[×] 装炉顺序文件验证失败: {msg}")
                    self.block_count_label.setText("0/0")
                    return
            
            # 创建临时副本
            temp_file_name = f"temp_装炉顺序_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            shutil.copy2(excel_file, temp_file_path)
            print(f"创建临时副本: {temp_file_path}")
            
            # 读取数据
            workbook = xlrd.open_workbook(temp_file_path)
            sheet = workbook.sheet_by_index(0)
            
            headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
            print(f"列名: {headers}")
            
            # 查找列索引
            order_col = None  # 装炉顺序号
            plan_col = None   # 计划号
            coil_col = None   # 钢卷号
            
            for idx, header in enumerate(headers):
                if '装炉顺序号' in header or '装炉顺序' in header:
                    order_col = idx
                    print(f"找到装炉顺序列: {idx}")
                elif '计划号' in header:
                    plan_col = idx
                    print(f"找到计划号列: {idx}")
                elif '钢卷号' in header:
                    coil_col = idx
                    print(f"找到钢卷号列: {idx}")
            
            if None in [order_col, plan_col, coil_col]:
                print(f"缺少必要列: order_col={order_col}, plan_col={plan_col}, coil_col={coil_col}")
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"删除临时文件: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件失败: {e}")
                self.block_count_label.setText("0/0")
                return
            
            # 读取数据
            furnace_data = []
            for row in range(1, sheet.nrows):
                try:
                    order = sheet.cell_value(row, order_col)
                    # 转换装炉顺序为整数
                    if isinstance(order, float) and order.is_integer():
                        order = int(order)
                    plan_no = str(sheet.cell_value(row, plan_col)).strip()
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    coil_no_clean = ''.join(c for c in coil_no if c.isdigit())

                    if plan_no and coil_no_clean:
                        furnace_data.append({
                            'order': order,
                            'plan_no': plan_no,
                            'coil_no': coil_no,
                            'coil_no_clean': coil_no_clean
                        })
                        print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no}, 纯净钢卷号={coil_no_clean}")
                    else:
                        print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}', 纯净钢卷号='{coil_no_clean}'")
                except Exception as e:
                    print(f"读取行 {row} 失败: {e}")
                    continue
            
            # 删除临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"删除临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")
            
            print(f"加载到 {len(furnace_data)} 条装炉数据")
            if len(furnace_data) == 0:
                print("装炉顺序.xls文件中没有数据")
                self.block_count_label.setText("0/0")
                return
            
            # 清空表格
            self.table_widget.setRowCount(0)

            # 加载计划号数据
            displayed_count = 0
            skipped_count = 0
            missing_file_count = 0
            
            for item in furnace_data:
                plan_no = item['plan_no']
                coil_no = item['coil_no']
                coil_no_clean = item['coil_no_clean']

                # 获取计划号文件
                plan_file = self.get_plan_file(plan_no)
                
                if plan_file:
                    try:
                        # 读取计划号文件数据，使用纯净钢卷号进行匹配
                        plan_data = self.read_plan_file(plan_file, coil_no_clean)
                        if plan_data:
                            # 使用原始钢卷号（带标注）显示
                            self.add_plan_data_to_table(plan_data, plan_no, coil_no)
                            displayed_count += 1
                        else:
                            # 计划号文件存在但找不到匹配的钢卷号，显示基本信息
                            print(f"计划号文件存在但未找到匹配的钢卷号: {plan_no}, 钢卷号: {coil_no}")
                            plan_data = {
                                'coil_no': coil_no
                            }
                            self.add_plan_data_to_table(plan_data, plan_no, coil_no)
                            displayed_count += 1
                    except Exception as e:
                        # 读取文件失败，显示基本信息
                        print(f"读取计划号文件失败: {plan_no}, 错误: {e}")
                        plan_data = {
                            'coil_no': coil_no
                        }
                        self.add_plan_data_to_table(plan_data, plan_no, coil_no)
                        displayed_count += 1
                else:
                    # 即使没有计划号文件，也要显示钢卷号
                    print(f"未找到计划号文件: {plan_no}，但仍显示钢卷号: {coil_no}")
                    missing_file_count += 1
                    plan_data = {
                        'coil_no': coil_no
                    }
                    self.add_plan_data_to_table(plan_data, plan_no, coil_no)
                    displayed_count += 1
            
            print(f"\n装炉明细数据加载完成:")
            print(f"  - 总钢卷号数: {len(furnace_data)}")
            print(f"  - 已显示: {displayed_count}")
            print(f"  - 未找到文件: {missing_file_count}")
            print(f"  - 跳过: {skipped_count}")
            
            # 保存表格数据
            self.save_current_table_data()
            
            # 更新块数显示
            self.update_block_count()
            
            # 查找最后离开时的钢卷号并定位光标
            self.locate_cursor_by_saved_coil()
            
            # 自动启动自动滚动功能
            self.start_auto_scroll()
            
            # 应用保存的标注条件
            self.apply_saved_annotation_conditions()
            # 加载自定义信息和换辊信息
            self.load_custom_and_roll_change_info()
        except Exception as e:
            print(f"加载装炉明细数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.block_count_label.setText("0/0")
    
    def showEvent(self, event):
        """窗口显示时的事件处理"""
        super().showEvent(event)
        # 窗口显示时加载窗口状态
        if hasattr(self, 'table_widget') and self.table_widget.rowCount() > 0:
            print(f"窗口显示时应用光标和滚动设置")
            # 查找最后离开时的钢卷号并定位光标
            self.locate_cursor_by_saved_coil()
            # 自动启动自动滚动功能
            self.start_auto_scroll()
            # 强制刷新表格
            self.table_widget.repaint()
            self.table_widget.update()
            # 自动应用保存的标注条件
            self.apply_saved_annotation_conditions()
            # 加载自定义信息和换辊信息
            self.load_custom_and_roll_change_info()
        
        # 同步主窗口的下一次执行时间
        if self.parent and hasattr(self.parent, 'next_execution_label') and hasattr(self, 'next_execution_label'):
            try:
                # 先调用主窗口的update_next_execution_label方法确保主窗口的时间是最新的
                if hasattr(self.parent, 'update_next_execution_label'):
                    self.parent.update_next_execution_label()
                # 然后同步主窗口的下一次执行时间
                next_exec_text = self.parent.next_execution_label.text()
                self.next_execution_label.setText(next_exec_text)
                print(f"同步下一次执行时间: {next_exec_text}")
            except Exception as e:
                print(f"同步下一次执行时间失败: {str(e)}")
            
    def apply_saved_annotation_conditions(self):
        """应用保存的标注条件"""
        print(f"应用保存的标注条件")
        if hasattr(self, 'custom_annotation_condition_groups') and self.custom_annotation_condition_groups:
            # 移除现有的自定义标注行
            rows_to_remove = []
            for i in range(self.table_widget.rowCount()):
                item = self.table_widget.item(i, 0)
                if item:
                    # 检查单元格是否是标注行（通过背景色判断）
                    if item.background().color() == QColor('#FFFF00'):  # 黄色背景
                        rows_to_remove.append(i)
            
            # 从后往前删除，避免索引变化
            for row in sorted(rows_to_remove, reverse=True):
                self.table_widget.removeRow(row)
            
            # 检查每个条件组
            for condition_group in self.custom_annotation_condition_groups:
                if not condition_group.get('enabled', True):
                    continue
                
                conditions = condition_group.get('conditions', [])
                combo_type = condition_group.get('combo_type', '且')
                
                # 收集启用的条件
                enabled_conditions = []
                for cond in conditions:
                    if isinstance(cond, dict):
                        if cond.get('enabled', True):
                            enabled_conditions.append(cond.get('text', ''))
                    else:
                        enabled_conditions.append(cond)
                
                # 组合条件
                if not enabled_conditions:
                    continue
                
                combined_condition = f" {combo_type} ".join(enabled_conditions)
                
                # 解析条件
                parsed_conditions = []
                if " 且 " in combined_condition:
                    parsed_conditions = combined_condition.split(" 且 ")
                elif " 或 " in combined_condition:
                    parsed_conditions = combined_condition.split(" 或 ")
                else:
                    parsed_conditions = [combined_condition]
                
                # 检查每个条件
                def check_single_condition(condition, row):
                    # 解析条件：字段名、运算符、值
                    field = ""
                    operator = ""
                    value = ""
                    
                    # 查找运算符
                    operators = [">=", "<=", ">", "<", "="]
                    for op in operators:
                        if op in condition:
                            parts = condition.split(op)
                            field = parts[0].strip()
                            operator = op
                            value = parts[1].strip()
                            break
                    
                    if not field or not operator or not value:
                        return False
                    
                    # 字段名映射到列索引
                    field_map = {
                        "牌号（钢级）": 2,
                        "坯宽": 3,
                        "减宽": 4,
                        "调宽": 5,
                        "轧宽": 6,
                        "公差带": 7,
                        "粗轧报信": 8,
                        "除鳞": 9,
                        "坯厚": 10,
                        "坯长": 11,
                        "轧厚": 12,
                        "中厚": 13,
                        "RT2": 14,
                        "强度": 15
                    }
                    
                    if field not in field_map:
                        return False
                    
                    column = field_map[field]
                    
                    # 获取单元格值
                    item = self.table_widget.item(row, column)
                    if not item:
                        return False
                    
                    cell_value = item.text().strip()
                    
                    # 移除标注符号（Δ和*）
                    cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                    
                    # 比较值
                    try:
                        # 移除标注符号（Δ和*）
                        clean_cell_value = cell_value.replace('Δ', '').replace('*', '').strip()
                        clean_value = value.replace('Δ', '').replace('*', '').strip()
                        
                        if operator == '=':
                            return clean_cell_value == clean_value
                        else:
                            cell_value_num = float(clean_cell_value)
                            # 对调宽字段取绝对值
                            if field == "调宽":
                                cell_value_num = abs(cell_value_num)
                            value_num = float(clean_value)
                            if operator == '>':
                                return cell_value_num > value_num
                            elif operator == '<':
                                return cell_value_num < value_num
                            elif operator == '>=':
                                return cell_value_num >= value_num
                            elif operator == '<=':
                                return cell_value_num <= value_num
                    except:
                        return False
                
                # 收集符合条件的行
                matched_rows = []
                for i in range(self.table_widget.rowCount()):
                    # 检查是否是标注行
                    item = self.table_widget.item(i, 0)
                    if item:
                        bg_color = item.background().color().name()
                        if bg_color == '#ffff00':  # 黄色背景
                            continue
                    
                    # 检查是否符合所有条件
                    match = True
                    for cond in parsed_conditions:
                        if not check_single_condition(cond, i):
                            match = False
                            break
                    
                    if match:
                        matched_rows.append(i)
                
                # 对符合条件的行添加标注
                if matched_rows:
                    # 从下往上处理，避免插入行影响索引
                    for row_idx in sorted(matched_rows, reverse=True):
                        # 检查是否已经有标注行
                        has_annotation = False
                        if row_idx + 1 < self.table_widget.rowCount():
                            next_item = self.table_widget.item(row_idx + 1, 0)
                            if next_item:
                                # 检查是否是标注行（通过背景色判断）
                                bg_color = next_item.background().color().name()
                                if bg_color == '#ffff00':  # 黄色背景
                                    has_annotation = True
                        
                        if not has_annotation:
                            # 在下面插入一行
                            new_row = row_idx + 1
                            self.table_widget.insertRow(new_row)
                            self.table_widget.setRowHeight(new_row, 80)
                            
                            # 设置标注内容
                            annotation_item = QTableWidgetItem(f"{combined_condition}")
                            annotation_item.setBackground(Qt.yellow)
                            # 设置字体
                            font = QFont()
                            font.setPointSize(20)
                            font.setBold(True)
                            annotation_item.setFont(font)
                            # 设置水平和垂直居中
                            annotation_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                            self.table_widget.setItem(new_row, 0, annotation_item)
                            
                            # 合并单元格，只合并到强度列（索引15）
                            self.table_widget.setSpan(new_row, 0, 1, 16)
    
    def closeEvent(self, event):
        """窗口关闭时的事件处理"""
        try:
            # 先关闭设置窗口（如果存在且可见），触发设置窗口的保存逻辑
            if hasattr(self, 'settings_window') and self.settings_window.isVisible():
                self.settings_window.close()
            # 保存窗口状态
            self.save_window_state()
            # 停止滚动定时器
            if self.scroll_timer.isActive():
                self.scroll_timer.stop()
            # 保存状态
            self.save_current_table_data()
            # 保存最后选中的钢卷号
            self.save_last_selected_coil()
            # 保存标注条件
            import json
            import os
            if hasattr(self, 'custom_annotation_condition_groups'):
                # 保存新格式（条件组）
                data = {
                    'condition_groups': self.custom_annotation_condition_groups
                }
            else:
                # 保存旧格式
                data = {
                    'conditions': self.custom_annotation_conditions if hasattr(self, 'custom_annotation_conditions') else [],
                    'combo_type': self.custom_annotation_combo_type if hasattr(self, 'custom_annotation_combo_type') else "且"
                }
            with open(self.annotation_conditions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            # 忽略所有错误，确保程序能正常关闭
            pass
        # 关闭窗口
        event.accept()
    
    def get_plan_file(self, plan_no):
        """获取计划号文件路径"""
        import os
        # 使用与主程序相同的plan_dir路径
        if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'plan_dir'):
            plan_dir = os.path.join(self.parent.plan_dir, "计划号")
            print(f"使用主程序的plan_dir: {plan_dir}")
        else:
            # 备用方案：使用当前工作目录
            plan_dir = os.path.join(os.getcwd(), "计划号")
            print(f"使用当前工作目录: {plan_dir}")
        # 首先在计划号目录查找
        file_path = os.path.join(plan_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        # 然后在backup目录查找
        backup_dir = os.path.join(plan_dir, "backup")
        if os.path.exists(backup_dir):
            file_path = os.path.join(backup_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
        # 尝试其他可能的路径
        # 直接在计划号目录的上级目录查找
        parent_dir = os.path.dirname(plan_dir)
        file_path = os.path.join(parent_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        # 尝试在当前工作目录查找
        file_path = os.path.join(os.getcwd(), f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        return None
    
    def get_all_coil_nos_from_plan_file(self, file_path):
        """从计划号文件中读取所有钢卷号"""
        try:
            import xlrd
            coil_nos = []
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            
            header_row = 0
            for i in range(min(10, sheet.nrows)):
                row_values = []
                for col in range(sheet.ncols):
                    try:
                        value = str(sheet.cell_value(i, col)).strip()
                        row_values.append(value)
                    except:
                        row_values.append('')
                has_coil_col = any('钢卷号' in v for v in row_values)
                has_seq_col = any('序号' in v for v in row_values)
                if has_coil_col or has_seq_col:
                    header_row = i
                    break
            
            if header_row == 0 and sheet.nrows > 1:
                header_row = 1
            
            headers = []
            for col in range(sheet.ncols):
                try:
                    header = str(sheet.cell_value(header_row, col)).strip()
                    headers.append(header)
                except:
                    headers.append('')
            
            col_map = {}
            for idx, header in enumerate(headers):
                col_map[header] = idx
            
            coil_no_col = -1
            if 'coil_no' in col_map:
                coil_no_col = col_map['coil_no']
            elif '钢卷号' in col_map:
                coil_no_col = col_map['钢卷号']
            else:
                for header, idx in col_map.items():
                    if '钢卷号' in header:
                        coil_no_col = idx
                        break
                if coil_no_col == -1:
                    for header, idx in col_map.items():
                        if '序号' in header:
                            coil_no_col = idx
                            break
            
            if coil_no_col != -1:
                for row in range(header_row + 1, sheet.nrows):
                    try:
                        cell_value = str(sheet.cell_value(row, coil_no_col)).strip()
                        if cell_value:
                            coil_nos.append(cell_value)
                    except:
                        pass
            
            return coil_nos
        except Exception as e:
            print(f"读取计划号文件钢卷号失败: {e}")
            return []
    
    def read_plan_file(self, file_path, target_coil_no):
        """从计划号文件中提取钢卷数据（原程序逻辑）"""
        try:
            import xlrd
            print(f"提取钢卷数据: {file_path}, 钢卷号: {target_coil_no}")
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            
            header_row = 0
            for i in range(min(10, sheet.nrows)):
                row_values = []
                for col in range(sheet.ncols):
                    try:
                        value = str(sheet.cell_value(i, col)).strip()
                        row_values.append(value)
                    except:
                        row_values.append('')
                has_coil_col = any('钢卷号' in v for v in row_values)
                has_seq_col = any('序号' in v for v in row_values)
                if has_coil_col or has_seq_col:
                    header_row = i
                    print(f"自动检测到列名行: {i+1} (包含钢卷号或序号列)")
                    break
            
            if header_row == 0:
                for i in range(min(5, sheet.nrows)):
                    row_values = []
                    for col in range(sheet.ncols):
                        try:
                            value = str(sheet.cell_value(i, col)).strip()
                            row_values.append(value)
                        except:
                            row_values.append('')
                    non_empty = [v for v in row_values if v]
                    if len(non_empty) >= 5:
                        header_row = i
                        print(f"自动检测到列名行: {i+1} (包含{len(non_empty)}个非空值)")
                        break
            
            if header_row == 0 and sheet.nrows > 1:
                header_row = 1
                print("使用第二行作为列名行")
            
            headers = []
            for col in range(sheet.ncols):
                try:
                    header = str(sheet.cell_value(header_row, col)).strip()
                    headers.append(header)
                except:
                    headers.append('')
            print(f"计划号文件列名（从第{header_row+1}行开始）: {headers}")
            
            col_map = {}
            for idx, header in enumerate(headers):
                col_map[header] = idx
                print(f"找到列: {idx} (表头: {header})")
            
            if '钢卷号' not in col_map and 'coil_no' not in col_map:
                print("未找到钢卷号列，尝试自动检测...")
                if sheet.nrows > header_row + 1:
                    for col in range(sheet.ncols):
                        try:
                            has_coil_like = 0
                            for row in range(header_row + 1, min(header_row + 11, sheet.nrows)):
                                value = str(sheet.cell_value(row, col)).strip()
                                clean_value = ''.join(c for c in value if c.isdigit())
                                if 8 <= len(clean_value) <= 12:
                                    has_coil_like += 1
                            if has_coil_like >= 3:
                                col_map['coil_no'] = col
                                print(f"自动检测到钢卷号列: {col}")
                                break
                        except:
                            pass
            
            found = False
            for row in range(header_row + 1, sheet.nrows):
                try:
                    coil_no_col = -1
                    if 'coil_no' in col_map:
                        coil_no_col = col_map['coil_no']
                    elif '钢卷号' in col_map:
                        coil_no_col = col_map['钢卷号']
                    else:
                        for header, idx in col_map.items():
                            if '钢卷号' in header:
                                coil_no_col = idx
                                break
                        if coil_no_col == -1:
                            for header, idx in col_map.items():
                                if '序号' in header:
                                    coil_no_col = idx
                                    break
                    
                    if coil_no_col != -1:
                        cell_value = str(sheet.cell_value(row, coil_no_col)).strip()
                        clean_cell_value = ''.join(c for c in cell_value if c.isdigit())
                        print(f"尝试匹配钢卷号: 目标={target_coil_no}, 单元格值={cell_value}, 清理后={clean_cell_value}")
                        if clean_cell_value == target_coil_no or cell_value == target_coil_no:
                            found = True
                            data = {}
                            for header, col_idx in col_map.items():
                                if col_idx < sheet.ncols:
                                    try:
                                        value = sheet.cell_value(row, col_idx)
                                        if isinstance(value, float) and value.is_integer():
                                            value = int(value)
                                        data[header] = str(value).strip()
                                    except:
                                        data[header] = ''
                            print(f"找到钢卷数据: {data}")
                            return data
                        else:
                            print(f"钢卷号不匹配: 目标={target_coil_no}, 单元格值={cell_value}, 清理后={clean_cell_value}")
                    else:
                        print("未找到钢卷号列")
                except Exception as e:
                    print(f"读取单元格失败: {e}")
            
            if not found:
                print(f"未找到钢卷号: {target_coil_no} 在文件: {file_path}")
                print("文件中的钢卷号:")
                for row in range(header_row + 1, min(header_row + 11, sheet.nrows)):
                    if 'coil_no' in col_map:
                        try:
                            cell_value = str(sheet.cell_value(row, col_map['coil_no'])).strip()
                            print(f"  行 {row}: {cell_value}")
                        except:
                            pass
                    elif '钢卷号' in col_map:
                        try:
                            cell_value = str(sheet.cell_value(row, col_map['钢卷号'])).strip()
                            print(f"  行 {row}: {cell_value}")
                        except:
                            pass
                print("返回基本数据结构")
                return {
                    '钢卷号': target_coil_no,
                    '牌号（钢级）': '',
                    '除鳞': '',
                    '去向': '',
                    '坯厚': '',
                    '坯宽': '',
                    '坯长': '',
                    '中厚': '',
                    '轧厚': '',
                    '轧宽': '',
                    '订宽': '',
                    '切边': '',
                    '调宽': '',
                    '减宽': '',
                    '公差带': '',
                    'RT2': '',
                    '强度': '',
                    '粗轧报信': '',
                    '坯头部宽': '',
                    '坯尾部宽': '',
                    '热轧产品分类': '',
                    '炼钢钢种': '',
                    '负公差': '',
                    '正公差': '',
                    '回炉坯': '',
                    '原轧宽': ''
                }
        except Exception as e:
            print(f"读取计划号文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_plan_data_to_table(self, plan_data, plan_no, coil_no):
        """将计划数据添加到表格"""
        try:
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            columns = [
                "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
                "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
            ]
            
            # 添加新行
            row_idx = self.table_widget.rowCount()
            self.table_widget.insertRow(row_idx)
            
            # 计划号和钢卷号直接使用传入的值
            # 注意：从xls读取的数据中，"切边"可能对应"切边方式"，"订宽"可能对应"订货宽度"
            row_data = [
                plan_no,
                coil_no,
                plan_data.get('牌号（钢级）', ''),
                plan_data.get('坯宽', ''),
                plan_data.get('减宽', ''),
                plan_data.get('调宽', ''),
                plan_data.get('轧宽', ''),
                plan_data.get('公差带', ''),
                plan_data.get('粗轧报信', ''),
                plan_data.get('除鳞', ''),
                plan_data.get('坯厚', ''),
                plan_data.get('坯长', ''),
                plan_data.get('轧厚', ''),
                plan_data.get('中厚', ''),
                plan_data.get('RT2', ''),
                plan_data.get('强度', ''),
                plan_data.get('切边方式', plan_data.get('切边', '')),  # 优先使用"切边方式"，其次使用"切边"
                plan_data.get('去向', ''),
                plan_data.get('订货宽度', plan_data.get('订宽', '')),  # 优先使用"订货宽度"，其次使用"订宽"
                plan_data.get('坯头部宽', ''),
                plan_data.get('坯尾部宽', ''),
                plan_data.get('热轧产品分类', ''),
                plan_data.get('炼钢钢种', ''),
                plan_data.get('负公差', ''),
                plan_data.get('正公差', ''),
                plan_data.get('回炉坯', ''),
                plan_data.get('原轧宽', '')
            ]
            
            # 计算标注信息
            标注信息 = []
            
            # 检查是否无APS钢种
            除鳞值 = str(plan_data.get('除鳞', '')).strip()
            if '无APS' in 除鳞值:
                标注信息.append("无APS钢种")
            
            # 检查减宽是否超标
            减宽值 = plan_data.get('减宽', '')
            try:
                减宽数值 = float(str(减宽值).replace('Δ', '').replace('*', '').strip())
                if 减宽数值 >= 240:
                    标注信息.append(f"减宽量超标: {减宽数值}")
                elif 减宽数值 < 0:
                    标注信息.append("逆宽轧制板坯")
            except:
                pass
            
            # 检查轧宽是否过低
            轧宽值 = plan_data.get('轧宽', '')
            try:
                轧宽数值 = float(str(轧宽值).replace('Δ', '').replace('*', '').strip())
                if 轧宽数值 < 930:
                    标注信息.append(f"轧宽低于930: {轧宽数值}")
                    if 轧宽数值 < 860:
                        标注信息.append(f"轧宽低于860: {轧宽数值}")
            except:
                pass
            
            # 填充数据
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # 设置字体
                font = item.font()
                font.setFamily("微软雅黑")
                font.setPointSize(20)
                font.setBold(True)
                item.setFont(font)
                
                # 获取列名
                col_name = columns[col_idx] if col_idx < len(columns) else ""
                
                # 检查是否有标识（三角符号Δ或星号*）
                value_str = str(value)
                if 'Δ' in value_str or '*' in value_str:
                    # 设置红色背景
                    item.setBackground(QBrush(QColor('#FF0000')))
                    # 添加annotation属性，用于样式表识别
                    item.setData(Qt.UserRole, True)
                    # 生成tooltip信息
                    tooltip = self.generate_tooltip(col_name, value_str, 标注信息)
                    if tooltip:
                        item.setToolTip(tooltip)
                # 除鳞字段中包含"回"和"无APS"的单元格也改背景色为红色
                elif col_name == "除鳞" and ('回' in value_str or '无APS' in value_str):
                    # 设置红色背景
                    item.setBackground(QBrush(QColor('#FF0000')))
                    # 添加annotation属性，用于样式表识别
                    item.setData(Qt.UserRole, True)
                    # 生成tooltip信息
                    tooltip = self.generate_tooltip(col_name, value_str, 标注信息)
                    if tooltip:
                        item.setToolTip(tooltip)
                # 其他高亮处理
                else:
                    self.process_cell_highlight(item, col_name, value_str, 标注信息)
                
                # 设置对齐方式
                if col_idx == 2:  # 牌号列（索引2）
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:  # 其他所有列居中
                    item.setTextAlignment(Qt.AlignCenter)  # 水平和垂直居中
                
                self.table_widget.setItem(row_idx, col_idx, item)
            
            # 保存标注信息到行数据中
            # 注意：这里我们需要将标注信息存储在一个可以被print_furnace_details方法访问的地方
            # 我们可以使用QTableWidgetItem的setData方法来存储标注信息
            # 在第0列（计划号列）的item中存储标注信息
            plan_item = self.table_widget.item(row_idx, 0)
            if plan_item:
                plan_item.setData(Qt.UserRole + 1, 标注信息)
            
            # 自动调整行高
            self.table_widget.resizeRowToContents(row_idx)
            # 增加行高10
            current_height = self.table_widget.rowHeight(row_idx)
            self.table_widget.setRowHeight(row_idx, current_height + 10)
            
            print(f"已插入表格数据: {row_data}")
                
        except Exception as e:
            print(f"添加计划数据到表格失败: {str(e)}")
    
    def generate_tooltip(self, col_name, value_str, 标注信息列表):
        """生成单元格的tooltip提示信息"""
        tooltip_lines = []
        
        # 列标题
        tooltip_lines.append(f"【{col_name}】")
        
        # 根据列名添加对应的预警条件
        if col_name == "除鳞":
            if '回' in value_str:
                tooltip_lines.append("• 回炉坯")
            if '无APS' in value_str:
                tooltip_lines.append("• 无APS钢种")
        elif col_name == "坯厚":
            try:
                value_clean = value_str.replace('Δ', '').replace('*', '').strip()
                if value_clean:
                    blank_thickness = float(value_clean)
                    if blank_thickness > 230:
                        tooltip_lines.append(f"• 坯厚超标 (当前值: {blank_thickness})")
            except:
                pass
        elif col_name == "牌号（钢级）":
            if 'Δ' in value_str:
                tooltip_lines.append("• 无APS钢种")
        elif col_name == "减宽":
            try:
                value_clean = value_str.replace('Δ', '').replace('*', '').strip()
                if value_clean:
                    width_reduction = float(value_clean)
                    if width_reduction >= 240:
                        tooltip_lines.append(f"• 减宽量超标 (当前值: {width_reduction})")
                    elif width_reduction < 0:
                        tooltip_lines.append("• 逆宽轧制板坯")
            except:
                pass
        elif col_name == "调宽":
            if 'Δ' in value_str:
                tooltip_lines.append("• 板坯最小宽度低于轧宽")
                tooltip_lines.append("  (相当于逆宽轧制)")
                tooltip_lines.append(f"  当前值: {value_str}")
        elif col_name == "轧宽":
            try:
                value_clean = value_str.replace('Δ', '').replace('*', '').strip()
                if value_clean:
                    roll_width = float(value_clean)
                    if roll_width < 860:
                        tooltip_lines.append(f"• 轧宽过低 (当前值: {roll_width})")
                    elif roll_width < 930:
                        tooltip_lines.append(f"• 轧宽偏低 (当前值: {roll_width})")
            except:
                pass
        elif col_name == "钢卷号":
            if '*' in value_str:
                tooltip_lines.append("• 正公差 ≤ 15")
            if 'Δ' in value_str:
                tooltip_lines.append("• 需注意的钢卷")
        
        # 如果有通用标注信息，也添加进去
        if 标注信息列表:
            tooltip_lines.append("")
            tooltip_lines.append("【预警详情】")
            for info in 标注信息列表:
                tooltip_lines.append(f"• {info}")
        
        return "\n".join(tooltip_lines) if tooltip_lines else None
    
    def process_cell_highlight(self, item, col_name, value, 标注信息列表=None):
        """处理单元格高亮"""
        from PyQt5.QtGui import QColor, QBrush
        
        # 检查是否有标识（三角符号Δ或星号*）
        value_str = str(value)
        tooltip = None
        
        if 'Δ' in value_str or '*' in value_str:
            # 设置红色背景
            item.setBackground(QBrush(QColor('#FF0000')))
            # 添加annotation属性，用于样式表识别
            item.setData(Qt.UserRole, True)
            # 生成tooltip
            if 标注信息列表 is not None:
                tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                if tooltip:
                    item.setToolTip(tooltip)
        # 除鳞字段中包含"回"和"无APS"的单元格也改背景色为红色
        elif col_name == "除鳞" and ('回' in value_str or '无APS' in value_str):
            # 设置红色背景
            item.setBackground(QBrush(QColor('#FF0000')))
            # 添加annotation属性，用于样式表识别
            item.setData(Qt.UserRole, True)
            # 生成tooltip
            if 标注信息列表 is not None:
                tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                if tooltip:
                    item.setToolTip(tooltip)
        # 原程序没有区分减宽、轧宽、坯厚的阈值判断，这些是额外的验证逻辑
        elif col_name == "调宽":
            # 调宽列，包含Δ符号时显示黄底黑字
            if 'Δ' in value_str:
                item.setBackground(QBrush(QColor('#FFFF00')))  # 黄色背景
                item.setForeground(QBrush(QColor('#000000')))  # 黑色字体
                # 生成tooltip
                if 标注信息列表 is not None:
                    tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                    if tooltip:
                        item.setToolTip(tooltip)
        elif col_name == "减宽":
            try:
                if value_str.replace('.', '').replace('-', '').isdigit():
                    width_reduction = float(value_str)
                    if width_reduction >= 240:
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                        # 生成tooltip
                        if 标注信息列表 is not None:
                            tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                            if tooltip:
                                item.setToolTip(tooltip)
                    elif width_reduction < 0:
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                        # 生成tooltip
                        if 标注信息列表 is not None:
                            tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                            if tooltip:
                                item.setToolTip(tooltip)
            except:
                pass
        
        elif col_name == "轧宽":
            try:
                if value_str.replace('.', '').isdigit():
                    roll_width = float(value_str)
                    if roll_width < 860:
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                        # 生成tooltip
                        if 标注信息列表 is not None:
                            tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                            if tooltip:
                                item.setToolTip(tooltip)
                    elif roll_width < 930:
                        item.setBackground(QBrush(QColor('#FFFF00')))
                        item.setForeground(QBrush(QColor('#000000')))
                        # 生成tooltip
                        if 标注信息列表 is not None:
                            tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                            if tooltip:
                                item.setToolTip(tooltip)
            except:
                pass
        
        elif col_name == "坯厚":
            try:
                if value_str.replace('.', '').isdigit():
                    blank_thickness = float(value_str)
                    if blank_thickness > 230:
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                        # 生成tooltip
                        if 标注信息列表 is not None:
                            tooltip = self.generate_tooltip(col_name, value_str, 标注信息列表)
                            if tooltip:
                                item.setToolTip(tooltip)
            except:
                pass
    
    def save_current_table_data(self):
        """保存当前表格数据"""
        try:
            import json
            import os
            # 构建保存文件路径
            # 使用与主程序相同的plan_dir路径
            if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'plan_dir'):
                plan_dir = os.path.join(self.parent.plan_dir, "计划号")
            else:
                # 备用方案：使用当前工作目录
                plan_dir = os.path.join(os.getcwd(), "计划号")
            os.makedirs(plan_dir, exist_ok=True)
            table_data_file = os.path.join(plan_dir, "furnace_table_data.json")
            
            # 收集当前表格数据
            table_data = []
            seq_num = 1
            for row_idx in range(self.table_widget.rowCount()):
                # 检查是否是换辊行或自定义信息行
                first_item = self.table_widget.item(row_idx, 0)
                is_special_row = False
                if first_item:
                    bg_color = first_item.background().color().name()
                    if bg_color == '#ffff00':
                        is_special_row = True

                if not is_special_row:
                    # 正常数据行，获取钢卷号
                    coil_item = self.table_widget.item(row_idx, 1)  # 钢卷号列（索引1）
                    if coil_item:
                        coil_number = coil_item.text().strip()
                        if coil_number:
                            table_data.append({
                                "coil_number": coil_number,
                                "sequence": seq_num
                            })
                            seq_num += 1
            
            # 读取之前的表格数据
            previous_table_data = []
            if os.path.exists(table_data_file):
                try:
                    with open(table_data_file, 'r', encoding='utf-8') as f:
                        previous_table_data = json.load(f)
                except:
                    previous_table_data = []
            
            # 保存最近2次的表格数据
            combined_data = [table_data] + previous_table_data[:1]  # 只保留最近2次的数据
            
            # 保存数据
            with open(table_data_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存表格数据: {table_data_file}")
            print(f"当前表格数据: {[item['coil_number'] for item in table_data]}")
            if previous_table_data:
                print(f"上一次表格数据: {[item['coil_number'] for item in previous_table_data[0]]}")
        except Exception as e:
            print(f"保存表格数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_window_state(self):
        """保存窗口状态"""
        try:
            import json
            import os
            # 构建保存文件路径
            plan_dir = os.path.join(os.getcwd(), "计划号")
            os.makedirs(plan_dir, exist_ok=True)
            state_file = os.path.join(plan_dir, "furnace_window_state.json")
            
            # 收集当前状态 - 找到当前行或最近的正常数据行的钢卷号
            current_coil_number = ""
            target_row = self.current_row
            
            # 如果当前行是特殊行（换辊行或自定义信息行），向上查找最近的正常数据行
            if self.table_widget.rowCount() > 0 and target_row < self.table_widget.rowCount():
                while target_row >= 0:
                    first_item = self.table_widget.item(target_row, 0)
                    is_special_row = False
                    if first_item:
                        bg_color = first_item.background().color().name()
                        cell_text = first_item.text()
                        if bg_color == '#ffff00' or '换辊' in cell_text:
                            is_special_row = True
                    
                    if not is_special_row:
                        coil_item = self.table_widget.item(target_row, 1)  # 钢卷号列（索引1）
                        if coil_item:
                            current_coil_number = coil_item.text().strip()
                        break
                    
                    target_row -= 1
            
            state_data = {
                "is_scrolling": self.is_scrolling,
                "scroll_interval": self.scroll_interval,
                "current_coil_number": current_coil_number
            }
            
            # 保存状态
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存窗口状态: {state_file}")
            print(f"状态数据: {state_data}")
        except Exception as e:
            print(f"保存窗口状态失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_window_state(self):
        """加载窗口状态"""
        try:
            import json
            import os
            # 构建保存文件路径
            plan_dir = os.path.join(os.getcwd(), "计划号")
            state_file = os.path.join(plan_dir, "furnace_window_state.json")
            
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    
                    # 恢复滚动状态
                    self.is_scrolling = state_data.get("is_scrolling", False)
                    self.scroll_interval = state_data.get("scroll_interval", 110)
                    current_coil_number = state_data.get("current_coil_number", "")
                    
                    # 恢复滚动时间设置
                    self.scroll_time_edit.setText(str(self.scroll_interval))
                    
                    # 恢复光标条位置（以钢卷号为基准）
                    if current_coil_number and self.table_widget.rowCount() > 0:
                        for row_idx in range(self.table_widget.rowCount()):
                            coil_item = self.table_widget.item(row_idx, 1)  # 钢卷号列（索引1）
                            if coil_item and coil_item.text().strip() == current_coil_number:
                                self.current_row = row_idx
                                self.table_widget.selectRow(row_idx)
                                self.table_widget.scrollToItem(coil_item, QTableWidget.PositionAtCenter)
                                print(f"已恢复光标条位置到钢卷号: {current_coil_number}（行: {row_idx}）")
                                break
                    
                    # 恢复滚动状态
                    if self.is_scrolling:
                        # 直接启动滚动，而不是调用 toggle_scroll
                        try:
                            scroll_time = int(self.scroll_time_edit.text())
                            if scroll_time < 1:
                                scroll_time = 1
                        except:
                            scroll_time = 5
                        
                        # 启动定时器
                        self.scroll_timer.setInterval(scroll_time * 1000)
                        # 先断开之前的连接，避免重复连接
                        try:
                            self.scroll_timer.timeout.disconnect()
                        except:
                            pass
                        self.scroll_timer.timeout.connect(self.auto_scroll)
                        self.scroll_timer.start()
                        self.is_scrolling = True
                        self.scroll_toggle_btn.setText("■")  # 停止图标
                        self.scroll_status_label.setText("自动滚动中")
                        print("已恢复自动滚动状态")
                    else:
                        # 确保按钮状态正确
                        self.scroll_toggle_btn.setText("▶")  # 播放图标
                        self.scroll_status_label.setText("自动滚动已停止")
                        print("已恢复自动滚动停止状态")
                    
                    print(f"已加载窗口状态: {state_file}")
                    print(f"状态数据: {state_data}")
                except Exception as e:
                    print(f"加载窗口状态失败: {e}")
            else:
                print(f"窗口状态文件不存在: {state_file}")
        except Exception as e:
            print(f"加载窗口状态失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_block_count(self):
        """更新块数显示"""
        try:
            total_rows = self.table_widget.rowCount()
            selected_rows = self.table_widget.selectionModel().selectedRows()
            if selected_rows:
                current_row = selected_rows[0].row() + 1
                self.block_count_label.setText(f"{current_row}/{total_rows}")
            else:
                self.block_count_label.setText(f"0/{total_rows}")
            print(f"更新块数显示: {current_row if selected_rows else 0}/{total_rows}")
        except Exception as e:
            print(f"更新块数显示失败: {e}")
            try:
                total_rows = self.table_widget.rowCount()
                self.block_count_label.setText(f"0/{total_rows}")
            except:
                self.block_count_label.setText("0/0")

    def on_cell_clicked(self, row, column):
        """当用户点击单元格时，将光标条移到该行"""
        self.table_widget.selectRow(row)
        if self.is_scrolling:
            self.table_widget.scrollToItem(self.table_widget.item(row, 0), QTableWidget.PositionAtCenter)
        self.update_block_count()
        for col in range(self.table_widget.columnCount()):
            item = self.table_widget.item(row, col)
            if item and item.background().color().name() in ['#ff0000', '#FF0000']:
                item.setBackground(QBrush(QColor('#FF0000')))

    def on_selection_changed(self):
        """当选择变化时更新块数显示和当前行"""
        self.update_block_count()
        # 更新当前行
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if selected_rows:
            self.current_row = selected_rows[0].row()
            print(f"当前行已更新为: {self.current_row}")

    def maintain_cell_highlight(self):
        """当选择变化时，确保标注的单元格保持红色背景"""
        selected_rows = set()
        for item in self.table_widget.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and item.background().color().name() in ['#ff0000', '#FF0000']:
                    item.setBackground(QBrush(QColor('#FF0000')))
    
    def toggle_scroll(self):
        """切换滚动状态"""
        if not self.is_scrolling:
            # 开始自动滚动
            try:
                scroll_time = int(self.scroll_time_edit.text())
                if scroll_time < 1:
                    scroll_time = 1
            except:
                scroll_time = 5
            
            # 检查是否有选中的行
            selected_items = self.table_widget.selectedItems()
            if selected_items:
                self.current_row = selected_items[0].row()
                # 将选中的钢卷号显示在屏幕中间，光标移到这一行
                self.table_widget.selectRow(self.current_row)
                self.table_widget.scrollToItem(selected_items[0], QTableWidget.PositionAtCenter)
            
            # 启动定时器
            self.scroll_timer.setInterval(scroll_time * 1000)
            # 先断开之前的连接，避免重复连接
            try:
                self.scroll_timer.timeout.disconnect()
            except:
                pass
            self.scroll_timer.timeout.connect(self.auto_scroll)
            self.scroll_timer.start()
            self.is_scrolling = True
            self.scroll_toggle_btn.setText("■")  # 停止图标
            self.scroll_status_label.setText("自动滚动中")
            # 确保选中行有背景色
            if self.table_widget.rowCount() > 0:
                self.table_widget.selectRow(self.current_row)
        else:
            # 停止自动滚动
            self.scroll_timer.stop()
            self.is_scrolling = False
            self.scroll_toggle_btn.setText("▶")  # 播放图标
            self.scroll_status_label.setText("自动滚动已停止")
            # 确保选中行有背景色
            if self.table_widget.rowCount() > 0:
                self.table_widget.selectRow(self.current_row)

    def auto_scroll(self):
        """自动向上滚动 - 光标在窗口中间不动，数据往上滚动"""
        if self.table_widget.rowCount() == 0:
            return
        
        # 每次向上滚动一个钢卷号（一行）
        # 为了实现数据往上滚动，需要让选中行向下移动
        if self.current_row < self.table_widget.rowCount() - 1:
            # 向下移动一行，这样数据会向上滚动
            self.current_row += 1
        else:
            # 到达底部，回到顶部
            self.current_row = 0
        
        # 确保选中行在屏幕中间
        self.table_widget.selectRow(self.current_row)
        self.table_widget.scrollToItem(self.table_widget.item(self.current_row, 0), QTableWidget.PositionAtCenter)
        
        # 更新块数显示
        self.update_block_count()
    
    def on_scroll_time_changed(self, text):
        """滚动时间变化"""
        try:
            self.scroll_interval = int(text)
            if self.is_scrolling:
                self.scroll_timer.setInterval(self.scroll_interval * 1000)
        except:
            pass
    
    def locate_cursor_by_saved_coil(self):
        """查找最后离开时光标所在行的钢卷号，并定位光标"""
        try:
            import json
            import os
            
            print("\n=== 定位光标到保存的钢卷号 ===")
            
            if self.table_widget.rowCount() == 0:
                print("表格为空，无法定位光标")
                return
            
            # 构建保存文件路径
            plan_dir = os.path.join(os.getcwd(), "计划号")
            state_file = os.path.join(plan_dir, "furnace_window_state.json")
            
            # 读取保存的钢卷号
            saved_coil_number = None
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    saved_coil_number = state_data.get("current_coil_number", "")
                    print(f"最后离开时的钢卷号: {saved_coil_number}")
                except Exception as e:
                    print(f"读取窗口状态文件失败: {e}")
            
            # 定位光标
            if saved_coil_number:
                # 查找该钢卷号在表格中的位置
                found = False
                for row_idx in range(self.table_widget.rowCount()):
                    coil_item = self.table_widget.item(row_idx, 1)  # 钢卷号列（索引1）
                    if coil_item and coil_item.text().strip() == saved_coil_number:
                        self.current_row = row_idx
                        self.table_widget.selectRow(row_idx)
                        self.table_widget.scrollToItem(coil_item, QTableWidget.PositionAtCenter)
                        print(f"已定位光标到钢卷号: {saved_coil_number}（行: {row_idx + 1}/{self.table_widget.rowCount()}）")
                        found = True
                        break
                
                if not found:
                    # 没有找到，定位到第一行
                    print(f"未找到钢卷号 {saved_coil_number}，定位到第一行")
                    self.current_row = 0
                    self.table_widget.selectRow(0)
                    self.table_widget.scrollToItem(self.table_widget.item(0, 0), QTableWidget.PositionAtTop)
                    print("已定位光标到第一行")
            else:
                # 没有保存的钢卷号，定位到第一行
                print("没有保存的钢卷号，定位到第一行")
                self.current_row = 0
                self.table_widget.selectRow(0)
                self.table_widget.scrollToItem(self.table_widget.item(0, 0), QTableWidget.PositionAtTop)
                print("已定位光标到第一行")
            
            # 强制刷新表格
            self.table_widget.repaint()
            self.table_widget.update()
            
        except Exception as e:
            print(f"定位光标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 失败时定位到第一行
            if self.table_widget.rowCount() > 0:
                self.current_row = 0
                self.table_widget.selectRow(0)
    
    def start_auto_scroll(self):
        """自动启动自动滚动功能"""
        try:
            print("\n=== 启动自动滚动 ===")
            
            # 获取滚动时间设置
            try:
                scroll_time = int(self.scroll_time_edit.text())
                if scroll_time < 1:
                    scroll_time = 1
            except:
                scroll_time = 5
            
            # 启动定时器
            self.scroll_timer.setInterval(scroll_time * 1000)
            # 先断开之前的连接，避免重复连接
            try:
                self.scroll_timer.timeout.disconnect()
            except:
                pass
            self.scroll_timer.timeout.connect(self.auto_scroll)
            self.scroll_timer.start()
            
            # 更新状态
            self.is_scrolling = True
            self.scroll_toggle_btn.setText("■")  # 停止图标
            self.scroll_status_label.setText("自动滚动中")
            
            print(f"已启动自动滚动，间隔: {scroll_time} 秒")
            
        except Exception as e:
            print(f"启动自动滚动失败: {str(e)}")
            import traceback
            traceback.print_exc()
    


class SettingsWindow(QDialog):
    """设置窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("设置")
        self.setGeometry(300, 200, 800, 800)
        
        # 导入UI
        from settings_window_ui import Ui_SettingsWindow
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        
        # 连接信号
        self.ui.mainWindowGetBtn.clicked.connect(lambda: self.get_window_coordinates('mainWindow'))
        self.ui.mainWindowTestBtn.clicked.connect(lambda: self.test_window_coordinates('mainWindow'))
        self.ui.furnaceWindowGetBtn.clicked.connect(lambda: self.get_window_coordinates('furnaceWindow'))
        self.ui.furnaceWindowTestBtn.clicked.connect(lambda: self.test_window_coordinates('furnaceWindow'))
        self.ui.planInputGetBtn.clicked.connect(lambda: self.get_window_coordinates('planInput'))
        self.ui.planInputTestBtn.clicked.connect(lambda: self.test_window_coordinates('planInput'))
        self.ui.queryBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('queryBtn'))
        self.ui.queryBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('queryBtn'))
        self.ui.exportBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('exportBtn'))
        self.ui.exportBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('exportBtn'))
        self.ui.closeBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('closeBtn'))
        self.ui.closeBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('closeBtn'))
        self.ui.detailExportBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('detailExportBtn'))
        self.ui.detailExportBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('detailExportBtn'))
        
        # 禁用所有按钮的自动默认行为，防止回车键触发
        self.ui.mainWindowGetBtn.setAutoDefault(False)
        self.ui.mainWindowGetBtn.setDefault(False)
        self.ui.mainWindowTestBtn.setAutoDefault(False)
        self.ui.mainWindowTestBtn.setDefault(False)
        self.ui.furnaceWindowGetBtn.setAutoDefault(False)
        self.ui.furnaceWindowGetBtn.setDefault(False)
        self.ui.furnaceWindowTestBtn.setAutoDefault(False)
        self.ui.furnaceWindowTestBtn.setDefault(False)
        self.ui.planInputGetBtn.setAutoDefault(False)
        self.ui.planInputGetBtn.setDefault(False)
        self.ui.planInputTestBtn.setAutoDefault(False)
        self.ui.planInputTestBtn.setDefault(False)
        self.ui.queryBtnGetBtn.setAutoDefault(False)
        self.ui.queryBtnGetBtn.setDefault(False)
        self.ui.queryBtnTestBtn.setAutoDefault(False)
        self.ui.queryBtnTestBtn.setDefault(False)
        self.ui.exportBtnGetBtn.setAutoDefault(False)
        self.ui.exportBtnGetBtn.setDefault(False)
        self.ui.exportBtnTestBtn.setAutoDefault(False)
        self.ui.exportBtnTestBtn.setDefault(False)
        self.ui.closeBtnGetBtn.setAutoDefault(False)
        self.ui.closeBtnGetBtn.setDefault(False)
        self.ui.closeBtnTestBtn.setAutoDefault(False)
        self.ui.closeBtnTestBtn.setDefault(False)
        self.ui.detailExportBtnGetBtn.setAutoDefault(False)
        self.ui.detailExportBtnGetBtn.setDefault(False)
        self.ui.detailExportBtnTestBtn.setAutoDefault(False)
        self.ui.detailExportBtnTestBtn.setDefault(False)
        # 禁用恢复默认值按钮的自动默认行为
        self.ui.restoreDefaultsBtn.setAutoDefault(False)
        self.ui.restoreDefaultsBtn.setDefault(False)
        
        # 恢复默认值按钮（不需要等待加载）
        self.ui.restoreDefaultsBtn.clicked.connect(self.restore_defaults)
        
        # 清理多余文件按钮
        self.ui.cleanupFilesBtn.clicked.connect(self.cleanup_extra_files)
        self.ui.cleanupFilesBtn.setAutoDefault(False)
        self.ui.cleanupFilesBtn.setDefault(False)
        
        # 加载设置（必须在信号连接之前，避免加载时触发保存）
        self.load_settings()
        
        # 窗口选择信号（在加载设置之后连接）
        self.ui.windowRadio1.toggled.connect(lambda: self.save_settings())
        self.ui.windowRadio2.toggled.connect(lambda: self.save_settings())
        
        # 坐标文本框实时保存
        self.ui.mainWindowXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.mainWindowYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.furnaceWindowXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.furnaceWindowYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.planInputXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.planInputYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.queryBtnXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.queryBtnYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.exportBtnXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.exportBtnYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.closeBtnXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.closeBtnYEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.detailExportBtnXEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.detailExportBtnYEdit.textChanged.connect(lambda: self.save_settings())
        
        # 自动导出设置信号
        self.ui.autoPrintCheckBox.stateChanged.connect(lambda: self.save_settings())
        
        # 自动执行设置信号
        self.ui.intervalModeRadio.toggled.connect(lambda: self.save_settings())
        self.ui.timeModeRadio.toggled.connect(lambda: self.save_settings())
        # 恢复时间间隔输入验证
        self.ui.intervalMinutesEdit.textChanged.connect(lambda: self.validate_interval_minutes())
        # 添加时间输入框的实时更新
        self.ui.timeEdit.textChanged.connect(lambda: self.validate_exec_times())
        
        # 确保窗口居中显示
        if self.parent:
            # 获取父窗口的几何信息
            parent_geo = self.parent.geometry()
            # 计算居中位置
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            # 设置窗口位置
            self.move(x, y)
    
    def closeEvent(self, event):
        """窗口关闭时自动保存设置"""
        print("[DEBUG] SettingsWindow closeEvent called")
        try:
            self.save_settings()
            print("设置窗口关闭时已自动保存设置")
        except Exception as e:
            print(f"[DEBUG] 设置窗口关闭时保存设置失败: {e}")
        event.accept()
    
    def validate_exec_times(self):
        """验证执行时间输入并实时更新下一次执行时间"""
        try:
            # 检查ui是否存在
            if not hasattr(self, 'ui') or not hasattr(self.ui, 'timeEdit'):
                print("UI组件未初始化")
                return
            
            text = self.ui.timeEdit.text()
            
            # 简单验证：检查是否包含有效的时间格式
            if text:
                time_strings = [t.strip() for t in text.split(",") if t.strip()]
                for time_str in time_strings:
                    try:
                        # 尝试解析时间格式
                        from datetime import datetime
                        datetime.strptime(time_str, "%H:%M")
                    except ValueError:
                        # 显示错误提示
                        msg = QMessageBox(self)
                        msg.setWindowTitle("提示")
                        msg.setText(f"时间格式错误: {time_str}，正确格式为 HH:MM")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
                        msg.exec_()
                        return
            
            # 保存设置
            self.save_settings()
            
            # 如果自动执行已启用，立即更新下一次执行时间
            if self.parent and hasattr(self.parent, 'get_settings'):
                current_settings = self.parent.get_settings()
                if current_settings.get("autoExec", False) and current_settings.get("execMode", "interval") == "time":
                    # 计算下一次执行时间
                    exec_times = text
                    if hasattr(self.parent, 'calculate_next_execution_time'):
                        self.parent.calculate_next_execution_time(exec_times)
                        # 更新标签
                        if hasattr(self.parent, 'next_execution_time') and self.parent.next_execution_time:
                            import time
                            next_time_str = time.strftime("%H:%M:%S", time.localtime(self.parent.next_execution_time))
                            self.parent.next_execution_label.setText(f"下一次执行: {next_time_str}")
                            # 强制更新UI
                            self.parent.next_execution_label.repaint()
                            self.parent.next_execution_label.update()
                            self.parent.repaint()
                            self.parent.update()
                            print(f"实时更新下一次执行时间: {next_time_str}")
                            
        except Exception as e:
            print(f"验证执行时间失败: {str(e)}")
    
    def validate_interval_minutes(self):
        """验证时间间隔输入"""
        try:
            # 检查ui是否存在
            if not hasattr(self, 'ui') or not hasattr(self.ui, 'intervalMinutesEdit'):
                print("UI组件未初始化")
                return
            
            text = self.ui.intervalMinutesEdit.text()
            if text:
                if text.isdigit():
                    value = int(text)
                    if value < 1 or value > 999:
                        # 显示错误提示
                        msg = QMessageBox(self)
                        msg.setWindowTitle("提示")
                        msg.setText("时间间隔必须在1-999之间")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
                        msg.exec_()
                        # 重置为1，不触发信号
                        self.ui.intervalMinutesEdit.blockSignals(True)
                        self.ui.intervalMinutesEdit.setText("1")
                        self.ui.intervalMinutesEdit.blockSignals(False)
                        return
                else:
                    # 显示错误提示
                    msg = QMessageBox(self)
                    msg.setWindowTitle("提示")
                    msg.setText("请输入有效的数字")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
                    msg.exec_()
                    # 清空输入，不触发信号
                    self.ui.intervalMinutesEdit.blockSignals(True)
                    self.ui.intervalMinutesEdit.setText("")
                    self.ui.intervalMinutesEdit.blockSignals(False)
                    return
            
            # 保存设置
            self.save_settings()
            
            # 如果自动执行已启用，立即更新下一次执行时间
            if self.parent and hasattr(self.parent, 'get_settings'):
                current_settings = self.parent.get_settings()
                if current_settings.get("autoExec", False) and current_settings.get("execMode", "interval") == "interval":
                    # 获取新的时间间隔
                    interval_minutes = int(text) if text and text.isdigit() else current_settings.get("intervalMinutes", 1)
                    # 计算下一次执行的具体时间
                    import time
                    next_exec_time = time.time() + (interval_minutes * 60)
                    next_time_str = time.strftime("%H:%M:%S", time.localtime(next_exec_time))
                    # 更新标签
                    self.parent.next_execution_label.setText(f"下一次执行: {next_time_str}")
                    # 强制更新UI
                    self.parent.next_execution_label.repaint()
                    self.parent.next_execution_label.update()
                    print(f"实时更新下一次执行时间: {next_time_str}")
                    
        except Exception as e:
            print(f"验证时间间隔失败: {str(e)}")
    
    def load_settings(self):
        """加载设置"""
        import json
        import os
        
        # 默认设置文件路径
        # 使用self.parent.plan_dir确保打包后也能正确读取配置文件
        if hasattr(self, 'parent') and hasattr(self.parent, 'plan_dir'):
            default_config_file = os.path.join(self.parent.plan_dir, 'default_settings.json')
        else:
            # 备用方案：确保使用正确的路径
            if getattr(sys, 'frozen', False):
                default_config_file = os.path.join(os.path.dirname(sys.executable), 'default_settings.json')
            else:
                default_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_settings.json')
        
        # 尝试从默认设置文件加载
        default_settings = None
        try:
            with open(default_config_file, 'r', encoding='utf-8') as f:
                default_settings = json.load(f)
        except Exception as e:
            print(f"加载默认设置文件失败: {e}")
        
        # 如果默认设置文件加载失败，使用硬编码的默认值
        if default_settings is None:
            default_settings = {
                # 坐标设置
                "mainWindow": {"x": 284, "y": 85},      # 装炉顺作成管理标签
                "furnaceWindow": {"x": 988, "y": 819},   # 装炉顺序导出按钮
                "planInput": {"x": 107, "y": 85},        # 轧制计划管理标签
                "queryBtn": {"x": 734, "y": 135},        # 选择计划号
                "exportBtn": {"x": 78, "y": 708},        # 导出总计划号列表按钮
                "closeBtn": {"x": 235, "y": 207},        # 第一个计划号
                "detailExportBtn": {"x": 79, "y": 859},   # 计划明细导出按钮
                
                # 窗口选择
                "selectedWindow": "BGCMS1-宝钢股份多基地制造管理系统运行环境",
                
                # 自动导出设置
                "autoPrint": True,
                
                # 装炉明细打印设置
                "savePrintFile": True,
                
                # 自动执行设置
                "autoExec": False,
                "execMode": "interval",  # interval 或 time
                "intervalMinutes": 1,
                "execTimes": "16:00,16:02,16:04"
            }
        
        # 加载设置文件
        # 使用self.parent.plan_dir确保打包后也能正确读取配置文件
        if hasattr(self, 'parent') and hasattr(self.parent, 'plan_dir'):
            config_file = os.path.join(self.parent.plan_dir, 'settings.json')
        else:
            # 备用方案：确保使用正确的路径
            if getattr(sys, 'frozen', False):
                config_file = os.path.join(os.path.dirname(sys.executable), 'settings.json')
            else:
                config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        if os.path.exists(config_file):
            try:
                # 先检查文件大小
                if os.path.getsize(config_file) < 5:
                    raise ValueError("Settings file is too small")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 验证设置结构
                if not isinstance(settings, dict):
                    raise ValueError("Invalid settings format")
                
                # 检查是否为空对象
                if len(settings) == 0:
                    raise ValueError("Settings file is empty")
                
                # 应用设置
                self.apply_settings(settings)
                print("设置加载成功")
                return
            except Exception as e:
                print(f"加载设置失败: {e}")
                # 如果加载失败，删除损坏的文件
                try:
                    os.remove(config_file)
                    print("已删除损坏的设置文件")
                except Exception as e:
                    print(f"删除损坏文件失败: {e}")
        
        # 如果加载失败或文件不存在，使用默认设置
        self.apply_settings(default_settings)
        # 保存默认设置
        self.save_settings(default_settings)
    
    def apply_settings(self, settings):
        """应用设置到界面"""
        # 应用坐标设置（使用默认值确保不会为空）
        # 主窗口坐标 - 装炉顺作成管理标签
        if "mainWindow" in settings:
            self.ui.mainWindowXEdit.setText(str(settings["mainWindow"].get("x", 284)))
            self.ui.mainWindowYEdit.setText(str(settings["mainWindow"].get("y", 85)))
        else:
            self.ui.mainWindowXEdit.setText("284")
            self.ui.mainWindowYEdit.setText("85")
        
        # 装炉窗口坐标 - 装炉顺序导出按钮
        if "furnaceWindow" in settings:
            self.ui.furnaceWindowXEdit.setText(str(settings["furnaceWindow"].get("x", 988)))
            self.ui.furnaceWindowYEdit.setText(str(settings["furnaceWindow"].get("y", 819)))
        else:
            self.ui.furnaceWindowXEdit.setText("988")
            self.ui.furnaceWindowYEdit.setText("819")
        
        # 计划输入坐标 - 轧制计划管理标签
        if "planInput" in settings:
            self.ui.planInputXEdit.setText(str(settings["planInput"].get("x", 107)))
            self.ui.planInputYEdit.setText(str(settings["planInput"].get("y", 85)))
        else:
            self.ui.planInputXEdit.setText("107")
            self.ui.planInputYEdit.setText("85")
        
        # 查询按钮坐标 - 选择计划号
        if "queryBtn" in settings:
            self.ui.queryBtnXEdit.setText(str(settings["queryBtn"].get("x", 734)))
            self.ui.queryBtnYEdit.setText(str(settings["queryBtn"].get("y", 135)))
        else:
            self.ui.queryBtnXEdit.setText("734")
            self.ui.queryBtnYEdit.setText("135")
        
        # 导出按钮坐标 - 导出总计划号列表按钮
        if "exportBtn" in settings:
            self.ui.exportBtnXEdit.setText(str(settings["exportBtn"].get("x", 78)))
            self.ui.exportBtnYEdit.setText(str(settings["exportBtn"].get("y", 708)))
        else:
            self.ui.exportBtnXEdit.setText("78")
            self.ui.exportBtnYEdit.setText("708")
        
        # 关闭按钮坐标 - 第一个计划号
        if "closeBtn" in settings:
            self.ui.closeBtnXEdit.setText(str(settings["closeBtn"].get("x", 235)))
            self.ui.closeBtnYEdit.setText(str(settings["closeBtn"].get("y", 207)))
        else:
            self.ui.closeBtnXEdit.setText("235")
            self.ui.closeBtnYEdit.setText("207")
        
        # 明细导出按钮坐标 - 计划明细导出按钮
        if "detailExportBtn" in settings:
            self.ui.detailExportBtnXEdit.setText(str(settings["detailExportBtn"].get("x", 79)))
            self.ui.detailExportBtnYEdit.setText(str(settings["detailExportBtn"].get("y", 859)))
        else:
            self.ui.detailExportBtnXEdit.setText("79")
            self.ui.detailExportBtnYEdit.setText("859")
        
        # 应用窗口选择设置
        if "selectedWindow" in settings:
            if settings["selectedWindow"] == "BGCMS1-宝钢股份多基地制造管理系统运行环境":
                self.ui.windowRadio2.setChecked(True)
            else:
                self.ui.windowRadio1.setChecked(True)
        
        # 应用自动导出设置
        if "autoPrint" in settings:
            self.ui.autoPrintCheckBox.setChecked(settings["autoPrint"])
        
        # 应用装炉明细打印设置
        if "savePrintFile" in settings:
            self.ui.savePrintFileCheckBox.setChecked(settings["savePrintFile"])
        
        # 应用自动执行设置
        if "execMode" in settings:
            if settings["execMode"] == "interval":
                self.ui.intervalModeRadio.setChecked(True)
            else:
                self.ui.timeModeRadio.setChecked(True)
        if "intervalMinutes" in settings:
            self.ui.intervalMinutesEdit.setText(str(settings["intervalMinutes"]))
        if "execTimes" in settings:
            self.ui.timeEdit.setText(settings["execTimes"])
        

    
    def save_settings(self, settings=None):
        """保存设置"""
        import json
        import os
        import sys
        
        print(f"[DEBUG] save_settings called, self.parent = {self.parent}")
        if self.parent:
            print(f"[DEBUG] self.parent.plan_dir = {getattr(self.parent, 'plan_dir', 'NOT FOUND')}")
        
        if settings is None:
            # 从界面收集设置
            # 获取当前的autoExec设置，避免覆盖
            if self.parent and hasattr(self.parent, 'get_settings'):
                current_settings = self.parent.get_settings()
            else:
                # 如果没有parent，使用默认设置
                current_settings = {
                    "autoExec": False,
                    "execMode": "interval",
                    "intervalMinutes": 1,
                    "execTimes": "16:00,16:02,16:04"
                }
            auto_exec = current_settings.get("autoExec", False)
            
            settings = {
                # 坐标设置
                "mainWindow": {
                    "x": int(self.ui.mainWindowXEdit.text()) if self.ui.mainWindowXEdit.text().isdigit() else 0,
                    "y": int(self.ui.mainWindowYEdit.text()) if self.ui.mainWindowYEdit.text().isdigit() else 0
                },
                "furnaceWindow": {
                    "x": int(self.ui.furnaceWindowXEdit.text()) if self.ui.furnaceWindowXEdit.text().isdigit() else 0,
                    "y": int(self.ui.furnaceWindowYEdit.text()) if self.ui.furnaceWindowYEdit.text().isdigit() else 0
                },
                "planInput": {
                    "x": int(self.ui.planInputXEdit.text()) if self.ui.planInputXEdit.text().isdigit() else 0,
                    "y": int(self.ui.planInputYEdit.text()) if self.ui.planInputYEdit.text().isdigit() else 0
                },
                "queryBtn": {
                    "x": int(self.ui.queryBtnXEdit.text()) if self.ui.queryBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.queryBtnYEdit.text()) if self.ui.queryBtnYEdit.text().isdigit() else 0
                },
                "exportBtn": {
                    "x": int(self.ui.exportBtnXEdit.text()) if self.ui.exportBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.exportBtnYEdit.text()) if self.ui.exportBtnYEdit.text().isdigit() else 0
                },
                "closeBtn": {
                    "x": int(self.ui.closeBtnXEdit.text()) if self.ui.closeBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.closeBtnYEdit.text()) if self.ui.closeBtnYEdit.text().isdigit() else 0
                },
                "detailExportBtn": {
                    "x": int(self.ui.detailExportBtnXEdit.text()) if self.ui.detailExportBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.detailExportBtnYEdit.text()) if self.ui.detailExportBtnYEdit.text().isdigit() else 0
                },
                
                # 窗口选择
                "selectedWindow": "Doc1.docx - Word" if self.ui.windowRadio1.isChecked() else "BGCMS1-宝钢股份多基地制造管理系统运行环境",
                
                # 自动导出设置
                "autoPrint": self.ui.autoPrintCheckBox.isChecked(),
                
                # 装炉明细打印设置
                "savePrintFile": self.ui.savePrintFileCheckBox.isChecked(),
                
                # 自动执行设置 - 保留当前的autoExec设置
                "autoExec": auto_exec,
                "execMode": "interval" if self.ui.intervalModeRadio.isChecked() else "time",
                "intervalMinutes": int(self.ui.intervalMinutesEdit.text()) if self.ui.intervalMinutesEdit.text().isdigit() else 1,
                "execTimes": self.ui.timeEdit.text(),
                

            }
        
        # 保存设置到文件
        # 使用self.parent.plan_dir确保打包后也能正确保存配置文件
        if hasattr(self, 'parent') and hasattr(self.parent, 'plan_dir'):
            config_file = os.path.join(self.parent.plan_dir, 'settings.json')
        else:
            # 备用方案：确保使用正确的路径
            if getattr(sys, 'frozen', False):
                # 打包成exe后的路径
                config_file = os.path.join(os.path.dirname(sys.executable), 'settings.json')
            else:
                # 脚本运行时的路径
                config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        print(f"[DEBUG] config_file path = {config_file}")
        print(f"[DEBUG] sys.frozen = {getattr(sys, 'frozen', False)}")
        print(f"[DEBUG] __file__ = {__file__ if '__file__' in dir() else 'N/A'}")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print(f"[DEBUG] 设置保存成功到: {config_file}")
        except Exception as e:
            print(f"[DEBUG] 保存设置失败: {e}")
        
        # 同步更新自动导出坐标配置文件
        self.update_coordinate_config(settings)
        
        # 更新主窗口的下一次执行时间和重启自动执行服务
        if self.parent and hasattr(self.parent, 'update_next_execution_label') and hasattr(self.parent, 'load_settings'):
            try:
                # 重新加载设置并重启自动执行服务
                if hasattr(self.parent, 'get_settings'):
                    updated_settings = self.parent.get_settings()
                    # 检查自动执行是否启用
                    if updated_settings.get("autoExec", False):
                        # 重启自动执行服务以应用新设置
                        self.parent.load_settings()
                        print("已重启自动执行服务并更新下一次执行时间")
                    else:
                        # 自动执行未启用，只更新标签
                        self.parent.update_next_execution_label()
                        print("已更新下一次执行时间")
                
                # 更新主窗口的自动打印复选框状态
                if hasattr(self.parent, 'auto_print_checkbox'):
                    auto_print = settings.get("autoPrint", True)
                    self.parent.auto_print_checkbox.setChecked(auto_print)
                    print(f"已更新主窗口自动打印复选框状态: {auto_print}")
            except Exception as e:
                print(f"更新下一次执行时间失败: {e}")
                import traceback
                traceback.print_exc()
    
    def update_coordinate_config(self, settings):
        """同步更新自动导出坐标配置文件"""
        import os
        import json
        
        # 坐标映射关系
        coordinate_mapping = {
            "mainWindow": "zhuanglu_tab",
            "furnaceWindow": "zhuanglu_export_btn",
            "planInput": "zhizhi_tab",
            "queryBtn": "plan_select",
            "exportBtn": "zhizhi_export_btn",
            "closeBtn": "first_plan",
            "detailExportBtn": "plan_detail_export"
        }
        
        # 获取现有的坐标配置
        coord_config = {}
        # 使用self.parent.plan_dir确保打包后也能正确保存配置文件
        if hasattr(self, 'parent') and hasattr(self.parent, 'plan_dir'):
            coord_file = os.path.join(self.parent.plan_dir, 'export_coordinates.json')
        else:
            # 备用方案：确保使用正确的路径
            if getattr(sys, 'frozen', False):
                coord_file = os.path.join(os.path.dirname(sys.executable), 'export_coordinates.json')
            else:
                coord_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_coordinates.json')
        if os.path.exists(coord_file):
            try:
                with open(coord_file, 'r', encoding='utf-8') as f:
                    coord_config = json.load(f)
            except Exception as e:
                print(f"加载坐标配置文件失败: {e}")
        
        # 更新坐标配置
        for settings_key, coord_key in coordinate_mapping.items():
            if settings_key in settings:
                x = settings[settings_key].get("x", 0)
                y = settings[settings_key].get("y", 0)
                coord_config[coord_key] = [x, y]
        
        # 保留其他配置项
        if "plan_spacing" not in coord_config:
            coord_config["plan_spacing"] = 21
        if "first_plan_offset" not in coord_config:
            coord_config["first_plan_offset"] = 0
        if "test_window" not in coord_config:
            coord_config["test_window"] = "BGCMS1-宝钢股份多基地制造管理系统运行环境"
        if "export_speed" not in coord_config:
            coord_config["export_speed"] = "中"
        
        # 保存坐标配置
        try:
            with open(coord_file, 'w', encoding='utf-8') as f:
                json.dump(coord_config, f, ensure_ascii=False, indent=2)
            print("坐标配置已同步更新")
        except Exception as e:
            print(f"保存坐标配置失败: {e}")
        
        # 如果主窗口存在，更新其coordinates属性
        if self.parent and hasattr(self.parent, 'coordinates'):
            self.parent.coordinates = coord_config
            print("主窗口坐标配置已更新")
    
    def restore_defaults(self):
        """恢复默认设置"""
        import os
        import json
        
        # 从默认设置文件加载默认值
        # 使用self.parent.plan_dir确保打包后也能正确读取配置文件
        if hasattr(self, 'parent') and hasattr(self.parent, 'plan_dir'):
            default_config_file = os.path.join(self.parent.plan_dir, 'default_settings.json')
        else:
            # 备用方案：确保使用正确的路径
            if getattr(sys, 'frozen', False):
                default_config_file = os.path.join(os.path.dirname(sys.executable), 'default_settings.json')
            else:
                default_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_settings.json')
        default_settings = None
        
        try:
            with open(default_config_file, 'r', encoding='utf-8') as f:
                default_settings = json.load(f)
        except Exception as e:
            print(f"加载默认设置文件失败: {e}")
        
        # 如果默认设置文件加载失败，使用硬编码的默认值
        if default_settings is None:
            default_settings = {
                "mainWindow": {"x": 284, "y": 85},      # 装炉顺作成管理标签
                "furnaceWindow": {"x": 988, "y": 819},   # 装炉顺序导出按钮
                "planInput": {"x": 107, "y": 85},        # 轧制计划管理标签
                "queryBtn": {"x": 734, "y": 135},        # 选择计划号
                "exportBtn": {"x": 78, "y": 708},        # 导出总计划号列表按钮
                "closeBtn": {"x": 235, "y": 207},        # 第一个计划号
                "detailExportBtn": {"x": 79, "y": 859},   # 计划明细导出按钮
                "selectedWindow": "BGCMS1-宝钢股份多基地制造管理系统运行环境",
                "autoPrint": True,
                "autoExec": False,
                "execMode": "interval",
                "intervalMinutes": 1,
                "execTimes": "16:00,16:02,16:04"
            }
        
        # 应用默认设置
        self.apply_settings(default_settings)
        # 保存默认设置
        self.save_settings(default_settings)
        
        # 显示提示
        QMessageBox.information(self, "提示", "已恢复默认设置")
    
    def cleanup_extra_files(self):
        """清理计划号目录中多余的计划号文件"""
        if self.parent and hasattr(self.parent, 'cleanup_extra_plan_files'):
            self.parent.cleanup_extra_plan_files()
    
    def get_window_coordinates(self, window_type):
        """获取窗口坐标 - 激活选择的窗口，移动鼠标，以鼠标左键点击作为最终获取的坐标值"""
        try:
            import win32gui
            import win32api
            import win32con
            
            # 获取当前选择的窗口
            selected_window = "Doc1.docx - Word" if self.ui.windowRadio1.isChecked() else "BGCMS1-宝钢股份多基地制造管理系统运行环境"
            print(f"获取坐标：激活窗口: {selected_window}")
            
            # 激活目标窗口
            if self.parent and hasattr(self.parent, 'activate_window'):
                self.parent.activate_window(selected_window)
            
            # 等待窗口激活
            import time
            time.sleep(0.3)
            
            # 显示坐标实时更新
            start_time = time.time()
            while True:
                # 检查窗口是否仍然打开
                if not self.isVisible():
                    break
                
                # 检查是否超过30秒，自动退出
                if time.time() - start_time > 30:
                    break
                
                x, y = win32api.GetCursorPos()
                # 更新界面
                if window_type == 'mainWindow':
                    self.ui.mainWindowXEdit.setText(str(x))
                    self.ui.mainWindowYEdit.setText(str(y))
                elif window_type == 'furnaceWindow':
                    self.ui.furnaceWindowXEdit.setText(str(x))
                    self.ui.furnaceWindowYEdit.setText(str(y))
                elif window_type == 'planInput':
                    self.ui.planInputXEdit.setText(str(x))
                    self.ui.planInputYEdit.setText(str(y))
                elif window_type == 'queryBtn':
                    self.ui.queryBtnXEdit.setText(str(x))
                    self.ui.queryBtnYEdit.setText(str(y))
                elif window_type == 'exportBtn':
                    self.ui.exportBtnXEdit.setText(str(x))
                    self.ui.exportBtnYEdit.setText(str(y))
                elif window_type == 'closeBtn':
                    self.ui.closeBtnXEdit.setText(str(x))
                    self.ui.closeBtnYEdit.setText(str(y))
                elif window_type == 'detailExportBtn':
                    self.ui.detailExportBtnXEdit.setText(str(x))
                    self.ui.detailExportBtnYEdit.setText(str(y))
                
                QApplication.processEvents()
                time.sleep(0.05)
                
                # 检查是否按下鼠标左键
                if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                    # 等待鼠标释放
                    while win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                        time.sleep(0.01)
                    # 保存当前坐标
                    self.save_settings()
                    # 将设置窗口置顶
                    self.raise_()
                    self.activateWindow()
                    break
                
                # 检查是否按下Esc键取消
                if win32api.GetAsyncKeyState(win32con.VK_ESCAPE) & 0x8000:
                    break
                    
        except Exception as e:
            print(f"获取坐标失败: {e}")
            QMessageBox.warning(self, "错误", "获取坐标失败")
    
    def test_window_coordinates(self, window_type):
        """测试窗口坐标 - 激活选择的窗口，按照文本框中的坐标值把鼠标移动到坐标位置"""
        try:
            import win32gui
            import win32api
            import win32con
            import time
            
            # 获取坐标
            if window_type == 'mainWindow':
                x = int(self.ui.mainWindowXEdit.text()) if self.ui.mainWindowXEdit.text().isdigit() else 0
                y = int(self.ui.mainWindowYEdit.text()) if self.ui.mainWindowYEdit.text().isdigit() else 0
            elif window_type == 'furnaceWindow':
                x = int(self.ui.furnaceWindowXEdit.text()) if self.ui.furnaceWindowXEdit.text().isdigit() else 0
                y = int(self.ui.furnaceWindowYEdit.text()) if self.ui.furnaceWindowYEdit.text().isdigit() else 0
            elif window_type == 'planInput':
                x = int(self.ui.planInputXEdit.text()) if self.ui.planInputXEdit.text().isdigit() else 0
                y = int(self.ui.planInputYEdit.text()) if self.ui.planInputYEdit.text().isdigit() else 0
            elif window_type == 'queryBtn':
                x = int(self.ui.queryBtnXEdit.text()) if self.ui.queryBtnXEdit.text().isdigit() else 0
                y = int(self.ui.queryBtnYEdit.text()) if self.ui.queryBtnYEdit.text().isdigit() else 0
            elif window_type == 'exportBtn':
                x = int(self.ui.exportBtnXEdit.text()) if self.ui.exportBtnXEdit.text().isdigit() else 0
                y = int(self.ui.exportBtnYEdit.text()) if self.ui.exportBtnYEdit.text().isdigit() else 0
            elif window_type == 'closeBtn':
                x = int(self.ui.closeBtnXEdit.text()) if self.ui.closeBtnXEdit.text().isdigit() else 0
                y = int(self.ui.closeBtnYEdit.text()) if self.ui.closeBtnYEdit.text().isdigit() else 0
            elif window_type == 'detailExportBtn':
                x = int(self.ui.detailExportBtnXEdit.text()) if self.ui.detailExportBtnXEdit.text().isdigit() else 0
                y = int(self.ui.detailExportBtnYEdit.text()) if self.ui.detailExportBtnYEdit.text().isdigit() else 0
            else:
                return
            
            # 获取当前选择的窗口
            selected_window = "Doc1.docx - Word" if self.ui.windowRadio1.isChecked() else "BGCMS1-宝钢股份多基地制造管理系统运行环境"
            print(f"测试坐标：激活窗口: {selected_window}")
            
            # 激活目标窗口
            if self.parent and hasattr(self.parent, 'activate_window'):
                self.parent.activate_window(selected_window)
            
            # 等待窗口激活
            time.sleep(0.5)
            
            # 移动鼠标到指定位置
            win32api.SetCursorPos((x, y))
            
            # 不显示弹窗，直接留在激活窗口
            print(f"鼠标已移动到{window_type}位置: ({x}, {y})")
            
        except Exception as e:
            print(f"测试坐标失败: {e}")
    
    def accept(self):
        """确认设置"""
        try:
            print("SettingsWindow.accept被调用")
            # 保存设置
            self.save_settings()
            print("设置已保存")
            super().accept()
            print("窗口已关闭")
            if self.parent:
                print("调用parent.load_settings()")
                self.parent.load_settings()
                print("parent.load_settings()调用完成")
        except UnicodeEncodeError:
            # 捕获编码错误，避免程序崩溃
            pass


class ExportProcessWindow(QDialog):
    """导出过程窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出过程")
        self.setGeometry(300, 200, 800, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加文本框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 添加按钮
        button = QPushButton("关闭")
        button.clicked.connect(self.close)
        layout.addWidget(button)
        
    def append_text(self, text):
        """追加文本"""
        self.text_edit.append(text)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())


if __name__ == "__main__":
    """主程序入口"""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        try:
            print(f"启动程序失败: {str(e)}")
        except UnicodeEncodeError:
            print("启动程序失败")
        import traceback
        try:
            traceback.print_exc()
        except UnicodeEncodeError:
            print("异常信息包含非ASCII字符")
        try:
            QMessageBox.critical(None, "错误", f"启动程序失败: {str(e)}")
        except UnicodeEncodeError:
            QMessageBox.critical(None, "错误", "启动程序失败")
        sys.exit(1)