# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 在第 1659 行后添加一行
new_lines = []
for i, line in enumerate(lines, 1):
    new_lines.append(line)
    if i == 1659:  # 在无 APS 钢种数 += 1 这行之后
        # 检查这一行是否是我们找的那一行
        if '无 APS 钢种数 += 1' in line:
            # 添加存储无 APS 钢种标志的代码
            new_lines.append('            row_data["是无 APS 钢种"] = 是无 APS 钢种\n')

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("已添加无 APS 钢种标记存储")
