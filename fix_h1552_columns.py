import pandas as pd
import os

# 读取文件
file_path = r'g:\newplan\计划号\H1552.xls'
df = pd.read_excel(file_path, engine='xlrd')

print("=" * 80)
print("修复 H1552.xls 列名问题")
print("=" * 80)
print()

# 重命名列名（修复空格问题）
column_mapping = {
    '钢卷 号': '钢卷号',           # 钢卷号（修复空格）
    '厚度 负公差': '厚度负公差',   # 厚度负公差（修复空格）
    '板 坯进TOP点时间': '板坯进TOP点时间',  # 修复空格
    '断裂延伸率（预 留）': '断裂延伸率（预留）',  # 修复空格
    ' 目标温度控制选择': '目标温度控制选择',  # 修复开头空格
}

# 执行重命名
df_renamed = df.rename(columns=column_mapping)

# 检查是否需要添加缺失的列
print("检查缺失的列：")
print()

# 1. 检查轧宽+（余量）列 - 如果没有，创建它
if '轧宽+（余量）' not in df_renamed.columns:
    if '轧宽' in df_renamed.columns and '宽展量' in df_renamed.columns:
        # 轧宽+（余量）= 轧宽 + 宽展量
        df_renamed['轧宽+（余量）'] = df_renamed['轧宽'] + df_renamed['宽展量']
        print("✅ 已创建 '轧宽+（余量）' 列（轧宽 + 宽展量）")
    elif '轧宽' in df_renamed.columns:
        df_renamed['轧宽+（余量）'] = df_renamed['轧宽']
        print("✅ 已创建 '轧宽+（余量）' 列（使用轧宽值）")
    else:
        print("❌ 无法创建 '轧宽+（余量）' 列（缺少轧宽列）")

# 2. 检查装炉顺序号列 - 如果没有，创建它
if '装炉顺序号' not in df_renamed.columns:
    if '顺序号' in df_renamed.columns:
        df_renamed['装炉顺序号'] = df_renamed['顺序号']
        print("✅ 已创建 '装炉顺序号' 列（使用顺序号）")
    else:
        print("❌ 无法创建 '装炉顺序号' 列（缺少顺序号列）")

# 删除第一列（空列）
if ' ' in df_renamed.columns or df_renamed.columns[0] == ' ':
    df_renamed = df_renamed.drop(columns=[df_renamed.columns[0]])
    print("✅ 已删除空列")

print()
print("=" * 80)
print("修复后的列名：")
print("=" * 80)
print(list(df_renamed.columns))

print()
print("=" * 80)
print("检查关键列是否存在：")
print("=" * 80)
key_columns = ['钢卷号', '轧宽+（余量）', '装炉顺序号']
for col in key_columns:
    if col in df_renamed.columns:
        print(f"✅ {col}")
    else:
        print(f"❌ {col}")

print()
print("=" * 80)
print("数据预览：")
print("=" * 80)
print(df_renamed[['计划号', '顺序号', '钢卷号', '轧宽+（余量）', '装炉顺序号']].head())

# 保存修复后的文件（使用xlsx格式）
output_path = r'g:\newplan\计划号\H1552_fixed.xlsx'
df_renamed.to_excel(output_path, index=False, engine='openpyxl')
print()
print(f"✅ 修复后的文件已保存到: {output_path}")
print("   注意：文件保存为.xlsx格式（xlsx格式更稳定）")

print()
print("=" * 80)
print("修复完成！")
print("=" * 80)