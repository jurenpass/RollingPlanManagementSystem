#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除第5649-5679行的重复嵌套函数定义
# 使用更精确的匹配
target = """                            def go_to_furnace_details():
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

replacement = """                            # 10秒后进入装炉明细画面（使用类方法）
                            QTimer.singleShot(10000, self.go_to_furnace_details)"""

if target in content:
    content = content.replace(target, replacement)
    print("成功删除重复代码")
else:
    print("未找到目标代码，可能已经被删除或格式不同")

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
