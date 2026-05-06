import re

# 读取文件内容
with open('furnace_order_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除主界面中的防止退出登录复选框代码
content = re.sub(r'# 防退出登录选项[\s\S]*?self\.anti_logout_checkbox\.pack\(side=tk\.RIGHT, padx=10\)\n', '', content)

# 删除与防止退出登录相关的方法
content = re.sub(r'def on_anti_logout_toggle\(self\):[\s\S]*?def on_auto_exec_toggle\(self\):', 'def on_auto_exec_toggle(self):', content)

# 删除设置页面中的防止退出登录时间间隔设置代码
content = re.sub(r'# 防止退出登录时间间隔设置[\s\S]*?ttk\.Label\(anti_logout_frame, text="\(30-999\)", foreground="gray", font=\(\'微软雅黑\', 9\)\)\.pack\(side=tk\.LEFT, padx=5\)\n', '', content)

# 写入修改后的内容
with open('furnace_order_manager.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已成功删除防止退出登录相关的设置及代码")
