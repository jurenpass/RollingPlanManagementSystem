# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在轧宽 +（余量）之前添加轧宽字段的处理
old_text = '''                elif col_name == "轧宽 +（余量）":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)'''

new_text = '''                elif col_name == "轧宽":
                    # 轧宽需标注时添加Δ标记
                    if row_data.get("轧宽需标注", False):
                        if value:
                            try:
                                轧宽数值 = float(value)
                                value = str(int(轧宽数值)) + "Δ"
                            except (ValueError, TypeError):
                                value = str(value) + "Δ"
                        else:
                            value = "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)
                elif col_name == "轧宽 +（余量）":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加轧宽字段处理逻辑")
