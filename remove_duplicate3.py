#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 删除第一处 go_to_furnace_details (第1109-1131行) - 这是较旧的版本
# 使用正则表达式匹配并删除

# 匹配第一个 go_to_furnace_details 函数定义（较旧的版本）
pattern1 = r'\n\s*# 定义10秒后进入装炉明细画面的函数\n\s*def go_to_furnace_details\(\):.*?QTimer\.singleShot\(10000, go_to_furnace_details\)'
content = re.sub(pattern1, '\n                        # 10秒后进入装炉明细画面（使用类方法）\n                        QTimer.singleShot(10000, self.go_to_furnace_details)', content, flags=re.DOTALL)

# 2. 保留第5641行的完整版本（带有刷新功能），删除第5687行的重复版本
# 匹配第二处 go_to_furnace_details 函数定义（重复的版本）
pattern2 = r'\n\s*# 定义进入装炉明细画面的函数\n\s*def go_to_furnace_details\(\):.*?QTimer\.singleShot\(10000, go_to_furnace_details\)'
content = re.sub(pattern2, '\n                            # 10秒后进入装炉明细画面（使用类方法）\n                            QTimer.singleShot(10000, self.go_to_furnace_details)', content, flags=re.DOTALL)

# 3. 在 MainWindow 类中添加 go_to_furnace_details 方法（在 open_furnace_details 方法之后）

# 找到 open_furnace_details 方法的结束位置
open_furnace_pattern = r'(def open_furnace_details\(self\):.*?print\("创建新的装炉明细窗口"\))'
match = re.search(open_furnace_pattern, content, re.DOTALL)

if match:
    # 在这个方法之后添加新的 go_to_furnace_details 方法
    new_method = '''

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
            print(f"进入装炉明细画面失败: {e}")'''

    # 在 open_furnace_details 方法结束后插入新方法
    content = content[:match.end()] + new_method + content[match.end():]

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
