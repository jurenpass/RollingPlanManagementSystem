import xlrd
import os

def analyze_h5178_in_zhuanglu():
    """分析H5178在装炉顺序中的位置"""
    plan_dir = r"g:\newplan\计划号"
    
    # 读取装炉顺序文件
    zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
    workbook = xlrd.open_workbook(zhuanglu_file)
    sheet = workbook.sheet_by_index(0)
    
    print(f"\n{'='*80}")
    print(f"分析H5178在装炉顺序中的位置")
    print(f"{'='*80}\n")
    
    # 找到列索引
    headers = []
    for col_idx in range(sheet.ncols):
        header = str(sheet.cell_value(0, col_idx)).strip()
        headers.append(header)
    
    print(f"表头: {headers}\n")
    
    zhuanglu_order_col = headers.index("装炉顺序号") if "装炉顺序号" in headers else -1
    plan_no_col = headers.index("计划号") if "计划号" in headers else -1
    coil_no_col = headers.index("钢卷号") if "钢卷号" in headers else -1
    
    # 收集所有H5178的钢卷号
    h5178_coils = []
    all_coils = []
    
    for row_idx in range(1, sheet.nrows):
        zhuanglu_order = int(sheet.cell_value(row_idx, zhuanglu_order_col)) if zhuanglu_order_col != -1 else row_idx
        plan_no = str(sheet.cell_value(row_idx, plan_no_col)).strip()
        coil_no = str(sheet.cell_value(row_idx, coil_no_col)).strip()
        
        coil_info = {
            "zhuanglu_order": zhuanglu_order,
            "plan_no": plan_no,
            "coil_no": coil_no,
            "row_idx": row_idx
        }
        
        all_coils.append(coil_info)
        
        if plan_no == "H5178":
            h5178_coils.append(coil_info)
    
    print(f"装炉顺序中总共有 {len(all_coils)} 条记录")
    print(f"H5178在装炉顺序中有 {len(h5178_coils)} 条记录\n")
    
    print(f"{'装炉顺序号':<15} {'计划号':<10} {'钢卷号':<15} {'行索引':<10}")
    print(f"{'-'*60}")
    
    for coil in h5178_coils:
        print(f"{coil['zhuanglu_order']:<15} {coil['plan_no']:<10} {coil['coil_no']:<15} {coil['row_idx']:<10}")
    
    print(f"\n{'-'*80}")
    print(f"H5178在装炉顺序中的分布（查看周围的计划号）：\n")
    
    # 找出H5178记录周围的记录
    for h_coil in h5178_coils:
        row_idx = h_coil['row_idx']
        print(f"\n装炉顺序号 {h_coil['zhuanglu_order']} (行 {row_idx}):")
        
        # 显示前3条和后3条
        start_idx = max(1, row_idx - 3)
        end_idx = min(sheet.nrows, row_idx + 4)
        
        for i in range(start_idx, end_idx):
            z_order = int(sheet.cell_value(i, zhuanglu_order_col)) if zhuanglu_order_col != -1 else i
            p_no = str(sheet.cell_value(i, plan_no_col)).strip()
            c_no = str(sheet.cell_value(i, coil_no_col)).strip()
            
            marker = " <-- H5178" if p_no == "H5178" else ""
            print(f"  装炉顺序 {z_order:4d}: 计划号 {p_no:10s}, 钢卷号 {c_no:15s}{marker}")

if __name__ == "__main__":
    analyze_h5178_in_zhuanglu()
