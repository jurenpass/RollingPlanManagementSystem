import xlrd

print("=" * 100)
print("对比H1552.xls和H5179.xls的列结构")
print("=" * 100)

# 读取两个文件
file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

wb1 = xlrd.open_workbook(file1)
wb2 = xlrd.open_workbook(file2)

sheet1 = wb1.sheet_by_index(0)
sheet2 = wb2.sheet_by_index(0)

cols1 = [sheet1.cell_value(0, i) for i in range(sheet1.ncols)]
cols2 = [sheet2.cell_value(0, i) for i in range(sheet2.ncols)]

print(f"\nH1552.xls 列数: {len(cols1)}")
print(f"H5179.xls 列数: {len(cols2)}")

print("\n" + "=" * 100)
print("列名对比（按顺序）:")
print("=" * 100)

max_len = max(len(cols1), len(cols2))
for i in range(max_len):
    col1 = cols1[i] if i < len(cols1) else ""
    col2 = cols2[i] if i < len(cols2) else ""
    
    if col1 == col2:
        status = "✓"
    else:
        status = "✗"
        
    print(f"{status} [{i:3d}] H1552: '{col1}' | H5179: '{col2}'")

print("\n" + "=" * 100)
print("H1552.xls特有的列（按出现顺序）:")
print("=" * 100)
for i, col in enumerate(cols1):
    if col and col not in cols2:
        print(f"  [{i:3d}] '{col}'")

print("\n" + "=" * 100)
print("检查关键列的位置:")
print("=" * 100)
key_cols = ["顺序号", "钢卷号", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽", "碳", "粗轧报信", "层号", "坯厚", "坯长"]

for col in key_cols:
    pos1 = cols1.index(col) if col in cols1 else -1
    pos2 = cols2.index(col) if col in cols2 else -1
    
    if pos1 == pos2:
        status = "✓"
    else:
        status = "✗"
    
    print(f"{status} {col}: H1552位置={pos1}, H5179位置={pos2}")

# 检查是否有位置偏移
print("\n" + "=" * 100)
print("检查列位置差异（H1552 - H5179）:")
print("=" * 100)
for col in key_cols:
    if col in cols1 and col in cols2:
        diff = cols1.index(col) - cols2.index(col)
        if diff != 0:
            print(f"  {col}: 位置偏移 {diff} 列")

wb1.release_resources()
wb2.release_resources()
