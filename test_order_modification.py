import xlrd
import xlwt
import os

# 模拟一下我们的修改逻辑
plan_dir = r"g:\newplan\计划号"
zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
h5178_file = os.path.join(plan_dir, "H5178.xls")

print("=" * 80)
print("测试修改逻辑")
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
    
    # 查找列名行
    current_columns = []
    for i in range(sheet.ncols):
        current_columns.append(sheet.cell_value(0, i))
    
    # 收集数据
    for row_idx in range(1, sheet.nrows):
        row_data = {}
        for col_idx, col_name in enumerate(current_columns):
            row_data[col_name] = sheet.cell_value(row_idx, col_idx)
        
        # 填充装炉顺
        if "钢卷号" in row_data:
            钢卷号值 = row_data["钢卷号"]
            if 钢卷号值:
                钢卷号字符串 = str(钢卷号值)
                if 钢卷号字符串 in 装炉顺序映射:
                    原装炉顺序号 = 装炉顺序映射[钢卷号字符串]["原装炉顺序号"]
                    row_data["装炉顺序号"] = 原装炉顺序号
                    row_data["装炉顺"] = 装炉顺序映射[钢卷号字符串]["装炉顺"]
        
        all_row_data.append(row_data)
    
    workbook.release_resources()

print(f"\n原始H5178数据（前5条）:")
for i, row_data in enumerate(all_row_data[:5]):
    print(f"{i+1}. 钢卷号: {row_data.get('钢卷号', 'N/A')}, 装炉顺: {row_data.get('装炉顺', 'N/A')}")

# 3. 应用我们的修改逻辑
print(f"\n\n应用修改逻辑...")

# 首先过滤掉没有装炉顺序号的数据
valid_row_data = []
for row_data in all_row_data:
    if "装炉顺" in row_data and row_data["装炉顺"] is not None and row_data["装炉顺"] != "":
        valid_row_data.append(row_data)

# 按照装炉顺排序
valid_row_data.sort(key=lambda x: x["装炉顺"])

# 为排序后的数据设置序号（从1开始）
for idx, row_data in enumerate(valid_row_data):
    row_data["顺序号"] = idx + 1

# 更新all_row_data为排序后的数据
all_row_data = valid_row_data

print(f"\n修改后的H5178数据（全部）:")
print(f"{'序号':<6} {'钢卷号':<15} {'装炉顺':<10}")
print("-" * 40)
for i, row_data in enumerate(all_row_data):
    print(f"{row_data.get('顺序号', i+1):<6} {row_data.get('钢卷号', 'N/A'):<15} {row_data.get('装炉顺', 'N/A'):<10}")

print(f"\n\n总结:")
print(f"原始数据条数: {len(all_row_data)}")
print(f"有效数据条数: {len(valid_row_data)}")
print(f"已按照装炉顺排序，并设置了序号！")