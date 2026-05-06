import xlrd

file_path = r"g:\newplan\计划号\H5178.xls"
workbook = xlrd.open_workbook(file_path)
sheet = workbook.sheet_by_index(0)

print("检查前5行，寻找包含'钢卷号'或'序号'的行:\n")

for i in range(min(5, sheet.nrows)):
    row_values = []
    for col in range(sheet.ncols):
        try:
            value = str(sheet.cell_value(i, col)).strip()
            row_values.append(value)
        except:
            row_values.append('')
    
    # 检查是否包含"钢卷号"或"序号"
    has_coil_col = any('钢卷号' in v for v in row_values)
    has_seq_col = any('序号' in v for v in row_values)
    
    print(f"行 {i}: has_coil_col={has_coil_col}, has_seq_col={has_seq_col}")
    print(f"  内容: {row_values[:10]}")  # 只显示前10列
    print()
