#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第5633-5663行的问题：在有导出计划号的情况下也需要设置定时器
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
                            
                            # 无论是否有导出计划号，都在10秒后进入装炉明细画面
                            # 使用QTimer确保在主线程中执行
                            from PyQt5.QtWidgets import QApplication
                            from PyQt5.QtCore import QTimer
                            
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
                            QTimer.singleShot(10000, self.go_to_furnace_details)"""

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
                            QTimer.singleShot(10000, self.go_to_furnace_details)"""

content = content.replace(old_code, new_code)

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
