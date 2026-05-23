import re

# 读取文件
with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 print_furnace_details 方法的起始位置
pattern = r'    def print_furnace_details\(self, is_incremental=False\):'
match = re.search(pattern, content)
if not match:
    print("未找到 print_furnace_details 方法")
    exit(1)

method_start = match.start()
print(f"找到 print_furnace_details 方法在位置 {method_start}")

# 查找下一个方法的起始位置（通过缩进判断）
# 查找 "    def " 在方法之前的最后一个
prev_def_pattern = r'    def \w+\(self[^)]*\):'
prev_matches = list(re.finditer(prev_def_pattern, content[:method_start]))
if prev_matches:
    prev_method_start = prev_matches[-1].start()
    print(f"前一个方法在位置 {prev_method_start}")
else:
    print("未找到前一个方法")
    exit(1)

# 提取方法代码（从前一个方法结束到下一个方法开始）
method_code = content[prev_method_start:method_start]

# 查找 FurnaceDetailsWindow 类中 print_btn_clicked 的位置
furnace_class_match = re.search(r'class FurnaceDetailsWindow', content)
if not furnace_class_match:
    print("未找到 FurnaceDetailsWindow 类")
    exit(1)

furnace_class_start = furnace_class_match.start()
print(f"FurnaceDetailsWindow 类在位置 {furnace_class_start}")

# 在 FurnaceDetailsWindow 类中找到 print_btn_clicked 的位置
print_btn_pattern = r'        def print_btn_clicked\(self\):'
print_btn_match = re.search(print_btn_pattern, content[furnace_class_start:])
if not print_btn_match:
    print("未找到 print_btn_clicked 方法")
    exit(1)

print_btn_position = furnace_class_start + print_btn_match.start()
print(f"print_btn_clicked 在位置 {print_btn_position}")

# 找到 print_btn_clicked 方法的结束位置（下一个同级或更高级的方法）
# 查找 "        def " 或 "    def " 在 print_btn_clicked 之后
next_def_pattern = r'\n    def |\n        def '
next_matches = list(re.finditer(next_def_pattern, content[print_btn_position + 10:]))
if next_matches:
    next_def_position = print_btn_position + 10 + next_matches[0].start()
    print(f"下一个方法在位置 {next_def_position}")
else:
    print("未找到下一个方法")
    exit(1)

# 提取 print_btn_clicked 的代码
print_btn_code = content[print_btn_position:next_def_position]
print(f"print_btn_clicked 代码长度: {len(print_btn_code)}")

# 删除 MainWindow 类中的 print_furnace_details 方法
new_content = content[:prev_method_start] + content[method_start:]

# 在 FurnaceDetailsWindow 类中的 print_btn_clicked 之前插入 print_furnace_details 方法
new_content = new_content[:print_btn_position] + '\n\n' + method_code.strip() + '\n\n' + new_content[print_btn_position:]

# 写入文件
with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("文件已更新！")
