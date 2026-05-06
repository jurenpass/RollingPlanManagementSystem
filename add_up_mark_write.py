# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改调宽标记字段的写入逻辑
old_text = '''                elif col_name == "板坯宽度调宽标记":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)'''

new_text = '''                elif col_name == "板坯宽度调宽标记":
                    # 调宽向上标记时添加↑符号
                    if row_data.get("调宽向上标记", False):
                        if value:
                            try:
                                调宽数值 = float(value)
                                value = str(int(调宽数值)) + "↑"
                            except (ValueError, TypeError):
                                value = str(value) + "↑"
                        else:
                            value = "↑"
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修改调宽标记字段写入逻辑")
