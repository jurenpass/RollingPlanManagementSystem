#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试背景色设置
"""

import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor, QBrush, QPainter
from PyQt5.QtCore import Qt

class CustomTableWidget(QTableWidget):
            def __init__(self, parent=None):
                super().__init__(parent)

            def paintEvent(self, event):
                # 先绘制背景色
                painter = QPainter(self.viewport())
                painter.translate(self.viewport().rect().topLeft())
                for row in range(self.rowCount()):
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item:
                            bg_color = item.background().color()
                            color_name = bg_color.name()
                            if color_name == '#ff0000':
                                rect = self.visualRect(self.model().index(row, col))
                                painter.fillRect(rect, QBrush(QColor('#FF0000')))
                            elif color_name == '#ffff00':
                                rect = self.visualRect(self.model().index(row, col))
                                painter.fillRect(rect, QBrush(QColor('#FFFF00')))
                # 再调用父类的paintEvent
                super().paintEvent(event)


class DebugTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('调试背景色')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.table = CustomTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['钢卷号', '除鳞', '测试'])

        # 测试数据
        test_data = [
            ['1234Δ', '回', '正常'],
            ['5678*', '无APS', '正常'],
            ['9012', '正常', '正常'],
        ]

        self.table.setRowCount(len(test_data))
        for row_idx, row_data in enumerate(test_data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))

                value_str = str(value)
                col_name = self.table.horizontalHeaderItem(col_idx).text()

                print(f"Setting item ({row_idx}, {col_idx}): {value_str}")

                if 'Δ' in value_str or '*' in value_str:
                    item.setBackground(QBrush(QColor('#FF0000')))
                    print(f"  -> Set RED background")
                elif col_name == "除鳞" and ('回' in value_str or '无APS' in value_str):
                    item.setBackground(QBrush(QColor('#FF0000')))
                    print(f"  -> Set RED background (除鳞)")
                else:
                    print(f"  -> No background")

                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        layout.addWidget(self.table)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebugTest()
    sys.exit(app.exec_())