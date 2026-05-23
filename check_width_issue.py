import xlrd

# 检查调宽问题的触发条件
# 条件：板坯头部宽度和尾部宽度的较小值 <= 轧宽值

file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

def check_width_issue(file_path, description):
    print(f"\n{'='*80}")
    print(f"检查 {description} 的调宽问题")
    print('='*80)

    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)

    cols = [sheet.cell_value(0, i) for i in range(sheet.ncols)]

    # 找到需要的列
    头部宽度_col = cols.index("板坯头部宽度") if "板坯头部宽度" in cols else -1
    尾部宽度_col = cols.index("板坯尾部宽度") if "板坯尾部宽度" in cols else -1
    轧宽_col = cols.index("轧宽") if "轧宽" in cols else -1
    钢卷号_col = cols.index("钢卷号") if "钢卷号" in cols else -1
    调宽标记_col = cols.index("板坯宽度调宽标记") if "板坯宽度调宽标记" in cols else -1

    print(f"列位置: 头部宽度={头部宽度_col}, 尾部宽度={尾部宽度_col}, 轧宽={轧宽_col}, 钢卷号={钢卷号_col}")

    issue_count = 0
    for row_idx in range(1, sheet.nrows):
        钢卷号 = sheet.cell_value(row_idx, 钢卷号_col) if 钢卷号_col != -1 else ""
        头部宽度 = sheet.cell_value(row_idx, 头部宽度_col) if 头部宽度_col != -1 else 0
        尾部宽度 = sheet.cell_value(row_idx, 尾部宽度_col) if 尾部宽度_col != -1 else 0
        轧宽 = sheet.cell_value(row_idx, 轧宽_col) if 轧宽_col != -1 else 0
        调宽标记 = sheet.cell_value(row_idx, 调宽标记_col) if 调宽标记_col != -1 else ""

        try:
            头部宽度 = float(头部宽度) if 头部宽度 != "" else 0
            尾部宽度 = float(尾部宽度) if 尾部宽度 != "" else 0
            轧宽 = float(轧宽) if 轧宽 != "" else 0
        except:
            continue

        较小值 = min(头部宽度, 尾部宽度)
        是否触发 = 较小值 <= 轧宽 and 轧宽 > 0

        if 是否触发:
            issue_count += 1
            if issue_count <= 5:  # 只显示前5条
                print(f"  ⚠️ 钢卷号={钢卷号}, 头部={头部宽度}, 尾部={尾部宽度}, 轧宽={轧宽}, 较小值={较小值}, 触发调宽问题!")
            elif issue_count == 6:
                print(f"  ... (还有更多)")

    print(f"\n总共有 {issue_count} 行触发了调宽问题")
    wb.release_resources()

check_width_issue(file1, "H1552.xls")
check_width_issue(file2, "H5179.xls")
