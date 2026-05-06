#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换
old_code = """            # 调用处理计划方法，设置auto_print=True，这样处理完成后会自动打印
            self.process_plans(auto_print=True, show_result=False)
            
            print("\\n=== 重新导出打印完成 ===")
            
        except Exception as e:
            print(f"重新导出打印失败: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"重新导出打印失败: {str(e)}")"""

new_code = """            # 调用处理计划方法，设置auto_print=True，这样处理完成后会自动打印
            self.process_plans(auto_print=True, show_result=False)
            
            # 回到主程序画面（轧制计划管理系统）
            print("\\n【步骤6】回到主程序画面...")
            self.activateWindow()
            self.raise_()
            self.show()
            self.activateWindow()
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            self.activateWindow()
            print("  ✓ 已回到主程序画面")
            
            print("\\n=== 重新导出打印完成 ===")
            
        except Exception as e:
            print(f"重新导出打印失败: {str(e)}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"重新导出打印失败: {str(e)}")"""

content = content.replace(old_code, new_code)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
