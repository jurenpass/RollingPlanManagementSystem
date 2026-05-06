import xlrd

# 测试从H5178.xls中提取特定钢卷号的数据
file_path = r"g:\newplan\计划号\H5178.xls"
workbook = xlrd.open_workbook(file_path)
sheet = workbook.sheet_by_index(0)

# 查找列名行
header_row = 2  # 第3行是列名行

# 查找列
headers = []
for col in range(sheet.ncols):
    try:
        header = str(sheet.cell_value(header_row, col)).strip()
        headers.append(header)
    except:
        headers.append('')

print(f"列名: {headers[:15]}")  # 只显示前15列

# 列映射
col_map = {}
for idx, header in enumerate(headers):
    if '钢卷号' in header:
        col_map['coil_no'] = idx
        print(f"找到钢卷号列: {idx}")
    elif '牌号' in header or '钢级' in header:
        col_map['grade'] = idx
    elif '除鳞' in header:
        col_map['scaling'] = idx
    elif '去向' in header:
        col_map['destination'] = idx
    elif '坯厚' in header:
        col_map['blank_thick'] = idx
    elif '坯宽' in header:
        col_map['blank_width'] = idx

print(f"\n列映射: {col_map}")

# 查找特定的钢卷号
target_coils = ['62019537', '62019538']

for target_coil in target_coils:
    print(f"\n查找钢卷号: {target_coil}")
    found = False
    for row in range(header_row + 1, sheet.nrows):
        if 'coil_no' in col_map:
            cell_value = str(sheet.cell_value(row, col_map['coil_no'])).strip()
            # 只保留数字
            clean_cell_value = ''.join(c for c in cell_value if c.isdigit())
            
            if clean_cell_value == target_coil:
                found = True
                print(f"  找到匹配: 行 {row}, 原始值='{cell_value}', 清理后='{clean_cell_value}'")
                # 提取数据
                data = {}
                for key, col_idx in col_map.items():
                    if col_idx < sheet.ncols:
                        try:
                            data[key] = str(sheet.cell_value(row, col_idx)).strip()
                        except:
                            data[key] = ''
                print(f"  数据: {data}")
                break
    
    if not found:
        print(f"  未找到钢卷号: {target_coil}")
