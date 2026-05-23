import xlrd
import xlwt
import pandas as pd
import os
import tempfile

def full_process(file_path):
    """模拟完整的处理流程"""
    print(f"\n{'='*100}")
    print(f"完整处理测试: {os.path.basename(file_path)}")
    print('='*100)
    
    try:
        # 1. 读取文件
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        
        # 2. 获取当前列名
        current_columns = []
        for i in range(sheet.ncols):
            current_columns.append(sheet.cell_value(0, i))
        
        print(f"原始列数: {len(current_columns)}")
        
        # 3. 定义目标列
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
            "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
            "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式", "板坯头部宽度", "板坯尾部宽度",
            "计划号", "热轧产品分类", "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽",
            "装炉顺序号"
        ]
        
        # 4. 初始化统计变量
        无APS钢种数 = 0
        无APS块数 = 0
        已添加无APS的钢种 = set()
        包含无APS = False
        减宽超标块数 = 0
        逆宽轧制板坯数 = 0
        低轧宽板坯数 = 0
        极低轧宽板坯数 = 0
        调宽问题列表 = []
        
        # 5. 收集所有行数据
        all_row_data = []
        has_low_roll_width = False
        
        for row_idx in range(1, min(3, sheet.nrows)):  # 只处理前2行
            row_data = {}
            for col_idx, col_name in enumerate(current_columns):
                row_data[col_name] = sheet.cell_value(row_idx, col_idx)
            
            # 测试填充"装炉顺序号"字段
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                print(f"\n处理行 {row_idx}:")
                print(f"  钢卷号: {钢卷号值}")
            
            # 如果"装炉顺序号"缺失，使用"顺序号"作为备选
            if "装炉顺序号" not in row_data or row_data.get("装炉顺序号") is None or pd.isna(row_data.get("装炉顺序号")):
                if "顺序号" in row_data and row_data["顺序号"] is not None and not pd.isna(row_data["顺序号"]):
                    row_data["装炉顺序号"] = row_data["顺序号"]
                    print(f"  使用顺序号作为装炉顺序号: {row_data['顺序号']}")
                else:
                    row_data["装炉顺序号"] = ""
                    print(f"  装炉顺序号缺失，设为空")
            
            # 如果"轧宽+（余量）"缺失，使用"轧宽"作为备选
            if "轧宽+（余量）" not in row_data or row_data.get("轧宽+（余量）") is None or pd.isna(row_data.get("轧宽+（余量）")):
                if "轧宽" in row_data and row_data["轧宽"] is not None and not pd.isna(row_data["轧宽"]):
                    row_data["轧宽+（余量）"] = row_data["轧宽"]
                    print(f"  使用轧宽作为轧宽+（余量）: {row_data['轧宽']}")
                else:
                    row_data["轧宽+（余量）"] = ""
                    print(f"  轧宽+（余量）缺失，设为空")
            
            # 检查减宽超标
            if "板坯宽度调宽标记" in row_data and str(row_data.get("板坯宽度调宽标记", "")).strip() != "0":
                if "板坯头部宽度" in row_data and "板坯尾部宽度" in row_data and "坯宽" in row_data:
                    try:
                        板坯头部宽度值 = float(row_data.get("板坯头部宽度", 0)) if row_data.get("板坯头部宽度", 0) != "" else 0
                        板坯尾部宽度值 = float(row_data.get("板坯尾部宽度", 0)) if row_data.get("板坯尾部宽度", 0) != "" else 0
                        坯宽新值 = max(板坯头部宽度值, 板坯尾部宽度值)
                        row_data["坯宽"] = 坯宽新值
                        
                        if "轧宽" in row_data:
                            轧宽值 = float(row_data.get("轧宽", 0)) if row_data.get("轧宽", 0) != "" else 0
                            减宽新值 = 坯宽新值 - 轧宽值
                            if 减宽新值 >= 240:
                                print(f"  ⚠️ 减宽量超标: {减宽新值}")
                            elif 减宽新值 < 0:
                                print(f"  ⚠️ 逆宽轧制")
                            row_data["侧压量"] = 减宽新值
                            
                            # 检查调宽三角符号
                            宽度较小值 = min(板坯头部宽度值, 板坯尾部宽度值)
                            if 宽度较小值 <= 轧宽值:
                                row_data["板坯宽度调宽标记"] = str(减宽新值) + "Δ"
                                print(f"  调宽标记: {row_data['板坯宽度调宽标记']}")
                                # 这里会使用调宽问题列表
                                if "钢卷号" in row_data:
                                    钢卷号 = row_data.get("钢卷号", "")
                                    调宽问题信息 = f"{钢卷号}-{宽度较小值}"
                                    调宽问题列表.append(调宽问题信息)
                                    print(f"  调宽问题列表添加: {调宽问题信息}")
                    except Exception as e:
                        print(f"  处理调宽时出错: {e}")
            
            all_row_data.append(row_data)
        
        # 6. 测试写入目标列
        print("\n测试写入目标列:")
        for col_name in target_columns[:5]:  # 只测试前5列
            if col_name in all_row_data[0]:
                print(f"  ✅ {col_name}: {all_row_data[0][col_name]}")
            else:
                print(f"  ❌ {col_name}: 缺失")
        
        # 7. 释放资源
        if hasattr(workbook, 'release_resources'):
            workbook.release_resources()
        
        print("\n✓ 完整处理测试成功！")
        return True, has_low_roll_width, 包含无APS
        
    except Exception as e:
        print(f"\n❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, False, False

# 测试H5179.xls
success, has_low, has_no_aps = full_process(r'g:\newplan\计划号\H5179.xls')

# 测试H1552.xls
success, has_low, has_no_aps = full_process(r'g:\newplan\计划号\H1552.xls')
