# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改钢卷号样式，使用左对齐
old_text = '''        # 钢卷号左对齐样式（16pt - 用于钢卷号，带下边框）
        style_data_16pt_left = xlwt.XFStyle()
        font_data_16pt_left = xlwt.Font()
        font_data_16pt_left.name = '仿宋'
        font_data_16pt_left.height = 320  # 16pt
        font_data_16pt_left.bold = True
        style_data_16pt_left.font = font_data_16pt_left
        style_data_16pt_left.alignment = alignment_data  # 左对齐
        borders_data_16pt_left = xlwt.Borders()
        borders_data_16pt_left.left = xlwt.Borders.NO_LINE
        borders_data_16pt_left.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left.top = xlwt.Borders.NO_LINE
        borders_data_16pt_left.bottom = xlwt.Borders.THIN  # 下边框
        style_data_16pt_left.borders = borders_data_16pt_left'''

new_text = '''        # 钢卷号左对齐样式（16pt - 用于钢卷号，带下边框）
        style_data_16pt_left = xlwt.XFStyle()
        font_data_16pt_left = xlwt.Font()
        font_data_16pt_left.name = '仿宋'
        font_data_16pt_left.height = 320  # 16pt
        font_data_16pt_left.bold = True
        style_data_16pt_left.font = font_data_16pt_left
        # 创建左对齐配置
        alignment_data_16pt_left = xlwt.Alignment()
        alignment_data_16pt_left.horz = xlwt.Alignment.HORZ_LEFT  # 左对齐
        alignment_data_16pt_left.vert = xlwt.Alignment.VERT_CENTER
        style_data_16pt_left.alignment = alignment_data_16pt_left
        borders_data_16pt_left = xlwt.Borders()
        borders_data_16pt_left.left = xlwt.Borders.NO_LINE
        borders_data_16pt_left.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left.top = xlwt.Borders.NO_LINE
        borders_data_16pt_left.bottom = xlwt.Borders.THIN  # 下边框
        style_data_16pt_left.borders = borders_data_16pt_left'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修复钢卷号样式：使用左对齐")
