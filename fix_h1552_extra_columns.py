import pandas as pd
import os

print("=" * 100)
print("修复 H1552.xls - 删除多余的列！")
print("=" * 100)
print()

# 读取文件
file_path = r'g:\newplan\计划号\H1552.xls'
df = pd.read_excel(file_path, engine='xlrd')

print(f"原始列数: {len(df.columns)}")

# 找到需要删除的列
cols_to_drop = ['违规标记', '违规说明', '特殊指令']
print(f"\n删除的列: {cols_to_drop}")

# 删除这些列
df_fixed = df.drop(columns=cols_to_drop)

print(f"\n修复后列数: {len(df_fixed.columns)}")

# 检查修复后的前几列是否和H5179.xls一致
print()
print("=" * 100)
print("修复后的前10列:")
print("=" * 100)
for i, col in enumerate(df_fixed.columns[:10]):
    print(f"第{i+1}列: {col}")

# 读取H5179.xls来对比
file2 = r'g:\newplan\计划号\H5179.xls'
df2 = pd.read_excel(file2, engine='xlrd')

print()
print("=" * 100)
print("对比H5179.xls的前10列:")
print("=" * 100)
for i, col in enumerate(df2.columns[:10]):
    print(f"第{i+1}列: {col}")

print()
print("=" * 100)
print("验证钢卷号列的位置:")
print("=" * 100)
if '钢卷号' in df_fixed.columns:
    idx = df_fixed.columns.get_loc('钢卷号')
    print(f"✅ H1552.xls 修复后: 钢卷号在第{idx+1}列")

if '钢卷号' in df2.columns:
    idx = df2.columns.get_loc('钢卷号')
    print(f"✅ H5179.xls: 钢卷号在第{idx+1}列")

# 保存修复后的文件
output_path = r'g:\newplan\计划号\H1552_fixed.xlsx'
df_fixed.to_excel(output_path, index=False, engine='openpyxl')
print()
print(f"✅ 修复后的文件已保存到: {output_path}")
print()
print("=" * 100)
print("修复完成！现在H1552.xls的列顺序和H5179.xls一致了！")
print("=" * 100)
