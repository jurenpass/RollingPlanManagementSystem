#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改第1处：进入装炉明细画面
content = content.replace('print("30秒后刷新装炉明细窗口数据...")', 'print("10秒后刷新装炉明细窗口数据...")')
content = content.replace('# 延迟30秒执行', '# 延迟10秒执行')
content = content.replace('time.sleep(30)', 'time.sleep(10)')

# 修改第2处：QTimer.singleShot(30000, go_to_furnace_details)
content = content.replace('QTimer.singleShot(30000, go_to_furnace_details)', 'QTimer.singleShot(10000, go_to_furnace_details)')

# 修改第3处：注释中的30秒
content = content.replace('# 定义30秒后进入装炉明细画面的函数', '# 定义10秒后进入装炉明细画面的函数')
content = content.replace('# 30秒后进入装炉明细画面', '# 10秒后进入装炉明细画面')
content = content.replace('print("30秒延时后进入装炉明细画面")', 'print("10秒延时后进入装炉明细画面")')
content = content.replace('# 设置30秒后进入装炉明细画面', '# 设置10秒后进入装炉明细画面')

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
