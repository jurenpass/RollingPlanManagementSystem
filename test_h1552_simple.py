import sys
import os
import xlrd
import xlwt
import pandas as pd

# 测试读取和处理H1552.xls文件
file_path = r'g:\newplan\计划号\H1552.xls'

try:
    # 读取文件
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    
    # 获取列名
    current_columns = []
    for i in range(sheet.ncols):
        current_columns.append(sheet.cell_value(0, i))
    
    print("H1552.xls 的列名:")
    for i, col in enumerate(current_columns):
        print(f"  {i}: '{col}'")
    
    # 检查关键列
    key_columns = ["顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）", "装炉顺序号", "轧宽"]
    print("\n关键列检查:")
    for col in key_columns:
        if col in current_columns:
            print(f"  ✅ {col} - 存在")
        else:
            print(f"  ❌ {col} - 缺失")
    
    # 测试数据处理
    print("\n测试数据行处理:")
    for row_idx in range(1, min(3, sheet.nrows)):
        row_data = {}
        for col_idx, col_name in enumerate(current_columns):
            row_data[col_name] = sheet.cell_value(row_idx, col_idx)
        
        # 测试填充缺失字段
        if "钢卷号" in row_data:
            钢卷号值 = row_data["钢卷号"]
            print(f"  行{row_idx}: 钢卷号={钢卷号值}")
        
        # 测试处理轧宽+（余量）
        if "轧宽+（余量）" not in row_data or row_data.get("轧宽+（余量）") is None or pd.isna(row_data.get("轧宽+（余量）")):
            if "轧宽" in row_data:
                row_data["轧宽+（余量）"] = row_data["轧宽"]
                print(f"    使用轧宽作为轧宽+（余量）: {row_data['轧宽']}")
        
        # 测试处理装炉顺序号
        if "装炉顺序号" not in row_data or row_data.get("装炉顺序号") is None or pd.isna(row_data.get("装炉顺序号")):
            if "顺序号" in row_data:
                row_data["装炉顺序号"] = row_data["顺序号"]
                print(f"    使用顺序号作为装炉顺序号: {row_data['顺序号']}")
    
    # 释放资源
    if hasattr(workbook, 'release_resources'):
        workbook.release_resources()
    
    print("\n✓ 测试成功！H1552.xls 可以正常处理")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
