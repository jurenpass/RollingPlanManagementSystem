#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = """    def re_export_and_print_selected(self):
        \"\"\"重新导出并打印选中的计划号
        
        功能说明：
        1. 重新导出总计划号列表.xls并重新计算获取所选计划号的坐标
        2. 重新导出所选计划号明细
        3. 打印所选计划号明细
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
            
            # 步骤1: 重新导出总计划号列表
            print("\\n【步骤1】重新导出总计划号列表...")
            success = self.export_zhizhi_plan_list(test_window=None, add_debug_log=print)
            if not success:
                QMessageBox.critical(self, "错误", "重新导出总计划号列表失败")
                return
            
            # 步骤2: 读取总计划号列表并计算坐标
            print("\\n【步骤2】读取总计划号列表并计算坐标...")
            plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
            if not os.path.exists(plan_list_file):
                QMessageBox.critical(self, "错误", f"总计划号列表文件不存在: {plan_list_file}")
                return
            
            # 读取总计划号列表并计算坐标
            coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=print)
            if not coord_map:
                QMessageBox.critical(self, "错误", "计算计划号坐标失败")
                return
            
            print(f"\\n计算完成，共获取 {len(coord_map)} 个计划号的坐标")
            
            # 步骤3: 重新导出所选计划号明细
            print("\\n【步骤3】重新导出所选计划号明细...")
            for plan_no in selected_plans:
                if plan_no not in coord_map:
                    print(f"  跳过 {plan_no}，未找到坐标")
                    continue
                
                plan_coord = coord_map[plan_no]
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", [79, 859])
                
                print(f"  导出计划号: {plan_no}, 坐标: {plan_coord}")
                success = self.export_single_plan_detail(
                    plan_no, 
                    plan_coord, 
                    plan_detail_export_btn=plan_detail_export_btn, 
                    test_window=None, 
                    add_debug_log=print
                )
                if success:
                    print(f"  ✓ {plan_no} 导出成功")
                else:
                    print(f"  ✗ {plan_no} 导出失败")
            
            # 步骤4: 打印所选计划号
            print("\\n【步骤4】打印所选计划号明细...")
            # 选中计划号
            self.table_widget.clearSelection()
            for i, plan_data in enumerate(self.plan_data):
                if plan_data['plan_no'] in selected_plans:
                    self.table_widget.selectRow(i)
            
            # 调用打印功能
            self.print_selected()
            
            print("\\n=== 重新导出打印完成 ===")
            
        except Exception as e:
            print(f"重新导出打印失败: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"重新导出打印失败: {str(e)}")"""

new_func = """    def re_export_and_print_selected(self):
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
                return
            
            # 步骤2: 读取总计划号列表并计算坐标
            print("\\n【步骤2】读取总计划号列表并计算坐标...")
            plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
            if not os.path.exists(plan_list_file):
                QMessageBox.critical(self, "错误", f"总计划号列表文件不存在: {plan_list_file}")
                return
            
            # 读取总计划号列表并计算坐标
            coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=print)
            if not coord_map:
                QMessageBox.critical(self, "错误", "计算计划号坐标失败")
                return
            
            print(f"\\n计算完成，共获取 {len(coord_map)} 个计划号的坐标")
            
            # 步骤3: 重新导出所选计划号明细
            print("\\n【步骤3】重新导出所选计划号明细...")
            for plan_no in selected_plans:
                if plan_no not in coord_map:
                    print(f"  跳过 {plan_no}，未找到坐标")
                    continue
                
                plan_coord = coord_map[plan_no]
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", [79, 859])
                
                print(f"  导出计划号: {plan_no}, 坐标: {plan_coord}")
                success = self.export_single_plan_detail(
                    plan_no, 
                    plan_coord, 
                    plan_detail_export_btn=plan_detail_export_btn, 
                    test_window=test_window, 
                    add_debug_log=print
                )
                if success:
                    print(f"  ✓ {plan_no} 导出成功")
                else:
                    print(f"  ✗ {plan_no} 导出失败")
            
            # 刷新数据，确保plan_data是最新的
            print("\\n【步骤4】刷新数据...")
            self.load_data()
            
            # 步骤5: 处理计划并打印
            print("\\n【步骤5】处理计划并打印...")
            # 选中计划号
            self.table_widget.clearSelection()
            for i, plan_data in enumerate(self.plan_data):
                if plan_data['plan_no'] in selected_plans:
                    self.table_widget.selectRow(i)
            
            # 调用处理计划方法，设置auto_print=True，这样处理完成后会自动打印
            self.process_plans(auto_print=True, show_result=False)
            
            print("\\n=== 重新导出打印完成 ===")
            
        except Exception as e:
            print(f"重新导出打印失败: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"重新导出打印失败: {str(e)}")
    
    def activate_target_window(self, window_title, add_debug_log=None):
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

content = content.replace(old_func, new_func)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
