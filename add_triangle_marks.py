# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改钢卷号写入逻辑，添加三角符号
old_text = '''                # 根据字段名选择不同的样式
                if col_name == "钢卷号":
                    new_sheet.write(row_idx, col_idx, value, style_data_16pt_left_border)'''

new_text = '''                # 根据字段名选择不同的样式
                if col_name == "钢卷号":
                    # 检查是否需要标注三角符号
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_16pt_left_border)'''

content = content.replace(old_text, new_text)

# 修改减宽量写入逻辑，添加三角符号
old_text2 = '''                elif col_name == "侧压量":
                    if row_data.get("减宽超标", False):
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)'''

new_text2 = '''                elif col_name == "侧压量":
                    # 减宽超标时添加三角符号
                    if row_data.get("减宽超标", False):
                        if value:
                            try:
                                减宽数值 = float(value)
                                value = str(int(减宽数值)) + "Δ"
                            except (ValueError, TypeError):
                                value = str(value) + "Δ"
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)'''

content = content.replace(old_text2, new_text2)

# 修改除鳞写入逻辑，添加回字填充
old_text3 = '''                elif col_name == "层号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

new_text3 = '''                elif col_name == "层号":
                    # 除鳞字段回字填充
                    if row_data.get("回字填充", False):
                        value = "回"  # 回字填充
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

content = content.replace(old_text3, new_text3)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加三角符号和回字填充标记到写入逻辑")
