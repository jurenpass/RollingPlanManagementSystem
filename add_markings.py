# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加回字填充标记
old_text = '''            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False'''

new_text = '''            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False
            row_data["回字填充"] = False  # 除鳞字段回字填充标记'''

content = content.replace(old_text, new_text)

# 添加除鳞回字检查
old_text2 = '''            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:'''

new_text2 = '''            # 检查除鳞字段，如果是"回"字则标记回字填充
            if "层号" in row_data:
                除鳞值 = str(row_data.get("层号", "")).strip()
                if 除鳞值 == "回":
                    row_data["回字填充"] = True
                    row_data["需标注"] = True  # 除鳞为回字时也需要标注钢卷号
            
            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:'''

content = content.replace(old_text2, new_text2)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加回字填充标记逻辑")
