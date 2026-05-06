# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在 style_data_16pt_left_border 之后添加 style_data_16pt_left 样式定义
old_text = '''        style_data_16pt_left_border.borders = borders_data_16pt_left_border
        
        # 装炉顺列右侧实线边框样式（12pt）'''

new_text = '''        style_data_16pt_left_border.borders = borders_data_16pt_left_border
        
        # 钢卷号左对齐样式（16pt - 用于钢卷号，无边框）
        style_data_16pt_left = xlwt.XFStyle()
        font_data_16pt_left = xlwt.Font()
        font_data_16pt_left.name = '仿宋'
        font_data_16pt_left.height = 320  # 16pt
        font_data_16pt_left.bold = True
        style_data_16pt_left.font = font_data_16pt_left
        style_data_16pt_left.alignment = alignment_data  # 左对齐
        
        # 装炉顺列右侧实线边框样式（12pt）'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加 style_data_16pt_left 样式定义")
