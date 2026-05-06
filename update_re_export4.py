#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改1: 更新 process_plans 方法签名，添加 force_process 参数
old_signature = """    def process_plans(self, auto_print=False, show_result=True):
        \"\"\"处理计划号文件 - 使用 pandas + xlwt 方案
        
        Args:
            auto_print: 是否在处理完成后自动打印（默认False,仅自动导出流程中为True）
            show_result: 是否显示处理结果弹窗（默认True,在显示按钮调用时为False）
        \"\"\""""

new_signature = """    def process_plans(self, auto_print=False, show_result=True, force_process=False):
        \"\"\"处理计划号文件 - 使用 pandas + xlwt 方案
        
        Args:
            auto_print: 是否在处理完成后自动打印（默认False,仅自动导出流程中为True）
            show_result: 是否显示处理结果弹窗（默认True,在显示按钮调用时为False）
            force_process: 是否强制处理（忽略已处理状态，默认False）
        \"\"\""""

content = content.replace(old_signature, new_signature)

# 修改2: 更新已处理检查逻辑，当 force_process=True 时跳过检查
old_check = """            if already_processed and show_result:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText(f"以下计划号已处理过,无需重复处理：\\n\\n{', '.join(already_processed)}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return"""

new_check = """            # 如果不是强制处理，检查已处理状态
            if already_processed and show_result and not force_process:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText(f"以下计划号已处理过,无需重复处理：\\n\\n{', '.join(already_processed)}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return"""

content = content.replace(old_check, new_check)

# 修改3: 更新重新导出打印调用，添加 force_process=True
old_call = """            # 调用处理计划方法，设置auto_print=True，这样处理完成后会自动打印
            self.process_plans(auto_print=True, show_result=False)"""

new_call = """            # 调用处理计划方法，设置auto_print=True和force_process=True，强制处理并自动打印
            self.process_plans(auto_print=True, show_result=False, force_process=True)"""

content = content.replace(old_call, new_call)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
