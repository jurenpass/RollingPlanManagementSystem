# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加新的判断逻辑
old_text = '''                    减宽新值 = 坯宽新值 - 轧宽值
                    if 减宽新值 >= 240:
                        减宽超标块数 += 1
                        row_data["减宽超标"] = True
                        row_data["需标注"] = True
                    elif 减宽新值 < 0:
                        逆宽轧制板坯数 += 1
                        row_data["减宽超标"] = True
                        row_data["需标注"] = True
                    row_data["侧压量"] = 减宽新值'''

new_text = '''                    减宽新值 = 坯宽新值 - 轧宽值
                    if 减宽新值 >= 240:
                        减宽超标块数 += 1
                        row_data["减宽超标"] = True
                        row_data["需标注"] = True
                    elif 减宽新值 < 0:
                        逆宽轧制板坯数 += 1
                        row_data["减宽超标"] = True
                        row_data["需标注"] = True
                    row_data["侧压量"] = 减宽新值
                    
                    # 检查头部宽度和尾部宽度中的小者是否 <= 轧宽
                    较小宽度 = min(板坯头部宽度值，板坯尾部宽度值)
                    if 较小宽度 <= 轧宽值：
                        row_data["调宽向上标记"] = True  # 调宽字段标注↑
                        row_data["轧宽需标注"] = True    # 轧宽字段标注Δ
                        row_data["需标注"] = True        # 钢卷号标注Δ'''

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已添加调宽向上标记判断逻辑")
