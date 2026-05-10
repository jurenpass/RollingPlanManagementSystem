#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 go_to_furnace_details() 函数，在激活窗口时同时刷新数据
old_go_to_furnace = """                            def go_to_furnace_details():
                                try:
                                    # 10秒后进入装炉明细画面
                                    has_furnace_details_window = False
                                    for widget in QApplication.topLevelWidgets():
                                        if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                                            has_furnace_details_window = True
                                            # 激活装炉明细窗口
                                            widget.activateWindow()
                                            widget.raise_()
                                            widget.show()
                                            print("10秒延时后进入装炉明细画面")
                                            break
                                    
                                    if not has_furnace_details_window:
                                        # 如果没有装炉明细窗口，打开新的装炉明细窗口
                                        print("未找到装炉明细窗口，打开新的装炉明细画面")
                                        self.open_furnace_details()
                                        print("成功打开装炉明细窗口")
                                except Exception as e:
                                    print(f"进入装炉明细画面失败: {e}")"""

new_go_to_furnace = """                            def go_to_furnace_details():
                                try:
                                    # 10秒后进入装炉明细画面
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
                                            print("10秒延时后进入装炉明细画面")
                                            break
                                    
                                    if not has_furnace_details_window:
                                        # 如果没有装炉明细窗口，打开新的装炉明细窗口
                                        print("未找到装炉明细窗口，打开新的装炉明细画面")
                                        self.open_furnace_details()
                                        print("成功打开装炉明细窗口")
                                except Exception as e:
                                    print(f"进入装炉明细画面失败: {e}")"""

content = content.replace(old_go_to_furnace, new_go_to_furnace)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
