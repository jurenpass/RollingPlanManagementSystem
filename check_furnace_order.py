import xlrd

# 读取装炉顺序文件
furnace_order_file = r'g:\newplan\计划号\装炉顺序.xls'
h1552_file = r'g:\newplan\计划号\H1552.xls'

try:
    # 读取装炉顺序文件
    wb_order = xlrd.open_workbook(furnace_order_file)
    sheet_order = wb_order.sheet_by_index(0)
    
    # 获取装炉顺序文件的列名
    headers = []
    for col_idx in range(sheet_order.ncols):
        headers.append(sheet_order.cell_value(0, col_idx))
    
    print("装炉顺序.xls 列名:")
    for i, header in enumerate(headers):
        print(f"  [{i}] '{header}'")
    
    # 找到钢卷号列
    if "钢卷号" in headers:
        coil_col = headers.index("钢卷号")
        print(f"\n钢卷号列索引: {coil_col}")
        
        # 收集所有钢卷号
        coil_numbers = set()
        for row_idx in range(1, sheet_order.nrows):
            coil_no = sheet_order.cell_value(row_idx, coil_col)
            if coil_no:
                coil_numbers.add(str(coil_no))
        
        print(f"装炉顺序.xls 中共有 {len(coil_numbers)} 个钢卷号")
        
        # 读取H1552.xls的钢卷号
        wb_h1552 = xlrd.open_workbook(h1552_file)
        sheet_h1552 = wb_h1552.sheet_by_index(0)
        
        h1552_cols = []
        for i in range(sheet_h1552.ncols):
            h1552_cols.append(sheet_h1552.cell_value(0, i))
        
        if "钢卷号" in h1552_cols:
            h1552_coil_col = h1552_cols.index("钢卷号")
            print(f"\nH1552.xls 钢卷号列索引: {h1552_coil_col}")
            
            # 检查H1552.xls的钢卷号是否在装炉顺序文件中
            print("\nH1552.xls 的钢卷号在装炉顺序.xls中的匹配情况:")
            found_count = 0
            not_found_count = 0
            not_found_list = []
            
            for row_idx in range(1, min(10, sheet_h1552.nrows)):  # 只检查前10行
                coil_no = sheet_h1552.cell_value(row_idx, h1552_coil_col)
                coil_str = str(coil_no)
                if coil_str in coil_numbers:
                    print(f"  ✅ {coil_str} - 找到")
                    found_count += 1
                else:
                    print(f"  ❌ {coil_str} - 未找到")
                    not_found_count += 1
                    not_found_list.append(coil_str)
            
            print(f"\n总计: 找到 {found_count} 个, 未找到 {not_found_count} 个")
            if not_found_list:
                print(f"未找到的钢卷号: {', '.join(not_found_list)}")
        
        wb_h1552.release_resources()
    
    wb_order.release_resources()

except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()
