# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复中文逗号
old_text = '''                        # 检查头部宽度和尾部宽度中的小者是否 <= 轧宽
                        较小宽度 = min(板坯头部宽度值，板坯尾部宽度值)
                        if 较小宽度 <= 轧宽值：
                            row_data["调宽向上标记"] = True  # 调宽字段标注↑
                            row_data["轧宽需标注"] = True    # 轧宽字段标注Δ
                            row_data["需标注"] = True        # 钢卷号标注Δ'''

new_text = '''                        # 检查头部宽度和尾部宽度中的小者是否 <= 轧宽
                        较小宽度 = min(板坯头部宽度值，板坯尾部宽度值)
                        if 较小宽度 <= 轧宽值:
                            row_data["调宽向上标记"] = True  # 调宽字段标注↑
                            row_data["轧宽需标注"] = True    # 轧宽字段标注Δ
                            row_data["需标注"] = True        # 钢卷号标注Δ'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修复中文逗号")
