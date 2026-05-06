import xlrd
import xlwt
import os

# 模拟一下我们的修改逻辑
plan_dir = r"g:\newplan\计划号"
zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
h5178_file = os.path.join(plan_dir, "H5178.xls")

print("=" * 80)
print("测试修改逻辑 - 保持原始顺序，序号=装炉顺")
print("=" * 80)

# 1. 读取装炉顺序文件，构建钢卷号到装炉顺序号的映射
装炉顺序映射 = {}
if os.path.exists(zhuanglu_file):
    workbook = xlrd.open_workbook(zhuanglu_file)
    sheet = workbook.sheet_by_index(0)
    
    headers = []
    for col_idx in range(sheet.ncols):
        headers.append(sheet.cell_value(0, col_idx))
    
    装炉钢卷号列 = headers.index("钢卷号") if "钢卷号" in headers else -1
    装炉顺序号列 = headers.index("装炉顺序号") if "装炉顺序号" in headers else -1
    
    if 装炉钢卷号列 != -1:
        for row_idx in range(1, sheet.nrows):
            钢卷号 = sheet.cell_value(row_idx, 装炉钢卷号列)
            if 钢卷号:
                钢卷号字符串 = str(钢卷号)
                原装炉顺序号 = None
                
                if 装炉顺序号列 != -1:
                    try:
                        原装炉顺序号 = int(sheet.cell_value(row_idx, 装炉顺序号列))
                    except (ValueError, TypeError):
                        原装炉顺序号 = 0
                
                装炉顺序映射[钢卷号字符串] = {
                    "原装炉顺序号": 原装炉顺序号,
                    "装炉顺": 原装炉顺序号
                }
    workbook.release_resources()

# 2. 读取H5178文件
all_row_data = []
if os.path.exists(h5178_file):
    workbook = xlrd.open_workbook(h5178_file)
    sheet = workbook.sheet_by_index(0)
    
    # 查找列名行（查找包含"序号"和"钢卷号"的行）
    字段列名行号 = -1
    for i in range(min(10, sheet.nrows)):
        row_values = []
        for j in range(sheet.ncols):
            cell_value = str(sheet.cell_value(i, j)).strip()
            row_values.append(cell_value)
        has_coil_col = any('钢卷号' in v for v in row_values)
        has_seq_col = any('序号' in v for v in row_values)
        if has_coil_col and has_seq_col:
            字段列名行号 = i
            print(f"找到列名行: 第 {i+1} 行")
            break
    
    if 字段列名行号 == -1:
        print("未找到列名行！")
    else:
        # 读取列名
        current_columns = []
        for j in range(sheet.ncols):
            current_columns.append(str(sheet.cell_value(字段列名行号, j)).strip())
        
        # 收集数据（从列名行的下一行开始）
        for row_idx in range(字段列名行号 + 1, sheet.nrows):
            row_data = {}
            for col_idx, col_name in enumerate(current_columns):
                if col_idx < sheet.ncols:
                    row_data[col_name] = sheet.cell_value(row_idx, col_idx)
            
            # 填充装炉顺
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                if 钢卷号值:
                    钢卷号字符串 = str(钢卷号值)
                    # 清理钢卷号字符串（去掉Δ等特殊字符）
                    钢卷号字符串_clean = 钢卷号字符串.replace('Δ', '').strip()
                    if 钢卷号字符串_clean in 装炉顺序映射:
                        原装炉顺序号 = 装炉顺序映射[钢卷号字符串_clean]["原装炉顺序号"]
                        row_data["装炉顺序号"] = 原装炉顺序号
                        row_data["装炉顺"] = 装炉顺序映射[钢卷号字符串_clean]["装炉顺"]
                    elif 钢卷号字符串 in 装炉顺序映射:
                        原装炉顺序号 = 装炉顺序映射[钢卷号字符串]["原装炉顺序号"]
                        row_data["装炉顺序号"] = 原装炉顺序号
                        row_data["装炉顺"] = 装炉顺序映射[钢卷号字符串]["装炉顺"]
            
            # 只添加有钢卷号的数据
            if row_data.get("钢卷号"):
                all_row_data.append(row_data)
    
    workbook.release_resources()

print(f"\n原始H5178数据（前10条）:")
print(f"{'原始序号':<10} {'钢卷号':<15} {'装炉顺':<10}")
print("-" * 40)
for i, row_data in enumerate(all_row_data[:10]):
    print(f"{row_data.get('序号', i+1):<10} {row_data.get('钢卷号', 'N/A'):<15} {row_data.get('装炉顺', 'N/A'):<10}")

# 3. 应用我们的修改逻辑
print(f"\n\n应用修改逻辑...")

# 为每条数据设置序号为装炉顺（保持原始顺序不变）
for row_data in all_row_data:
    if "装炉顺" in row_data and row_data["装炉顺"] is not None and row_data["装炉顺"] != "":
        row_data["顺序号"] = row_data["装炉顺"]

print(f"\n修改后的H5178数据（前10条）:")
print(f"{'新序号':<10} {'钢卷号':<15} {'装炉顺':<10}")
print("-" * 40)
for i, row_data in enumerate(all_row_data[:10]):
    print(f"{row_data.get('顺序号', i+1):<10} {row_data.get('钢卷号', 'N/A'):<15} {row_data.get('装炉顺', 'N/A'):<10}")

print(f"\n\n总结:")
print(f"数据条数: {len(all_row_data)}")
print(f"已保持原始顺序，序号字段值已设置为装炉顺！")