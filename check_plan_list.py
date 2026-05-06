import xlrd

# 读取总计划号列表文件
workbook = xlrd.open_workbook('G:\\newplan\\计划号\\总计划号列表.xls')
sheet = workbook.sheet_by_index(0)

# 获取列名
headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
print('列名:', headers)

# 查找计划号列
plan_col = -1
for i, header in enumerate(headers):
    if '计划号' in str(header):
        plan_col = i
        break

print('计划号列索引:', plan_col)

# 如果找到计划号列，打印相关信息
if plan_col != -1:
    plan_numbers = []
    for row in range(1, sheet.nrows):
        plan_no = str(sheet.cell_value(row, plan_col)).strip()
        if plan_no:
            plan_numbers.append(plan_no)
    
    print('计划号数量:', len(plan_numbers))
    print('前10个计划号:', plan_numbers[:10])
    # 检查是否包含H5182
    print('包含H5182:', 'H5182' in plan_numbers)
    print('所有计划号:', plan_numbers)