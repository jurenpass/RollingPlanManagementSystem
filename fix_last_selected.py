#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改1: 在 FurnaceDetailsWindow 的 __init__ 中添加保存最后选中钢卷号的变量
old_furnace_init = """class FurnaceDetailsWindow(QMainWindow):
    \"\"\"装炉明细窗口\"\"\"
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("装炉明细")
        self.showMaximized()
        
        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)"""

new_furnace_init = """class FurnaceDetailsWindow(QMainWindow):
    \"\"\"装炉明细窗口\"\"\"
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("装炉明细")
        self.showMaximized()

        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # 记录最后选中的钢卷号，用于恢复定位
        self.last_selected_coil_no = None"""

content = content.replace(old_furnace_init, new_furnace_init)

# 修改2: 在 closeEvent 中添加保存最后选中的钢卷号
old_close_event = """    def closeEvent(self, event):
        \"\"\"窗口关闭时的事件处理\"\"\"
        try:
            # 先关闭设置窗口（如果存在且可见），触发设置窗口的保存逻辑
            if hasattr(self, 'settings_window') and self.settings_window.isVisible():
                self.settings_window.close()
            # 保存窗口状态
            self.save_window_state()
            # 停止滚动定时器
            if self.scroll_timer.isActive():
                self.scroll_timer.stop()
            # 保存状态
            self.save_current_table_data()
            # 保存标注条件"""

new_close_event = """    def closeEvent(self, event):
        \"\"\"窗口关闭时的事件处理\"\"\"
        try:
            # 先关闭设置窗口（如果存在且可见），触发设置窗口的保存逻辑
            if hasattr(self, 'settings_window') and self.settings_window.isVisible():
                self.settings_window.close()
            # 保存窗口状态
            self.save_window_state()
            # 停止滚动定时器
            if self.scroll_timer.isActive():
                self.scroll_timer.stop()
            # 保存状态
            self.save_current_table_data()
            # 保存最后选中的钢卷号
            self.save_last_selected_coil()
            # 保存标注条件"""

content = content.replace(old_close_event, new_close_event)

# 修改3: 在 FurnaceDetailsWindow 类中添加保存和恢复选中钢卷号的方法
# 在 save_current_table_data 方法之前添加
old_save_table_data = """    def save_current_table_data(self):
        \"\"\"保存当前表格数据到文件\"\"\""""

new_save_table_data = """    def save_last_selected_coil(self):
        \"\"\"保存最后选中的钢卷号\"\"\"
        try:
            # 获取当前选中的行
            current_row = self.table_widget.currentRow()
            if current_row >= 0:
                # 获取该行的钢卷号（第1列）
                coil_item = self.table_widget.item(current_row, 1)  # 钢卷号在第1列
                if coil_item and coil_item.text().strip():
                    self.last_selected_coil_no = coil_item.text().strip()
                    print(f"保存最后选中的钢卷号: {self.last_selected_coil_no}")

                    # 保存到配置文件
                    import json
                    import os
                    config_file = os.path.join(self.parent.plan_dir if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'plan_dir') else os.getcwd(), "last_selected_coil.json")
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump({'last_selected_coil_no': self.last_selected_coil_no}, f, ensure_ascii=False)
        except Exception as e:
            print(f"保存最后选中的钢卷号失败: {e}")

    def restore_selected_coil(self):
        \"\"\"恢复上次选中的钢卷号位置\"\"\"
        try:
            # 读取保存的钢卷号
            import json
            import os
            config_file = os.path.join(self.parent.plan_dir if hasattr(self, 'parent') and self.parent and hasattr(self.parent, 'plan_dir') else os.getcwd(), "last_selected_coil.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    target_coil_no = data.get('last_selected_coil_no')
                    if target_coil_no:
                        print(f"尝试定位到钢卷号: {target_coil_no}")

                        # 在表格中查找该钢卷号
                        for row in range(self.table_widget.rowCount()):
                            coil_item = self.table_widget.item(row, 1)  # 钢卷号在第1列
                            if coil_item and coil_item.text().strip() == target_coil_no:
                                # 选中该行
                                self.table_widget.selectRow(row)
                                self.table_widget.setCurrentCell(row, 0)
                                # 滚动到该行
                                self.table_widget.scrollToItem(self.table_widget.item(row, 0))
                                print(f"已定位到钢卷号: {target_coil_no} (第{row+1}行)")
                                return True

                        print(f"未找到钢卷号: {target_coil_no}，将定位到第一行")
                        # 如果没找到，定位到第一行
                        if self.table_widget.rowCount() > 0:
                            self.table_widget.selectRow(0)
                            self.table_widget.setCurrentCell(0, 0)
                            self.table_widget.scrollToItem(self.table_widget.item(0, 0))
                            print("已定位到第一行")
                        return False
            else:
                # 如果没有保存的钢卷号，定位到第一行
                if self.table_widget.rowCount() > 0:
                    self.table_widget.selectRow(0)
                    self.table_widget.setCurrentCell(0, 0)
                    self.table_widget.scrollToItem(self.table_widget.item(0, 0))
                    print("已定位到第一行（无保存记录）")
        except Exception as e:
            print(f"恢复选中钢卷号失败: {e}")
            # 出错时也定位到第一行
            if self.table_widget.rowCount() > 0:
                self.table_widget.selectRow(0)
                self.table_widget.setCurrentCell(0, 0)

    def save_current_table_data(self):
        \"\"\"保存当前表格数据到文件\"\"\""""

