# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 在设置除鳞字段后，检查是否有"回"字，如果有则设置需标注
old_text1 = '''                # 最后设置除鳞字段的值
                row_data["层号"] = 除鳞值
            
            # 3. 添加标记逻辑
            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False'''

new_text1 = '''                # 最后设置除鳞字段的值
                row_data["层号"] = 除鳞值
            
            # 3. 添加标记逻辑
            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False
            
            # 检查除鳞字段是否包含"回"字，如果是则标记需标注
            if "层号" in row_data:
                除鳞值 = str(row_data.get("层号", "")).strip()
                if 除鳞值 and "回" in 除鳞值:
                    row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号'''

content = content.replace(old_text1, new_text1)

# 2. 删除写入阶段对"回"字的检查（因为已经在数据处理阶段检查过了）
old_text2 = '''                elif col_name == "层号":
                    # 检查除鳞字段是否包含"回"字，如果是则标注对应钢卷号
                    if value and "回" in str(value):
                        row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

new_text2 = '''                elif col_name == "层号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)'''

content = content.replace(old_text2, new_text2)

# 3. 修改钢卷号样式为左对齐
old_text3 = '''                if col_name == "钢卷号":
                    # 检查是否需要标注三角符号
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_16pt_left_border)'''

new_text3 = '''                if col_name == "钢卷号":
                    # 检查是否需要标注三角符号
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_16pt_left)'''

content = content.replace(old_text3, new_text3)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修复：1.在数据处理阶段检查回字 2.钢卷号改为左对齐")
