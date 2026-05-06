import xlrd
import os

# 检查装炉顺序.xls文件
file_path = r"g:\newplan\计划号\装炉顺序.xls"

if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
else:
    print(f"检查文件: {file_path}")
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    
    print(f"总行数: {sheet.nrows}")
    print(f"总列数: {sheet.ncols}")
    print("\n前20行内容:")
    
    for row in range(min(20, sheet.nrows)):
        row_data = []
        for col in range(sheet.ncols):
            try:
                value = sheet.cell_value(row, col)
                row_data.append(str(value))
            except:
                row_data.append('')
        print(f"行 {row}: {row_data}")
        
    # 查找特定的钢卷号
    print("\n查找钢卷号 62019537 和 62019538:")
    for row in range(1, sheet.nrows):
        for col in range(sheet.ncols):
            try:
                value = str(sheet.cell_value(row, col)).strip()
                if '62019537' in value or '62019538' in value:
                    print(f"找到: 行 {row}, 列 {col}, 值='{value}'")
            except:
                pass
