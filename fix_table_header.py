# -*- coding: utf-8 -*-
"""
精确替换 furnace_order_manager_pyqt5.py 中的表头布局代码
"""

# 读取文件
with open('g:\\newplan\\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 要替换的旧代码（精确匹配，共 15 行，从第 1691 行到第 1705 行）
# 第 1691 行：# 第二行：计划号和块数
# 第 1692 行：计划号块数信息 = f"计划号：{计划号} | 块数：{块数}"
# 第 1693 行：new_sheet.write(1, 0, 计划号块数信息，style_header_info)
# 第 1694 行：（空行）
# 第 1695 行：# 第二行：提示信息（如果有）
# 第 1696 行：if 提示信息列表:
# 第 1697 行：提示信息 = "；".join(提示信息列表)
# 第 1698 行：new_sheet.write(2, 0, f"提示：{提示信息}", style_header_info)
# 第 1699 行：（空行）
# 第 1700 行：# 写入字段列名
# 第 1701 行：header_row = 3
# 第 1702 行：if 提示信息列表:
# 第 1703 行：header_row = 4
# 第 1704 行：（空行）
# 第 1705 行：for col_idx, col_name in enumerate(target_columns):

# 检查是否匹配
start_index = 1690  # 第 1691 行（索引从 0 开始）
expected_lines = [
    '        # 第二行：计划号和块数\n',
    '        计划号块数信息 = f"计划号:{计划号} | 块数:{块数}"\n',
    '        # 此行已在新代码中移除\n',
    '        \n',
    '        # 第二行：提示信息（如果有）\n',
    '        if 提示信息列表:\n',
    '            提示信息 = "；".join(提示信息列表)\n',
    '            new_sheet.write(2, 0, f"提示:{提示信息}", style_header_info)\n',
    '        \n',
    '        # 写入字段列名\n',
    '        header_row = 3\n',
    '        if 提示信息列表:\n',
    '            header_row = 4\n',
    '        \n',
    '        for col_idx, col_name in enumerate(target_columns):\n',
]

# 验证是否匹配
match = True
for i, expected in enumerate(expected_lines):
    actual = lines[start_index + i]
    if actual != expected:
        print(f"第 {i} 行不匹配:")
        print(f"  期望：{repr(expected)}")
        print(f"  实际：{repr(actual)}")
        match = False

if match:
    print("验证通过，开始替换...")
    
    # 新代码
    new_code = '''        # 计算提示信息行数（先左右再上下，每行显示 2 条）
        if len(提示信息列表) == 0:
            提示信息行数 = 1  # 至少有一行（空行）
        else:
            提示信息行数 = (len(提示信息列表) + 1) // 2  # 向上取整，每行 2 条
        
        # 字段列名行号 = 提示信息起始行 (1) + 提示信息行数
        字段列名行号 = 1 + 提示信息行数
        
        # 找到各列的索引
        轧宽列索引 = -1
        订宽列索引 = -1
        除鳞列索引 = -1
        强度列索引 = -1
        粗轧报信列索引 = -1
        装炉顺列索引 = -1
        牌号列索引 = -1
        公差带列索引 = -1
        序号列索引 = 0  # 假设序号是第一列
        钢卷号列索引 = 1  # 假设钢卷号是第二列
        
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "轧宽":
                轧宽列索引 = col_idx
            elif 映射后的列名 == "订宽":
                订宽列索引 = col_idx
            elif 映射后的列名 == "除鳞":
                除鳞列索引 = col_idx
            elif 映射后的列名 == "强度":
                强度列索引 = col_idx
            elif 映射后的列名 == "粗轧报信":
                粗轧报信列索引 = col_idx
            elif 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
            elif 映射后的列名 == "牌号（钢级）":
                牌号列索引 = col_idx
            elif 映射后的列名 == "公差带":
                公差带列索引 = col_idx
        
        # 找到需要的列索引
        坯宽列索引 = -1
        轧厚列索引 = -1
        坯长列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "坯宽":
                坯宽列索引 = col_idx
            elif 映射后的列名 == "轧厚":
                轧厚列索引 = col_idx
            elif 映射后的列名 == "坯长":
                坯长列索引 = col_idx
        
        # 计算左区域（坯宽到公差带）
        if 坯宽列索引 >= 0 and 公差带列索引 >= 0:
            左区域起始 = 坯宽列索引
            左区域结束 = 公差带列索引
        else:
            左区域起始 = -1
            左区域结束 = -1
        
        # 计算中间区域（粗轧报信到坯长）
        if 粗轧报信列索引 >= 0 and 坯长列索引 >= 0:
            中间区域起始 = 粗轧报信列索引
            中间区域结束 = 坯长列索引
        else:
            中间区域起始 = -1
            中间区域结束 = -1
        
        # 计算右区域（轧厚到装炉顺）
        if 轧厚列索引 >= 0 and 装炉顺列索引 >= 0:
            右区域起始 = 轧厚列索引
            右区域结束 = 装炉顺列索引
        else:
            右区域起始 = -1
            右区域结束 = -1
        
        # 第二行及以下：计划号、块数、提示信息、打印时间
        # 序号和钢卷号列合并，填充计划号信息
        new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 序号列索引，钢卷号列索引，f"计划号：{计划号}", style_header_info)
        
        # 牌号（钢级）列填充块数信息
        if 牌号列索引 >= 0:
            new_sheet.write(字段列名行号 - 1, 牌号列索引，f"块数：{块数} 块", style_header_info)
        
        # 显示提示信息
        if 左区域起始 >= 0 and 左区域结束 >= 0 and 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 计算需要的行数（每行显示 2 条提示信息）
            提示信息总行数 = (len(提示信息列表) + 1) // 2  # 向上取整
            for i in range(提示信息总行数):
                # 左列（坯宽到公差带）：显示第 i*2 条提示信息
                左列索引 = i * 2
                if 左列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始，左区域结束，提示信息列表 [左列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始，左区域结束，"", style_header_info)
                
                # 中间列（粗轧报信到坯长）：显示第 i*2+1 条提示信息
                中间列索引 = i * 2 + 1
                if 中间列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始，中间区域结束，提示信息列表 [中间列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始，中间区域结束，"", style_header_info)
        elif 左区域起始 >= 0 and 左区域结束 >= 0:
            # 如果只有左区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 左区域起始，左区域结束，提示信息，style_header_info)
        elif 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 如果只有中间区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 中间区域起始，中间区域结束，提示信息，style_header_info)
        
        # 右区域（中厚到装炉顺）显示打印时间
        if 右区域起始 >= 0 and 右区域结束 >= 0:
            new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 右区域起始，右区域结束，f"打印时间：{当前时间}", style_time)
        
        # 设置行高（25pt = 500 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 500
            new_sheet.row(i).height_mismatch = True
        
        # 字段列名（使用内外边框线样式）
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            new_sheet.write(字段列名行号，col_idx, 映射后的列名，style_header_border)
        
        # 设置字段列名行的行高（25pt = 500 twips）
        new_sheet.row(字段列名行号).height = 500
        new_sheet.row(字段列名行号).height_mismatch = True
        
'''
    
    # 替换
    new_lines = lines[:start_index] + [new_code] + lines[start_index + len(expected_lines):]
    
    # 写回文件
    with open('g:\\newplan\\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"成功替换！共删除了 {len(expected_lines)} 行，替换为新的表头布局代码")
else:
    print("验证失败，未执行替换")
