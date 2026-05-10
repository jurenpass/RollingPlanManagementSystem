#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 open_furnace_details 方法，确保始终只有一个装炉明细窗口
old_code = """    def open_furnace_details(self):
        \"\"\"打开装炉明细窗口\"\"\"
        self.furnace_details_window = FurnaceDetailsWindow(self)
        self.furnace_details_window.show()"""

new_code = """    def open_furnace_details(self):
        \"\"\"打开装炉明细窗口 - 确保始终只有一个窗口打开\"\"\"
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
            print("已激活现有的装炉明细窗口")
        else:
            # 如果没有装炉明细窗口，创建新窗口
            self.furnace_details_window = FurnaceDetailsWindow(self)
            self.furnace_details_window.show()
            print("创建新的装炉明细窗口")"""

content = content.replace(old_code, new_code)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
