import xlrd
import os
import tempfile
import shutil

# 模拟程序逻辑，检查特定钢卷号的处理

# 1. 从装炉顺序.xls读取数据
plan_dir = r"g:\newplan\计划号"
excel_file = os.path.join(plan_dir, "装炉顺序.xls")

print(f"读取装炉顺序文件: {excel_file}")

# 创建临时副本
temp_file = tempfile.NamedTemporaryFile(suffix='.xls', delete=False)
temp_file_path = temp_file.name
temp_file.close()
shutil.copy2(excel_file, temp_file_path)

workbook = xlrd.open_workbook(temp_file_path)
sheet = workbook.sheet_by_index(0)

headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
print(f"列名: {headers}")

# 查找列索引
order_col = None
plan_col = None
coil_col = None

for idx, header in enumerate(headers):
    if '装炉顺序号' in header or '装炉顺序' in header:
        order_col = idx
        print(f"找到装炉顺序列: {idx}")
    elif '计划号' in header and '新' not in header:
        plan_col = idx
        print(f"找到计划号列: {idx}")
    elif '钢卷号' in header:
        coil_col = idx
        print(f"找到钢卷号列: {idx}")

# 查找特定的钢卷号
target_coils = ['62019537', '62019538']
print(f"\n查找钢卷号: {target_coils}")

for row in range(1, sheet.nrows):
    try:
        order = sheet.cell_value(row, order_col)
        if isinstance(order, float) and order.is_integer():
            order = int(order)
        plan_no = str(sheet.cell_value(row, plan_col)).strip()
        coil_no = str(sheet.cell_value(row, coil_col)).strip()
        # 只保留数字
        coil_no_clean = ''.join(c for c in coil_no if c.isdigit())
        
        if coil_no_clean in target_coils:
            print(f"找到: 行 {row}, 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no} -> 清理后={coil_no_clean}")
    except Exception as e:
        print(f"读取行 {row} 失败: {e}")

# 清理临时文件
os.unlink(temp_file_path)
