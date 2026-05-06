import xlrd
import os

# 检查H5178.xls文件
file_path = r"g:\newplan\计划号\H5178.xls"

if not os.path.exists(file_path):
    print(f"文件不存在: {file_path}")
else:
    print(f"检查文件: {file_path}")
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    
    print(f"总行数: {sheet.nrows}")
    print(f"总列数: {sheet.ncols}")
    print("\n前10行内容:")
    
    for row in range(min(10, sheet.nrows)):
        row_data = []
        for col in range(sheet.ncols):
            try:
                value = sheet.cell_value(row, col)
                row_data.append(str(value))
            except:
                row_data.append('')
        print(f"行 {row}: {row_data[:15]}")  # 只显示前15列
        
    print("\n查找钢卷号列...")
    # 尝试找到包含钢卷号的列
    for col in range(sheet.ncols):
        for row in range(sheet.nrows):
            try:
                value = str(sheet.cell_value(row, col)).strip()
                if value.isdigit() and 8 <= len(value) <= 12:
                    print(f"找到可能的钢卷号: {value} 在行 {row}, 列 {col}")
                    # 显示该行的其他数据
                    row_data = []
                    for c in range(min(20, sheet.ncols)):
                        try:
                            v = str(sheet.cell_value(row, c)).strip()
                            row_data.append(v)
                        except:
                            row_data.append('')
                    print(f"  该行数据: {row_data}")
                    break
            except:
                pass
