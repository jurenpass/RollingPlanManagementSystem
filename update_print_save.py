#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改1: 在 refresh_data 方法中添加 save_current_table_data 调用
# 先找到 refresh_data 方法的位置
old_refresh = """            self.load_furnace_data()
        self.refresh_data = refresh_data"""
new_refresh = """            self.load_furnace_data()
            # 刷新数据后，保存当前数据，确保打印时能正确识别新增的钢卷号
            self.save_current_table_data()
        self.refresh_data = refresh_data"""
content = content.replace(old_refresh, new_refresh)

# 修改2: 在 print_furnace_details 方法中，打印成功后添加 save_current_table_data 调用
# 在 win32com 打印成功后添加
old_win32_end = """                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
                    workbook.release_resources()
                
                return True"""
new_win32_end = """                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
                    workbook.release_resources()
                
                # 打印成功后，保存当前数据，确保下次打印能正确识别新增的钢卷号
                self.save_current_table_data()
                return True"""
content = content.replace(old_win32_end, new_win32_end)

# 修改3: 在默认打印方式成功后也添加 save_current_table_data 调用
old_default_print = """                        return True
                    else:
                        print("非Windows系统，无法使用默认打印方式")
                        return False"""
new_default_print = """                        # 打印成功后，保存当前数据，确保下次打印能正确识别新增的钢卷号
                        self.save_current_table_data()
                        return True
                    else:
                        print("非Windows系统，无法使用默认打印方式")
                        return False"""
content = content.replace(old_default_print, new_default_print)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
