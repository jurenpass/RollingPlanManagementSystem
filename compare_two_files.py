import pandas as pd
import os

print("=" * 100)
print("对比 H1552.xls 和 H5179.xls")
print("=" * 100)
print()

# 读取两个文件
file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

df1 = pd.read_excel(file1, engine='xlrd')
df2 = pd.read_excel(file2, engine='xlrd')

print(f"✅ H1552.xls: {df1.shape[0]}行, {df1.shape[1]}列")
print(f"✅ H5179.xls: {df2.shape[0]}行, {df2.shape[1]}列")
print()

print("=" * 100)
print("1. 对比列名差异")
print("=" * 100)
cols1 = set(df1.columns)
cols2 = set(df2.columns)

unique_to_1 = cols1 - cols2
unique_to_2 = cols2 - cols1

if unique_to_1:
    print(f"\n❌ 只有 H1552.xls 有的列:")
    for col in sorted(unique_to_1):
        print(f"   - {col}")

if unique_to_2:
    print(f"\n✅ 只有 H5179.xls 有的列:")
    for col in sorted(unique_to_2):
        print(f"   - {col}")

if not unique_to_1 and not unique_to_2:
    print("\n✅ 两个文件列名完全一致！")

print()
print("=" * 100)
print("2. 对比'钢卷号'相关的列")
print("=" * 100)

for df, filename in [(df1, 'H1552.xls'), (df2, 'H5179.xls')]:
    print(f"\n📄 {filename}:")
    coil_related_cols = [c for c in df.columns if '钢卷' in c or '卷' in c]
    for col in sorted(coil_related_cols):
        print(f"   - {col}")
        print(f"     前3个值: {list(df[col].head(3))}")

print()
print("=" * 100)
print("3. 检查 H1552.xls 的前2行详细数据")
print("=" * 100)
print("\nH1552.xls 前2行:")
print(df1.head(2).T)

print()
print("=" * 100)
print("4. 检查 H5179.xls 的前2行详细数据")
print("=" * 100)
print("\nH5179.xls 前2行:")
print(df2.head(2).T)

print()
print("=" * 100)
print("5. 检查关键列的数据类型")
print("=" * 100)
key_columns = ['计划号', '钢卷号', '顺序号', '轧宽', '坯宽']
for col in key_columns:
    if col in df1.columns and col in df2.columns:
        print(f"\n{col}:")
        print(f"  H1552: dtype={df1[col].dtype}, 非空值={df1[col].notna().sum()}/{len(df1)}")
        print(f"  H5179: dtype={df2[col].dtype}, 非空值={df2[col].notna().sum()}/{len(df2)}")
