#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改1: 更新 activate_target_window 方法，不取消最大化
old_activate = """    def activate_target_window(self, window_title, add_debug_log=None):
        \"\"\"激活目标窗口
        
        参数:
            window_title: 目标窗口标题
            add_debug_log: 调试日志函数
            
        返回:
            True - 激活成功
            False - 激活失败
        \"\"\"
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import win32gui
            import win32con
            
            add_debug_log(f"  目标窗口: {window_title}")
            
            # 查找窗口
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                # 先ShowWindow再SetForegroundWindow
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                # 额外尝试：使用SetWindowPos
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                add_debug_log("  ✓ 成功激活目标窗口")
                return True
            else:
                add_debug_log("  ✗ 未找到目标窗口")
                return False
                
        except Exception as e:
            add_debug_log(f"  ✗ 激活窗口失败: {str(e)}")
            return False"""

new_activate = """    def activate_target_window(self, window_title, add_debug_log=None):
        \"\"\"激活目标窗口
        
        参数:
            window_title: 目标窗口标题
            add_debug_log: 调试日志函数
            
        返回:
            True - 激活成功
            False - 激活失败
        \"\"\"
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import win32gui
            import win32con
            
            add_debug_log(f"  目标窗口: {window_title}")
            
            # 查找窗口
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                # 直接激活窗口，不改变其大小和状态（保持最大化）
                win32gui.SetForegroundWindow(hwnd)
                # 额外尝试：使用SetWindowPos确保窗口在最前面
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                add_debug_log("  ✓ 成功激活目标窗口")
                return True
            else:
                add_debug_log("  ✗ 未找到目标窗口")
                return False
                
        except Exception as e:
            add_debug_log(f"  ✗ 激活窗口失败: {str(e)}")
            return False"""

content = content.replace(old_activate, new_activate)

# 修改2: 更新 re_export_and_print_selected 方法，添加点击轧制计划管理标签的步骤
old_reexport = """    def re_export_and_print_selected(self):
        \"\"\"重新导出并打印选中的计划号
        
        功能说明：
        1. 激活目标软件窗口（BGCMS系统）
        2. 重新导出总计划号列表.xls
        3. 计算坐标，获取所选计划号的坐标
        4. 重新导出所选计划号明细.xls
        5. 执行处理计划
        6. 打印所选计划号明细
        \"\"\"
        try:
            from PyQt5.QtWidgets import QMessageBox
            from PyQt5.QtCore import Qt
            
            # 检查是否选择了计划号
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                self.activateWindow()
                self.raise_()
                self.show()
                QMessageBox.warning(self, "警告", "请先在计划号列表中选择要重新导出打印的计划号")
                return
            
            # 获取选中的计划号
            selected_rows = sorted([index.row() for index in selected_items])
            selected_plans = [self.plan_data[row]['plan_no'] for row in selected_rows]
            
            print(f"\\n=== 开始重新导出打印 ===")
            print(f"选中的计划号: {selected_plans}")
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            if not os.path.exists(plan_dir):
                QMessageBox.critical(self, "错误", f"计划号文件夹不存在: {plan_dir}")
                return
            
            # 获取设置中的目标窗口
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            # 步骤0: 激活目标软件窗口
            print("\\n【步骤0】激活目标软件窗口...")
            success = self.activate_target_window(test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", f"无法激活目标窗口: {test_window}")
                return
            
            # 步骤1: 重新导出总计划号列表
            print("\\n【步骤1】重新导出总计划号列表...")
            success = self.export_zhizhi_plan_list(test_window=test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", "重新导出总计划号列表失败")
                return"""

new_reexport = """    def re_export_and_print_selected(self):
        \"\"\"重新导出并打印选中的计划号
        
        功能说明：
        1. 激活目标软件窗口（BGCMS系统）
        2. 点击轧制计划管理标签 [107, 85]
        3. 重新导出总计划号列表.xls
        4. 计算坐标，获取所选计划号的坐标
        5. 重新导出所选计划号明细.xls
        6. 执行处理计划
        7. 打印所选计划号明细
        \"\"\"
        try:
            from PyQt5.QtWidgets import QMessageBox
            from PyQt5.QtCore import Qt
            
            # 检查是否选择了计划号
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                self.activateWindow()
                self.raise_()
                self.show()
                QMessageBox.warning(self, "警告", "请先在计划号列表中选择要重新导出打印的计划号")
                return
            
            # 获取选中的计划号
            selected_rows = sorted([index.row() for index in selected_items])
            selected_plans = [self.plan_data[row]['plan_no'] for row in selected_rows]
            
            print(f"\\n=== 开始重新导出打印 ===")
            print(f"选中的计划号: {selected_plans}")
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            if not os.path.exists(plan_dir):
                QMessageBox.critical(self, "错误", f"计划号文件夹不存在: {plan_dir}")
                return
            
            # 获取设置中的目标窗口
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            # 获取轧制计划管理标签坐标
            zhizhi_tab = self.coordinates.get("zhizhi_tab", [107, 85])
            
            # 步骤0: 激活目标软件窗口
            print("\\n【步骤0】激活目标软件窗口...")
            success = self.activate_target_window(test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", f"无法激活目标窗口: {test_window}")
                return
            
            # 步骤0.5: 点击轧制计划管理标签
            print("\\n【步骤0.5】点击轧制计划管理标签...")
            print(f"  坐标: {zhizhi_tab}")
            try:
                import pyautogui
                import time
                pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
                time.sleep(0.2)
                pyautogui.click()
                time.sleep(0.5)
                print("  ✓ 点击成功")
            except Exception as e:
                print(f"  ✗ 点击失败: {str(e)}")
                QMessageBox.critical(self, "错误", f"点击轧制计划管理标签失败: {str(e)}")
                return
            
            # 步骤1: 重新导出总计划号列表
            print("\\n【步骤1】重新导出总计划号列表...")
            success = self.export_zhizhi_plan_list(test_window=test_window, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", "重新导出总计划号列表失败")
                return"""

content = content.replace(old_reexport, new_reexport)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
