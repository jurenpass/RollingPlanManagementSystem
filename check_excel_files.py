import xlrd
import os

def read_excel_file(file_path):
    """读取Excel文件内容"""
    print(f"\n{'='*80}")
    print(f"文件: {file_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        workbook = xlrd.open_workbook(file_path)
        print(f"工作表数量: {len(workbook.sheet_names())}")
        print(f"工作表名称: {workbook.sheet_names()}")
        
        for sheet_idx in range(min(len(workbook.sheet_names()), 2)):
            sheet = workbook.sheet_by_index(sheet_idx)
            print(f"\n--- 工作表 {sheet_idx}: {sheet.name} ---")
            print(f"行数: {sheet.nrows}, 列数: {sheet.ncols}")
            
            # 显示前20行
            for row_idx in range(min(sheet.nrows, 20)):
                row_values = []
                for col_idx in range(min(sheet.ncols, 10)):
                    cell_value = sheet.cell_value(row_idx, col_idx)
                    row_values.append(str(cell_value))
                print(f"行 {row_idx}: {' | '.join(row_values)}")
                
    except Exception as e:
        print(f"读取文件失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    plan_dir = r"g:\newplan\计划号"
    
    # 读取装炉顺序文件
    zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
    read_excel_file(zhuanglu_file)
    
    # 读取H5178文件
    h5178_file = os.path.join(plan_dir, "H5178.xls")
    read_excel_file(h5178_file)
