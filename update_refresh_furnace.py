#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 FurnaceDetailsWindow 类的 load_furnace_data 方法调用后添加刷新方法
old_code = """        # 加载数据
        self.load_furnace_data()
        
        # 创建自动滚动定时器"""

new_code = """        # 加载数据
        self.load_furnace_data()

        # 创建刷新数据的方法，供外部调用
        def refresh_data():
            \"\"\"刷新装炉明细数据\"\"\"
            print("刷新装炉明细数据...")
            self.load_furnace_data()
        self.refresh_data = refresh_data
        
        # 创建自动滚动定时器"""

content = content.replace(old_code, new_code)

# 修改自动执行完成后打开装炉明细画面的代码，使用刷新方法替代关闭再打开
old_auto_code = """                # 自动执行模式下，打开装炉明细画面并更新数据
                if not from_main_window:
                    # 自动执行完打开装炉明细画面，确保数据更新
                    print("30秒后打开装炉明细窗口...")
                    # 直接在单独的线程中打开装炉明细窗口，避免事件循环冲突
                    import threading
                    def open_furnace_details():
                        # 延迟30秒执行
                        import time
                        time.sleep(30)
                        # 先检查是否已有装炉明细窗口，如果有则关闭它以更新数据
                        from PyQt5.QtWidgets import QApplication
                        existing_furnace_details = []
                        for widget in QApplication.topLevelWidgets():
                            if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                                existing_furnace_details.append(widget)
                        
                        # 关闭所有已有的装炉明细窗口，确保数据更新
                        for widget in existing_furnace_details:
                            print(f"关闭已有的装炉明细窗口以更新数据")
                            widget.close()
                        
                        # 打开新的装炉明细窗口，确保数据是最新的
                        print("打开新的装炉明细画面")
                        try:
                            self.furnace_details()
                            print("成功打开装炉明细窗口，数据已更新")
                        except Exception as e:
                            print(f"打开装炉明细窗口失败: {str(e)}")
                    # 启动新线程
                    threading.Thread(target=open_furnace_details, daemon=True).start()"""

new_auto_code = """                # 自动执行模式下，打开装炉明细画面并更新数据
                if not from_main_window:
                    # 自动执行完打开装炉明细画面，刷新数据而不关闭窗口
                    print("30秒后刷新装炉明细窗口数据...")
                    # 直接在单独的线程中刷新装炉明细窗口数据，避免事件循环冲突
                    import threading
                    def refresh_furnace_details():
                        # 延迟30秒执行
                        import time
                        time.sleep(30)
                        # 先检查是否已有装炉明细窗口
                        from PyQt5.QtWidgets import QApplication
                        existing_furnace_details = []
                        for widget in QApplication.topLevelWidgets():
                            if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                                existing_furnace_details.append(widget)

                        if existing_furnace_details:
                            # 如果有装炉明细窗口，刷新数据而不关闭
                            for widget in existing_furnace_details:
                                print(f"刷新装炉明细窗口数据")
                                # 调用刷新方法
                                if hasattr(widget, 'refresh_data'):
                                    widget.refresh_data()
                                # 激活窗口
                                widget.activateWindow()
                                widget.raise_()
                                widget.show()
                            print("装炉明细窗口数据已刷新")
                        else:
                            # 如果没有装炉明细窗口，打开新的
                            print("未找到装炉明细窗口，打开新的装炉明细画面")
                            try:
                                self.open_furnace_details()
                                print("成功打开装炉明细窗口")
                            except Exception as e:
                                print(f"打开装炉明细窗口失败: {str(e)}")
                    # 启动新线程
                    threading.Thread(target=refresh_furnace_details, daemon=True).start()"""

content = content.replace(old_auto_code, new_auto_code)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
