#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要删除的行范围（第5649-5679行）
# 使用0-based索引，所以是第5648-5678行
start_line = 5648
end_line = 5678

# 检查这段代码是否包含 go_to_furnace_details 嵌套函数定义
found_nested_func = False
for i in range(start_line, min(end_line + 1, len(lines))):
    if 'def go_to_furnace_details():' in lines[i] and i > 1000:  # 排除类方法定义
        found_nested_func = True
        print(f"找到第{i+1}行的嵌套函数定义")
        break

if found_nested_func:
    # 删除这段代码
    new_lines = lines[:start_line] + lines[end_line + 1:]

    with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"成功删除第{start_line+1}-{end_line+1}行的重复代码")
else:
    print("未找到嵌套函数定义，可能已经被删除")
