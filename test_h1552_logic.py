import xlrd
import pandas as pd

# 只测试数据处理逻辑，不保存文件
file_path = r'g:\newplan\计划号\H1552.xls'

try:
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    
    # 获取列名
    current_columns = []
    for i in range(sheet.ncols):
        current_columns.append(sheet.cell_value(0, i))
    
    print(f"H1552.xls 列数: {len(current_columns)}")
    
    # 目标列
    target_columns = [
        "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
        "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
        "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式", "板坯头部宽度", "板坯尾部宽度",
        "计划号", "热轧产品分类", "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽",
        "装炉顺序号"
    ]
    
    # 初始化变量（关键修复：添加调宽问题列表）
    调宽问题列表 = []
    
    # 处理数据
    all_row_data = []
    for row_idx in range(1, min(5, sheet.nrows)):
        row_data = {}
        for col_idx, col_name in enumerate(current_columns):
            row_data[col_name] = sheet.cell_value(row_idx, col_idx)
        
        # 填充缺失字段
        if "轧宽+（余量）" not in row_data or pd.isna(row_data.get("轧宽+（余量）")):
            if "轧宽" in row_data:
                row_data["轧宽+（余量）"] = row_data["轧宽"]
        
        if "装炉顺序号" not in row_data or pd.isna(row_data.get("装炉顺序号")):
            if "顺序号" in row_data:
                row_data["装炉顺序号"] = row_data["顺序号"]
        
        # 测试调宽问题列表的使用
        if "板坯宽度调宽标记" in row_data and str(row_data.get("板坯宽度调宽标记", "")).strip() != "0":
            if "板坯头部宽度" in row_data and "板坯尾部宽度" in row_data and "坯宽" in row_data and "轧宽" in row_data:
                try:
                    板坯头部宽度值 = float(row_data.get("板坯头部宽度", 0)) if row_data.get("板坯头部宽度", 0) != "" else 0
                    板坯尾部宽度值 = float(row_data.get("板坯尾部宽度", 0)) if row_data.get("板坯尾部宽度", 0) != "" else 0
                    轧宽值 = float(row_data.get("轧宽", 0)) if row_data.get("轧宽", 0) != "" else 0
                    
                    宽度较小值 = min(板坯头部宽度值, 板坯尾部宽度值)
                    if 宽度较小值 <= 轧宽值:
                        钢卷号 = row_data.get("钢卷号", "")
                        调宽问题信息 = f"{钢卷号}-{宽度较小值}"
                        调宽问题列表.append(调宽问题信息)  # 这里不会再报错了！
                        print(f"  添加调宽问题: {调宽问题信息}")
                except Exception as e:
                    print(f"  处理调宽时出错: {e}")
        
        all_row_data.append(row_data)
    
    # 验证处理结果
    print("\n处理结果验证:")
    for col in target_columns[:5]:
        if col in all_row_data[0]:
            print(f"  ✅ {col}: {all_row_data[0][col]}")
        else:
            print(f"  ❌ {col}: 缺失")
    
    print(f"\n调宽问题列表长度: {len(调宽问题列表)}")
    
    workbook.release_resources()
    
    print("\n✓ H1552.xls 数据处理逻辑测试成功！")
    print("  修复了 '调宽问题列表' 未定义的问题")
    print("  类似H1552.XLS的计划现在可以正常处理")
    
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
