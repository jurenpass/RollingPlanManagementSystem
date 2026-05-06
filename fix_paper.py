# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换纸张设置
old_text = """        # 设置页面属性
        # 设置纸张大小为美国 Fanfold (标准值为 39)
        # 注意：xlwt 的 paper_size 值对应 Excel 的纸张类型枚举
        # 39 = xlPaperFanfoldUS (14.875 x 11 inches)
        new_sheet.paper_size = 39"""

new_text = """        # 设置页面属性
        # 设置纸张大小为美国 Fanfold (137 = xlPaperFanfoldUS, 14.875 x 11 inches)
        # 注意：xlwt 的 paper_size 值对应 Excel 的纸张类型枚举
        # 137 = xlPaperFanfoldUS (14.875 x 11 inches) - 连续折叠纸
        # 39 = xlPaperFanfoldStandard (14.875 x 11 inches) - 备选
        new_sheet.paper_size = 137"""

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("纸张设置已更新为 137 (FanfoldUS)")
