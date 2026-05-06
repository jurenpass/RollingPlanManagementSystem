import xlrd

# 测试钢卷号匹配（修改后）
file_path = r"g:\newplan\计划号\H5178.xls"
workbook = xlrd.open_workbook(file_path)
sheet = workbook.sheet_by_index(0)

# 从装炉顺序.xls中读取的钢卷号（已清理，只保留数字）
test_coil_nos = ['62019537', '62019538', '62019539']

print("检查钢卷号匹配（修改后，只保留数字）:\n")

# 查找列名行
header_row = 2  # 已知第3行是列名行

# 查找钢卷号列
coil_col = 1  # 已知第2列是钢卷号列

for test_coil in test_coil_nos:
    print(f"查找钢卷号: {test_coil}")
    found = False
    for row in range(header_row + 1, sheet.nrows):
        cell_value = str(sheet.cell_value(row, coil_col)).strip()
        # 只保留ASCII数字
        clean_cell_value = ''.join(c for c in cell_value if c.isdigit())
        
        if clean_cell_value == test_coil:
            print(f"  找到匹配: 行 {row}, 原始值='{cell_value}', 清理后='{clean_cell_value}'")
            found = True
            break
        elif row <= header_row + 5:  # 只显示前5个不匹配的值
            print(f"  行 {row}: 原始值='{cell_value}', 清理后='{clean_cell_value}'")
    
    if not found:
        print(f"  未找到钢卷号: {test_coil}")
    print()
