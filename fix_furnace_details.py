#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改：在有导出计划号的情况下也打开装炉明细画面
old_code = """                            # 回到主程序画面（轧制计划管理系统）
                            print("返回主程序画面（轧制计划管理系统）")
                            try:
                                # 激活本程序的主窗口
                                self.activateWindow()
                                self.raise_()
                                self.show()
                                print("成功返回主程序画面")
                            except Exception as e:
                                print(f"返回主程序画面失败: {e}")
                        else:"""

new_code = """                            # 回到主程序画面（轧制计划管理系统）
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
                            
                            def go_to_furnace_details():
                                try:
                                    # 检查是否已有装炉明细窗口
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
                                    print(f"进入装炉明细画面失败: {e}")
                            
                            # 设置10秒后进入装炉明细画面
                            QTimer.singleShot(10000, go_to_furnace_details)
                        else:"""

content = content.replace(old_code, new_code)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
