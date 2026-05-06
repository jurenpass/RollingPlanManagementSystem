#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试标注检测逻辑
"""

import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QColor, QBrush

class TestAnnotationDetection:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.table = QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(['钢卷号', '除鳞', '测试'])
        
        # 测试数据
        test_data = [
            ['1234Δ', '回', '正常'],
            ['5678*', '无APS', '正常'],
            ['9012', '正常', '正常']
        ]
        
        for row in range(3):
            for col in range(3):
                value = test_data[row][col]
                item = QTableWidgetItem(value)
                
                # 模拟标注检测逻辑
                value_str = str(value)
                col_name = self.table.horizontalHeaderItem(col).text()
                
                if 'Δ' in value_str or '*' in value_str:
                    item.setBackground(QBrush(QColor('#FF0000')))
                    print(f"标注检测: {value} -> 红色背景")
                elif col_name == "除鳞" and ('回' in value_str or '无APS' in value_str):
                    item.setBackground(QBrush(QColor('#FF0000')))
                    print(f"除鳞标注: {value} -> 红色背景")
                else:
                    print(f"正常: {value} -> 无背景")
                
                self.table.setItem(row, col, item)
        
        self.table.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    test = TestAnnotationDetection()