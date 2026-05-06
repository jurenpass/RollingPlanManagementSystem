import xlrd
import xlwt
from xlutils.copy import copy

# 打开装炉顺序.xls文件
rb = xlrd.open_workbook('G:/newplan/计划号/装炉顺序.xls')
r_sheet = rb.sheet_by_index(0)

# 创建一个可写的副本
wb = copy(rb)
ws = wb.get_sheet(0)

# 找到最后一行
last_row = r_sheet.nrows

# 获取最后一行的序号
last_order = r_sheet.cell_value(last_row-1, 0)
if last_order == '':
    last_order = 0
else:
    last_order = int(last_order)

# 添加新的钢卷号
new_row = last_row
ws.write(new_row, 0, last_order + 1)  # 序号
ws.write(new_row, 1, 'H5178')  # 计划号
ws.write(new_row, 2, '62019583')  # 钢卷号

# 保存修改后的文件
wb.save('G:/newplan/计划号/装炉顺序.xls')
print('已添加新钢卷号: 62019583')
print(f'新行位置: {new_row}')
