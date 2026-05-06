# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改坯厚字段的写入逻辑，添加三角符号标记
old_text1 = '''                elif col_name == "坯厚":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)'''

new_text1 = '''                elif col_name == "坯厚":
                    # 检查坯厚是否>230，如果是则添加三角符号
                    坯厚需标注 = False
                    if "坯厚" in row_data:
                        坯厚值 = row_data.get("坯厚", 0)
                        try:
                            坯厚数值 = float(坯厚值) if 坯厚值 != "" else 0
                            if 坯厚数值 > 230:
                                坯厚需标注 = True
                        except (ValueError, TypeError):
                            pass
                    if 坯厚需标注 and value:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)'''

content = content.replace(old_text1, new_text1)

# 2. 修改除鳞字段的写入逻辑，在包含"回"字时添加回字标注
old_text2 = '''                elif col_name == "层号":
                    # 检查除鳞字段是否包含"回"字，如果是则标注对应钢卷号
                    if value and "回" in str(value):
                        row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

new_text2 = '''                elif col_name == "层号":
                    # 检查除鳞字段是否包含"回"字，如果是则标注回字并标注对应钢卷号
                    if value and "回" in str(value):
                        row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
                        # 如果除鳞字段不是以"回"开头，则在前面添加"回"字
                        if not str(value).startswith("回"):
                            value = "回" + str(value)
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

content = content.replace(old_text2, new_text2)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加坯厚和除鳞字段的标注")
