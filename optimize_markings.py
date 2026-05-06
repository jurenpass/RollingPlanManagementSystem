# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 去除回字填充标记的重置
old_text1 = '''            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False
            row_data["回字填充"] = False  # 除鳞字段回字填充标记'''

new_text1 = '''            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False'''

content = content.replace(old_text1, new_text1)

# 2. 去除回字填充的检查逻辑
old_text2 = '''            # 检查除鳞字段，如果是"回"字则标记回字填充
            if "层号" in row_data:
                除鳞值 = str(row_data.get("层号", "")).strip()
                if 除鳞值 == "回":
                    row_data["回字填充"] = True
                    row_data["需标注"] = True  # 除鳞为回字时也需要标注钢卷号
            
            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:'''

new_text2 = '''            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:'''

content = content.replace(old_text2, new_text2)

# 3. 修改除鳞字段写入逻辑 - 检查是否包含"回"字，如果是则标注钢卷号
old_text3 = '''                elif col_name == "层号":
                    # 除鳞字段回字填充
                    if row_data.get("回字填充", False):
                        value = "回"  # 回字填充
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

new_text3 = '''                elif col_name == "层号":
                    # 检查除鳞字段是否包含"回"字，如果是则标注对应钢卷号
                    if value and "回" in str(value):
                        row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

content = content.replace(old_text3, new_text3)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已优化标记逻辑：去除重复，修正除鳞标记逻辑")
