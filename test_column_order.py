import xlrd
import xlwt
import pandas as pd
import os

# 测试不同列顺序的文件处理
def test_process_file(file_path, description):
    print(f"\n{'='*100}")
    print(f"测试文件: {description}")
    print(f"文件路径: {file_path}")
    print('='*100)
    
    try:
        # 读取文件
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        
        # 获取列名
        current_columns = []
        for i in range(sheet.ncols):
            current_columns.append(sheet.cell_value(0, i))
        
        print(f"列数: {len(current_columns)}")
        
        # 测试关键列是否存在
        key_cols = ["顺序号", "钢卷号", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽"]
        print("\n关键列检查:")
        for col in key_cols:
            if col in current_columns:
                print(f"  ✅ {col} - 位置: {current_columns.index(col)}")
            else:
                print(f"  ❌ {col} - 缺失")
        
        # 测试数据处理
        print("\n数据处理测试:")
        row_data = {}
        for col_idx, col_name in enumerate(current_columns):
            row_data[col_name] = sheet.cell_value(1, col_idx)
        
        print(f"  钢卷号: {row_data.get('钢卷号', 'N/A')}")
        print(f"  坯宽: {row_data.get('坯宽', 'N/A')}")
        print(f"  轧宽: {row_data.get('轧宽', 'N/A')}")
        
        # 测试填充缺失字段
        if "轧宽+（余量）" not in row_data or row_data.get("轧宽+（余量）") is None or pd.isna(row_data.get("轧宽+（余量）")):
            if "轧宽" in row_data:
                row_data["轧宽+（余量）"] = row_data["轧宽"]
                print(f"  ✅ 使用轧宽作为轧宽+（余量）: {row_data['轧宽']}")
        
        if "装炉顺序号" not in row_data or row_data.get("装炉顺序号") is None or pd.isna(row_data.get("装炉顺序号")):
            if "顺序号" in row_data:
                row_data["装炉顺序号"] = row_data["顺序号"]
                print(f"  ✅ 使用顺序号作为装炉顺序号: {row_data['顺序号']}")
        
        # 释放资源
        if hasattr(workbook, 'release_resources'):
            workbook.release_resources()
        
        print("\n✓ 测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# 测试H5179.xls（已知能正常处理）
test_process_file(r'g:\newplan\计划号\H5179.xls', "H5179.xls (已知能正常处理)")

# 测试H1552.xls（处理失败）
test_process_file(r'g:\newplan\计划号\H1552.xls', "H1552.xls (处理失败)")
