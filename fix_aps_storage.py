# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加无 APS 钢种标记存储
old_text = '''                    if brand not in 已添加无 APS 的钢种:
                        已添加无 APS 的钢种.add(brand)
                        无 APS 钢种数 += 1
            
            # 处理调宽字段 - 如果调宽为"1"，则进行特殊处理'''

new_text = '''                    if brand not in 已添加无 APS 的钢种:
                        已添加无 APS 的钢种.add(brand)
                        无 APS 钢种数 += 1
            row_data["是无 APS 钢种"] = 是无 APS 钢种
            
            # 处理调宽字段 - 如果调宽为"1"，则进行特殊处理'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加无 APS 钢种标记存储")
