# -*- coding: utf-8 -*-
"""
添加打印功能到 furnace_order_manager_pyqt5.py
"""

# 读取原文件
with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在打印按钮添加后添加信号连接
old_btn_code = '''        center_buttons.addWidget(self.print_btn)
        
        # 全部打印复选框'''

new_btn_code = '''        center_buttons.addWidget(self.print_btn)
        
        # 连接打印按钮信号
        self.print_btn.clicked.connect(self.print_furnace_details)
        
        # 全部打印复选框'''

content = content.replace(old_btn_code, new_btn_code)

# 2. 在 run_excel_macro_with_pandas 方法之前添加打印方法
old_method = '''    def run_excel_macro_with_pandas(self, file_path):'''

new_method = '''    def print_furnace_details(self):
        """打印装炉明细 - 像主程序画面中的格式打印"""
        try:
            import os
            import time
            import xlwt
            
            # 获取所有数据
            rows = []
            for row_idx in range(self.table_widget.rowCount()):
                row_data = []
                for col_idx in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row_idx, col_idx)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                rows.append(row_data)
            
            if not rows:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "没有数据可打印")
                return
            
            # 创建临时 Excel 文件（存储在计划号文件夹中）
            plan_dir = os.path.join(self.plan_dir, "计划号")
            temp_file_name = f"temp_装炉明细打印_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            
            # 创建工作簿和工作表
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet('装炉明细')
            
            # 设置列名
            提示行 = ["装炉明细打印"]
            headers = ["序号", "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度"]
            
            # 定义样式
            # 大标题样式
            style_title = xlwt.XFStyle()
            font_title = xlwt.Font()
            font_title.name = '仿宋'
            font_title.height = 280  # 14pt
            font_title.bold = True
            style_title.font = font_title
            alignment_title = xlwt.Alignment()
            alignment_title.horz = xlwt.Alignment.HORZ_CENTER
            alignment_title.vert = xlwt.Alignment.VERT_CENTER
            style_title.alignment = alignment_title
            
            # 打印时间样式（右对齐）
            style_time = xlwt.XFStyle()
            font_time = xlwt.Font()
            font_time.name = '仿宋'
            font_time.height = 200  # 10pt
            font_time.bold = True
            style_time.font = font_time
            alignment_time = xlwt.Alignment()
            alignment_time.horz = xlwt.Alignment.HORZ_RIGHT
            alignment_time.vert = xlwt.Alignment.VERT_CENTER
            style_time.alignment = alignment_time
            
            # 字段列名样式（带边框）
            style_header_border = xlwt.XFStyle()
            font_header_border = xlwt.Font()
            font_header_border.name = '仿宋'
            font_header_border.height = 280  # 14pt
            font_header_border.bold = True
            style_header_border.font = font_header_border
            alignment_header_border = xlwt.Alignment()
            alignment_header_border.horz = xlwt.Alignment.HORZ_CENTER
            alignment_header_border.vert = xlwt.Alignment.VERT_CENTER
            style_header_border.alignment = alignment_header_border
            borders_header = xlwt.Borders()
            borders_header.left = xlwt.Borders.THIN
            borders_header.right = xlwt.Borders.THIN
            borders_header.top = xlwt.Borders.THIN
            borders_header.bottom = xlwt.Borders.THIN
            style_header_border.borders = borders_header
            
            # 字段列名样式（强度字段，8pt 字号）
            style_header_strength = xlwt.XFStyle()
            font_header_strength = xlwt.Font()
            font_header_strength.name = '仿宋'
            font_header_strength.height = 160  # 8pt
            font_header_strength.bold = True
            style_header_strength.font = font_header_strength
            style_header_strength.alignment = alignment_header_border
            style_header_strength.borders = borders_header
            
            # 序号列样式（14pt）- 左边框为实线
            style_data_seq = xlwt.XFStyle()
            font_data_seq = xlwt.Font()
            font_data_seq.name = '仿宋'
            font_data_seq.height = 280  # 14pt
            font_data_seq.bold = True
            style_data_seq.font = font_data_seq
            alignment_data = xlwt.Alignment()
            alignment_data.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data.vert = xlwt.Alignment.VERT_CENTER
            style_data_seq.alignment = alignment_data
            borders_data_seq = xlwt.Borders()
            borders_data_seq.left = xlwt.Borders.THIN
            borders_data_seq.right = xlwt.Borders.NO_LINE
            borders_data_seq.top = xlwt.Borders.THIN
            borders_data_seq.bottom = xlwt.Borders.THIN
            style_data_seq.borders = borders_data_seq
            
            # 数据行样式（带边框，去掉竖线）
            borders_data = xlwt.Borders()
            borders_data.left = xlwt.Borders.NO_LINE
            borders_data.right = xlwt.Borders.NO_LINE
            borders_data.top = xlwt.Borders.THIN
            borders_data.bottom = xlwt.Borders.THIN
            
            # 钢卷号列样式（16pt）
            style_data_coil = xlwt.XFStyle()
            font_data_coil = xlwt.Font()
            font_data_coil.name = '仿宋'
            font_data_coil.height = 320  # 16pt
            font_data_coil.bold = True
            style_data_coil.font = font_data_coil
            style_data_coil.alignment = alignment_data
            style_data_coil.borders = borders_data
            
            # 14pt 样式
            style_data_14pt = xlwt.XFStyle()
            font_data_14pt = xlwt.Font()
            font_data_14pt.name = '仿宋'
            font_data_14pt.height = 280  # 14pt
            font_data_14pt.bold = True
            style_data_14pt.font = font_data_14pt
            alignment_data_14pt = xlwt.Alignment()
            alignment_data_14pt.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_14pt.vert = xlwt.Alignment.VERT_CENTER
            style_data_14pt.alignment = alignment_data_14pt
            style_data_14pt.borders = borders_data
            
            # 12pt 样式
            style_data_12pt = xlwt.XFStyle()
            font_data_12pt = xlwt.Font()
            font_data_12pt.name = '仿宋'
            font_data_12pt.height = 240  # 12pt
            font_data_12pt.bold = True
            style_data_12pt.font = font_data_12pt
            alignment_data_12pt = xlwt.Alignment()
            alignment_data_12pt.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data_12pt.vert = xlwt.Alignment.VERT_CENTER
            style_data_12pt.alignment = alignment_data_12pt
            style_data_12pt.borders = borders_data
            
            # 12pt 样式（强度列）- 右边框为实线
            style_data_12pt_strength = xlwt.XFStyle()
            font_data_12pt_strength = xlwt.Font()
            font_data_12pt_strength.name = '仿宋'
            font_data_12pt_strength.height = 240  # 12pt
            font_data_12pt_strength.bold = True
            style_data_12pt_strength.font = font_data_12pt_strength
            style_data_12pt_strength.alignment = alignment_data_12pt
            borders_data_strength = xlwt.Borders()
            borders_data_strength.left = xlwt.Borders.NO_LINE
            borders_data_strength.right = xlwt.Borders.THIN
            borders_data_strength.top = xlwt.Borders.THIN
            borders_data_strength.bottom = xlwt.Borders.THIN
            style_data_12pt_strength.borders = borders_data_strength
            
            # 设置列宽
            col_widths = [
                int(5.5 * 256 * 1.2),       # 1. 序号
                int(7.0 * 256 * 1.04),       # 2. 计划号
                int(19 * 256 * 1.04),        # 3. 钢卷号
                int(18 * 256 * 1.04),       # 4. 牌号（钢级）
                int(7 * 256 * 1.04),         # 5. 坯宽
                int(7 * 256 * 1.05),         # 6. 减宽（侧压量）
                int(6 * 256 * 1.2),          # 7. 调宽
                int(7 * 256 * 1.13),         # 8. 轧宽
                int(9 * 256 * 1.03),         # 9. 公差带
                int(33 * 256 * 1.04),        # 10. 粗轧报信
                int(7 * 256 * 1.08),         # 11. 除鳞
                int(7 * 256 * 1.04),         # 12. 坯厚
                int(6.2 * 256 * 1.13),       # 13. 坯长
                int(6 * 256 * 1.04),         # 14. 轧厚
                int(5 * 256 * 1.04),         # 15. 中厚
                int(6.57 * 256 * 1.04),      # 16. RT2
                int(2 * 256 * 1.2)           # 17. 强度
            ]
            
            for col_idx, width in enumerate(col_widths):
                if col_idx < len(headers):
                    sheet.col(col_idx).width = width
                    sheet.col(col_idx).width_mismatch = True
            
            # 写入提示行（第一行）并合并单元格
            sheet.write_merge(0, 0, 0, len(headers) - 1, 提示行 [0], style_title)
            sheet.row(0).height = 460  # 23pt
            sheet.row(0).height_mismatch = True
            
            # 第二行：打印时间
            print_time = time.strftime("%Y-%m-%d %H:%M:%S")
            sheet.write(1, len(headers) - 1, f"打印时间：{print_time}", style_time)
            sheet.row(1).height = 460  # 23pt
            sheet.row(1).height_mismatch = True
            
            # 写入字段名行（第三行）
            for col, header in enumerate(headers):
                if col == len(headers) - 1:  # 强度字段
                    sheet.write(2, col, header, style_header_strength)
                else:
                    sheet.write(2, col, header, style_header_border)
            sheet.row(2).height = 500  # 25pt
            sheet.row(2).height_mismatch = True
            
            # 写入数据行
            seq_num = 1
            for row_idx, row_data in enumerate(rows):
                # 写入序号
                sheet.write(row_idx + 3, 0, seq_num, style_data_seq)
                
                # 写入其他字段
                for col_idx, value in enumerate(row_data[1:], 1):  # 跳过第一列（序号）
                    if col_idx == 2:  # 钢卷号列（16pt）
                        sheet.write(row_idx + 3, col_idx, value, style_data_coil)
                    elif col_idx in [4, 5, 6, 7, 11, 15]:  # 14pt 列
                        sheet.write(row_idx + 3, col_idx, value, style_data_14pt)
                    elif col_idx == 16:  # 强度列（12pt，右边框实线）
                        sheet.write(row_idx + 3, col_idx, value, style_data_12pt_strength)
                    else:  # 其他 12pt 列
                        sheet.write(row_idx + 3, col_idx, value, style_data_12pt)
                
                seq_num += 1
            
            # 保存文件
            workbook.save(temp_file_path)
            print(f"已生成打印文件：{temp_file_path}")
            
            # 使用 pywin32 打印文件
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            
            # 打开工作簿
            workbook_com = excel.Workbooks.Open(temp_file_path)
            
            # 打印活动工作表
            workbook_com.ActiveSheet.PrintOut()
            
            # 关闭工作簿
            workbook_com.Close(SaveChanges=False)
            
            # 退出 Excel
            excel.Quit()
            
            # 删除临时文件
            import time
            time.sleep(1)  # 等待打印完成
            os.remove(temp_file_path)
            print(f"已删除临时文件：{temp_file_path}")
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "完成", "打印完成")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            QMessageBox.critical(self, "错误", f"打印失败：{str(e)}")
            print(f"打印失败：{str(e)}")
            print(traceback.format_exc())
    
    def run_excel_macro_with_pandas(self, file_path):'''

# 替换
content = content.replace(old_method, new_method)

# 写入文件
with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加打印功能到 furnace_order_manager_pyqt5.py")
