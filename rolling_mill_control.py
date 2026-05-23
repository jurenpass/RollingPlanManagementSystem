#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QFrame, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QScrollArea, QGridLayout, QHBoxLayout, QVBoxLayout,
                             QSplitter)
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtCore import Qt

class RollingMillControl(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("轧机控制系统")
        self.setGeometry(100, 100, 1600, 900)
        
        # 主背景色
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(180, 180, 180))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 1. 顶部状态栏区域
        self.add_top_status_bar(main_layout)
        
        # 2. 中间主显示区域
        self.add_main_display_area(main_layout)
        
        # 3. 底部数据表格区域
        self.add_bottom_data_area(main_layout)
        
        # 4. 最底部功能按钮区域
        self.add_function_buttons(main_layout)
    
    def add_top_status_bar(self, parent_layout):
        top_frame = QFrame()
        top_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        top_frame.setStyleSheet("background-color: #D0D0D0;")
        
        # 黄色标题栏
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #FFFF00;")
        header_layout = QHBoxLayout(header_frame)
        
        # 左侧区域
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.create_status_label("Plant Status RM"))
        left_layout.addWidget(self.create_status_label("Diagnostic RM"))
        left_layout.addWidget(self.create_status_label("CSM/DMSM RM"))
        left_layout.addWidget(self.create_status_label("CSM/DMSM RM"))
        
        # 右侧区域
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.create_status_label("Setpoints RM"))
        right_layout.addWidget(self.create_status_label("Diagnostic Level2"))
        
        header_layout.addLayout(left_layout)
        header_layout.addStretch()
        header_layout.addLayout(right_layout)
        
        top_layout = QVBoxLayout(top_frame)
        top_layout.addWidget(header_frame)
        
        parent_layout.addWidget(top_frame)
    
    def create_status_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("background-color: #E0E0E0; padding: 5px 10px; border: 1px solid #A0A0A0;")
        label.setFixedHeight(25)
        return label
    
    def add_main_display_area(self, parent_layout):
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        main_frame.setStyleSheet("background-color: #C8C8C8;")
        parent_layout.addWidget(main_frame)
        
        layout = QVBoxLayout(main_frame)
        
        # 标题栏
        title_label = QLabel("Plant Status RM")
        title_label.setStyleSheet("background-color: #808080; color: white; padding: 5px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 设备ID行
        id_row = QWidget()
        id_layout = QHBoxLayout(id_row)
        ids = ["5200", "5203", "", "", ""]
        for i, id_text in enumerate(ids):
            if id_text:
                id_label = QLabel(f"ID {id_text}")
                id_label.setStyleSheet("background-color: #00CED1; color: blue; padding: 3px 20px; font-weight: bold;")
            else:
                id_label = QLabel()
                id_label.setStyleSheet("background-color: #C0C0C0;")
            id_label.setFixedHeight(20)
            id_layout.addWidget(id_label)
            if i < 4:
                id_layout.addStretch(1)
        layout.addWidget(id_row)
        
        # 轧机示意图区域
        mill_frame = QFrame()
        mill_frame.setStyleSheet("background-color: #D8D8D8;")
        mill_layout = QHBoxLayout(mill_frame)
        
        # 左侧状态区
        left_status = QWidget()
        left_layout = QVBoxLayout(left_status)
        left_layout.addWidget(self.create_status_box("C-Mode", "#00CED1"))
        left_layout.addWidget(self.create_status_box("Disc.Auto", "#00CED1"))
        left_layout.addWidget(self.create_status_box("No Slab Appr.", "#FFD700"))
        mill_layout.addWidget(left_status)
        
        # 轧机图形区
        mill_graph = QFrame()
        mill_graph.setStyleSheet("background-color: #D0D0D0;")
        mill_graph.setFixedHeight(120)
        mill_graph_layout = QHBoxLayout(mill_graph)
        
        # 机架图形
        for i in range(17):
            stand = QFrame()
            stand.setStyleSheet("background-color: #228B22;")
            stand.setFixedSize(40, 30)
            mill_graph_layout.addWidget(stand)
            if i < 16:
                mill_graph_layout.addStretch(1)
        
        mill_layout.addWidget(mill_graph)
        mill_layout.addStretch()
        
        # 右侧状态区
        right_status = QWidget()
        right_layout = QVBoxLayout(right_status)
        right_layout.addWidget(self.create_status_box("Cobble P.Back", "#00CED1"))
        right_layout.addWidget(self.create_status_box("RM Trans", "#228B22"))
        right_layout.addWidget(self.create_status_box("Line", "#4169E1"))
        mill_layout.addWidget(right_status)
        
        layout.addWidget(mill_frame)
        
        # 数据显示区
        data_frame = QFrame()
        data_frame.setStyleSheet("background-color: #B8B8B8;")
        data_layout = QHBoxLayout(data_frame)
        
        # 入口数据
        entry_group = self.create_data_group("Entry", [
            ("1110", "°C"), ("600", "°C"),
            ("1361", "mm"), ("1361", "mm"),
            ("1.00", "m/s"), ("1.00", "m/s")
        ])
        data_layout.addWidget(entry_group)
        
        # SG数据
        sg_group = self.create_data_group("SG", [
            ("2250", "mm"), ("2250", "mm"),
            ("2260.0", "mm"), ("2260.0", "mm")
        ])
        data_layout.addWidget(sg_group)
        
        # R1数据
        r1_group = self.create_data_group("R1", [
            ("203.48", "mm"), ("1.43", "m/s"),
            ("0.01", "MN"), ("7.3", "s")
        ])
        data_layout.addWidget(r1_group)
        
        # Swivel数据
        swivel_group = self.create_data_group("Swivel", [
            ("-0.51", "mm"), ("-0.51", "mm")
        ])
        data_layout.addWidget(swivel_group)
        
        # SG数据
        sg2_group = self.create_data_group("SG", [
            ("2157", "mm"), ("2171", "mm"),
            ("31.03", "mm"), ("31.10", "mm")
        ])
        data_layout.addWidget(sg2_group)
        
        # E2数据
        e2_group = self.create_data_group("E2", [
            ("1030", "mm"), ("1030", "mm"),
            ("1.00", "m/s"), ("-0.05", "MN")
        ])
        data_layout.addWidget(e2_group)
        
        # R2数据
        r2_group = self.create_data_group("R2", [
            ("155.2", "mm"), ("155.26", "mm"),
            ("1.00", "m/s"), ("0.20", "MN")
        ])
        data_layout.addWidget(r2_group)
        
        # Swivel数据
        swivel2_group = self.create_data_group("Swivel", [
            ("+0.45", "mm"), ("+0.45", "mm"),
            ("7", "%")
        ])
        data_layout.addWidget(swivel2_group)
        
        # SG数据
        sg3_group = self.create_data_group("SG", [
            ("2157", "mm"), ("2171", "mm"),
            ("25.12", "mm"), ("25.12", "mm")
        ])
        data_layout.addWidget(sg3_group)
        
        # Exit数据
        exit_group = self.create_data_group("Exit", [
            ("1110", "Wmm"), ("600", "°C"),
            ("3.00", "m/s"), ("0.00", "")
        ])
        data_layout.addWidget(exit_group)
        
        # R2 Fan
        fan_group = QFrame()
        fan_group.setStyleSheet("background-color: #228B22;")
        fan_label = QLabel("R2 Fan")
        fan_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        fan_layout = QVBoxLayout(fan_group)
        fan_layout.addWidget(fan_label)
        data_layout.addWidget(fan_group)
        
        layout.addWidget(data_frame)
    
    def create_status_box(self, text, color):
        box = QFrame()
        box.setStyleSheet(f"background-color: {color};")
        label = QLabel(text)
        label.setStyleSheet("color: white; font-weight: bold; padding: 3px 10px;")
        layout = QVBoxLayout(box)
        layout.addWidget(label)
        return box
    
    def create_data_group(self, title, data):
        group = QFrame()
        group.setStyleSheet("background-color: #A8A8A8;")
        layout = QVBoxLayout(group)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("background-color: #606060; color: white; padding: 2px 5px; font-size: 10px;")
        layout.addWidget(title_label)
        
        grid = QGridLayout()
        for i, (value, unit) in enumerate(data):
            value_label = QLabel(value)
            value_label.setStyleSheet("background-color: #00CED1; color: #00008B; font-weight: bold; padding: 2px 5px;")
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("background-color: #87CEEB; padding: 2px 3px; font-size: 10px;")
            grid.addWidget(value_label, i // 2, (i % 2) * 2)
            grid.addWidget(unit_label, i // 2, (i % 2) * 2 + 1)
        
        layout.addLayout(grid)
        return group
    
    def add_bottom_data_area(self, parent_layout):
        bottom_frame = QFrame()
        bottom_frame.setFrameStyle(QFrame.Box | QFrame.Sunken)
        bottom_frame.setStyleSheet("background-color: #D0D0D0;")
        
        layout = QHBoxLayout(bottom_frame)
        
        # 左侧表格区域
        left_table = QFrame()
        left_layout = QVBoxLayout(left_table)
        
        # SP, R1, R2 行
        for name in ["SP", "R1", "R2", "R2"]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            
            name_label = QLabel(name)
            name_label.setStyleSheet("background-color: #4169E1; color: white; padding: 3px 10px; font-weight: bold;")
            row_layout.addWidget(name_label)
            
            id_label = QLabel("Slab ID")
            id_label.setStyleSheet("background-color: #6495ED; color: white; padding: 3px 10px;")
            row_layout.addWidget(id_label)
            
            for _ in range(4):
                data_label = QLabel("1650")
                data_label.setStyleSheet("background-color: #4169E1; color: white; padding: 3px 15px;")
                row_layout.addWidget(data_label)
            
            row_layout.addStretch()
            
            wcl_label = QLabel("WCL")
            wcl_label.setStyleSheet("background-color: #6495ED; color: white; padding: 3px 5px;")
            row_layout.addWidget(wcl_label)
            
            val_label = QLabel("90 %")
            val_label.setStyleSheet("background-color: #4169E1; color: white; padding: 3px 10px;")
            row_layout.addWidget(val_label)
            
            left_layout.addWidget(row)
        
        # 数据表
        table_container = QScrollArea()
        table_container.setWidgetResizable(True)
        
        table_widget = QTableWidget(8, 4)
        table_widget.setHorizontalHeaderLabels(["E2[mm]", "R2[mm]", "V [m/s]", "Desc"])
        
        for i in range(8):
            for j in range(4):
                if j == 3:
                    item = QTableWidgetItem("1")
                else:
                    item = QTableWidgetItem("1650" if j < 2 else "3.5")
                item.setBackground(QColor("#4169E1"))
                item.setForeground(QColor(Qt.white))
                table_widget.setItem(i, j, item)
        
        table_container.setWidget(table_widget)
        left_layout.addWidget(table_container)
        
        layout.addWidget(left_table)
        
        # 右侧表格区域
        right_table = QFrame()
        right_layout = QVBoxLayout(right_table)
        
        # Actual Slab 行
        for _ in range(3):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            
            slab_label = QLabel("Slab")
            slab_label.setStyleSheet("background-color: #2E8B57; color: white; padding: 3px 15px;")
            row_layout.addWidget(slab_label)
            
            for _ in range(6):
                data_label = QLabel("1650")
                data_label.setStyleSheet("background-color: #3CB371; color: white; padding: 3px 15px;")
                row_layout.addWidget(data_label)
            
            row_layout.addStretch()
            right_layout.addWidget(row)
        
        # R2 Max speed 和 SP Level
        speed_row = QWidget()
        speed_layout = QHBoxLayout(speed_row)
        speed_layout.addStretch()
        
        speed_label = QLabel("R2 Max speed")
        speed_label.setStyleSheet("background-color: #2E8B57; color: white; padding: 3px 10px;")
        speed_layout.addWidget(speed_label)
        
        speed_val = QLabel("5.8 m/s")
        speed_val.setStyleSheet("background-color: #00CED1; color: #00008B; padding: 3px 10px; font-weight: bold;")
        speed_layout.addWidget(speed_val)
        
        level_label = QLabel("SP Level")
        level_label.setStyleSheet("background-color: #2E8B57; color: white; padding: 3px 10px;")
        speed_layout.addWidget(level_label)
        
        level_val = QLabel("35.6 %")
        level_val.setStyleSheet("background-color: #00CED1; color: #00008B; padding: 3px 10px; font-weight: bold;")
        speed_layout.addWidget(level_val)
        
        right_layout.addWidget(speed_row)
        
        # 状态按钮行
        status_row = QWidget()
        status_layout = QHBoxLayout(status_row)
        status_layout.addStretch()
        
        rt_stop = QLabel("RT STOP")
        rt_stop.setStyleSheet("background-color: #4169E1; color: white; padding: 3px 15px; font-weight: bold;")
        status_layout.addWidget(rt_stop)
        
        r1_spd = QLabel("R1 SPD UP")
        r1_spd.setStyleSheet("background-color: #228B22; color: white; padding: 3px 15px;")
        status_layout.addWidget(r1_spd)
        
        exit_spd = QLabel("EXIT SPD UP")
        exit_spd.setStyleSheet("background-color: #228B22; color: white; padding: 3px 15px;")
        status_layout.addWidget(exit_spd)
        
        right_layout.addWidget(status_row)
        
        # 右侧数据表
        table_container2 = QScrollArea()
        table_container2.setWidgetResizable(True)
        
        table_widget2 = QTableWidget(8, 7)
        table_widget2.setHorizontalHeaderLabels(["E2[mm]", "R2[mm]", "V [m/s]", "Desc", "Ski[%]", "Ski[m]", ""])
        
        for i in range(8):
            for j in range(7):
                if j == 2:
                    item = QTableWidgetItem("1650")
                elif j == 3:
                    item = QTableWidgetItem("1")
                elif j == 4:
                    item = QTableWidgetItem("1")
                elif j == 5:
                    item = QTableWidgetItem("1")
                else:
                    item = QTableWidgetItem("1650")
                item.setBackground(QColor("#2E8B57"))
                item.setForeground(QColor(Qt.white))
                table_widget2.setItem(i, j, item)
        
        table_container2.setWidget(table_widget2)
        right_layout.addWidget(table_container2)
        
        layout.addWidget(right_table)
        
        parent_layout.addWidget(bottom_frame)
    
    def add_function_buttons(self, parent_layout):
        button_frame = QFrame()
        button_frame.setStyleSheet("background-color: #C0C0C0;")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)
        
        buttons = [
            "Mill Mode", "Stand Mode", "Sizing Press Mode", "Simulation",
            "Roll Data", "Jogging Selection", "Set Run Counter",
            "Release Drives", "Change Ski", "Cooling", "Confirm", "Fault acknowle"
        ]
        
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #A0A0A0;
                    border: 1px solid #808080;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #B0B0B0;
                }
            """)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        parent_layout.addWidget(button_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RollingMillControl()
    window.showMaximized()
    sys.exit(app.exec_())