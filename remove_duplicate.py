#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到重复的 go_to_furnace_details 代码块
# 第一处：第5650-5671行（在 if event.exported_plans: 分支中）
# 第二处：第5687-5717行（在 else: 分支中）

# 替换第一处重复代码为方法调用
old_code1 = """                            def go_to_furnace_details():
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
                                                # 刷新后恢复上次选中的钢卷号位置
                                                if hasattr(widget, 'restore_selected_coil'):
                                                    widget.restore_selected_coil()
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

new_code1 = """                            # 设置10秒后进入装炉明细画面
                            QTimer.singleShot(10000, self.go_to_furnace_details)
                        else:"""

content = content.replace(old_code1, new_code1)

# 替换第二处重复代码（已缩进在 else 分支中）
old_code2 = """                            # 定义进入装炉明细画面的函数
                            def go_to_furnace_details():
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
                                                # 刷新后恢复上次选中的钢卷号位置
                                                if hasattr(widget, 'restore_selected_coil'):
                                                    widget.restore_selected_coil()
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
                            QTimer.singleShot(10000, go_to_furnace_details)"""

new_code2 = """                            # 设置10秒后进入装炉明细画面
                            QTimer.singleShot(10000, self.go_to_furnace_details)"""

content = content.replace(old_code2, new_code2)

# 在 MainWindow 类中添加 go_to_furnace_details 方法
# 在 open_furnace_details 方法之后添加
old_open_furnace = """    def open_furnace_details(self):
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

new_open_furnace = """    def open_furnace_details(self):
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
            print("创建新的装炉明细窗口")

    def go_to_furnace_details(self):
        \"\"\"进入装炉明细画面 - 被定时器调用\"\"\"
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
            print(f"进入装炉明细画面失败: {e}")"""

content = content.replace(old_open_furnace, new_open_furnace)

with open('g:/newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
