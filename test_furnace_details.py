#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试完整的标注检测流程
"""

import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt

class TestFurnaceDetails(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('测试标注检测')
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['钢卷号', '除鳞', '测试'])
        
        # 设置表格样式
        table_style = """
            QTableWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                gridline-color: #CCCCCC;
                outline: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FD;
            }
        """
        self.table_widget.setStyleSheet(table_style)
        
        # 测试数据 - 模拟实际的计划数据
        test_data = [
            # 带标注的钢卷号
            ['1234Δ', '回', '正常'],
            ['5678*', '无APS', '正常'],
            # 正常钢卷号
            ['9012', '正常', '正常'],
            # 除鳞字段带标注
            ['3456', '回', '正常'],
            ['7890', '无APS', '正常']
        ]
        
        # 添加数据到表格
        self.table_widget.setRowCount(len(test_data))
        for row_idx, row_data in enumerate(test_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                
                # 设置字体
                font = item.font()
                font.setFamily("微软雅黑")
                font.setPointSize(20)
                font.setBold(True)
                item.setFont(font)
                
                # 获取列名
                col_name = self.table_widget.horizontalHeaderItem(col_idx).text()
                
                # 检查是否有标识（三角符号Δ或星号*）
                value_str = str(value)
                if 'Δ' in value_str or '*' in value_str:
                    # 设置红色背景
                    item.setBackground(QBrush(QColor('#FF0000')))
                    # 添加annotation属性，用于样式表识别
                    item.setData(Qt.UserRole, True)
                    print(f"标注检测: {value} -> 红色背景")
                # 除鳞字段中包含"回"和"无APS"的单元格也改背景色为红色
                elif col_name == "除鳞" and ('回' in value_str or '无APS' in value_str):
                    # 设置红色背景
                    item.setBackground(QBrush(QColor('#FF0000')))
                    # 添加annotation属性，用于样式表识别
                    item.setData(Qt.UserRole, True)
                    print(f"除鳞标注: {value} -> 红色背景")
                else:
                    print(f"正常: {value} -> 无背景")
                
                # 设置对齐方式
                if col_idx == 8:  # 粗轧报信在第9列（索引8）
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                else:
                    item.setTextAlignment(Qt.AlignCenter)  # 水平和垂直居中
                
                self.table_widget.setItem(row_idx, col_idx, item)
                
                # 自动调整行高
                self.table_widget.resizeRowToContents(row_idx)
                # 增加行高10
                current_height = self.table_widget.rowHeight(row_idx)
                self.table_widget.setRowHeight(row_idx, current_height + 10)
        
        layout.addWidget(self.table_widget)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestFurnaceDetails()
    sys.exit(app.exec_())