content = content.replace(old_save_table_data, new_save_table_data)

# 修改4: 在 refresh_data 方法中调用 restore_selected_coil
old_refresh_data = """        def refresh_data():
            \"\"\"刷新装炉明细数据\"\"\"
            print("刷新装炉明细数据...")
            self.load_furnace_data()
            # 刷新数据后，保存当前数据，确保打印时能正确识别新增的钢卷号
            self.save_current_table_data()
        self.refresh_data = refresh_data"""

new_refresh_data = """        def refresh_data():
            \"\"\"刷新装炉明细数据\"\"\"
            print("刷新装炉明细数据...")
            self.load_furnace_data()
            # 刷新数据后，恢复上次选中的钢卷号位置
            self.restore_selected_coil()
            # 保存当前数据，确保打印时能正确识别新增的钢卷号
            self.save_current_table_data()
        self.refresh_data = refresh_data"""

content = content.replace(old_refresh_data, new_refresh_data)

# 修改5: 在 go_to_furnace_details 中打开/激活窗口后也调用 restore_selected_coil
old_go_to_furnace = """                                    if not has_furnace_details_window:
                                        # 如果没有装炉明细窗口，打开新的装炉明细窗口
                                        print("未找到装炉明细窗口，打开新的装炉明细画面")
                                        self.open_furnace_details()
                                        print("成功打开装炉明细窗口")"""

new_go_to_furnace = """                                    if not has_furnace_details_window:
                                        # 如果没有装炉明细窗口，打开新的装炉明细窗口
                                        print("未找到装炉明细窗口，打开新的装炉明细画面")
                                        self.open_furnace_details()
                                        print("成功打开装炉明细窗口")"""

# 由于字符串冲突，需要用不同的方式替换
# 直接在窗口激活后添加 restore_selected_coil 调用
old_activate_code = """                                        # 刷新装炉明细数据
                                            if hasattr(widget, 'refresh_data'):
                                                print("刷新装炉明细窗口数据")
                                                widget.refresh_data()"""

new_activate_code = """                                        # 刷新装炉明细数据
                                            if hasattr(widget, 'refresh_data'):
                                                print("刷新装炉明细窗口数据")
                                                widget.refresh_data()
                                                # 刷新后恢复上次选中的钢卷号位置
                                                if hasattr(widget, 'restore_selected_coil'):
                                                    widget.restore_selected_coil()"""

content = content.replace(old_activate_code, new_activate_code)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
