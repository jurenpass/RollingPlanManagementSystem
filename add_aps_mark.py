# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在检查牌号逻辑中添加无 APS 钢种标记
old_text = '''            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无 APS 块数 += 1
                    row_data["需标注"] = True
                    包含无 APS = True
                    if brand not in 已添加无 APS 的钢种:
                        已添加无 APS 的钢种.add(brand)
                        无 APS 钢种数 += 1'''

new_text = '''            # 检查牌号是否在 APS 列表中，如果不在则标记需标注
            是无 APS 钢种 = False
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无 APS 块数 += 1
                    row_data["需标注"] = True
                    是无 APS 钢种 = True
                    包含无 APS = True
                    if brand not in 已添加无 APS 的钢种:
                        已添加无 APS 的钢种.add(brand)
                        无 APS 钢种数 += 1
            row_data["是无 APS 钢种"] = 是无 APS 钢种'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加无 APS 钢种标记")
