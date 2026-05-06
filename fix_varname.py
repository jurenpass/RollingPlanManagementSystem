# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复牌号（钢级）的写入逻辑
old_text = '''                elif col_name == "牌号（钢级）":
                    # 无 APS 钢种时添加Δ标记
                    是无 APS 钢种 = row_data.get("是无 APS 钢种", False)
                    需标注 = row_data.get("需标注", False)
                    if 需标注 and 是无 APS 钢种:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_left)'''

new_text = '''                elif col_name == "牌号（钢级）":
                    # 无 APS 钢种时添加Δ标记
                    is_no_aps = row_data.get("是无 APS 钢种", False)
                    需标注 = row_data.get("需标注", False)
                    if 需标注 and is_no_aps:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_left)'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修复变量名")
