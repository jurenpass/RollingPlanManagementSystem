import pandas as pd

print("=" * 100)
print("深入对比 H1552.xls 和 H5179.xls 的数据内容")
print("=" * 100)
print()

# 读取两个文件
file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

df1 = pd.read_excel(file1, engine='xlrd')
df2 = pd.read_excel(file2, engine='xlrd')

print("=" * 100)
print("检查 H1552.xls 特有的列是否有数据")
print("=" * 100)
unique_cols = ['作业长CP', '加热CP.1', '卷取CP.1', '板坯CP.1', '特殊指令', '粗轧CP.1', '精轧CP.1', '质检CP.1', '运输链CP']
for col in unique_cols:
    if col in df1.columns:
        non_null = df1[col].notna().sum()
        print(f"{col}: {non_null}/{len(df1)} 行有数据")
        if non_null > 0:
            print(f"  前3个值: {list(df1[col].dropna().head(3))}")
print()

print("=" * 100)
print("检查前10列的具体内容（对比两个文件）")
print("=" * 100)
for i, col in enumerate(df1.columns[:10]):
    if i < len(df2.columns):
        col2 = df2.columns[i]
        print(f"\n第{i+1}列:")
        print(f"  H1552: '{col}' → {df1[col].dtype}")
        print(f"  H5179: '{col2}' → {df2[col2].dtype}")
        print(f"  H1552前2值: {list(df1[col].head(2))}")
        print(f"  H5179前2值: {list(df2[col2].head(2))}")

print()
print("=" * 100)
print("检查是否有列全为空")
print("=" * 100)
print("\nH1552.xls 全为空的列:")
empty_cols1 = [c for c in df1.columns if df1[c].isna().all()]
if empty_cols1:
    for col in empty_cols1:
        print(f"  ❌ {col}")
else:
    print("  ✅ 没有全为空的列")

print("\nH5179.xls 全为空的列:")
empty_cols2 = [c for c in df2.columns if df2[c].isna().all()]
if empty_cols2:
    for col in empty_cols2:
        print(f"  ❌ {col}")
else:
    print("  ✅ 没有全为空的列")

print()
print("=" * 100)
print("检查计划号和新计划号列")
print("=" * 100)
for df, name in [(df1, 'H1552.xls'), (df2, 'H5179.xls')]:
    print(f"\n{name}:")
    if '计划号' in df.columns:
        print(f"  计划号列值: {df['计划号'].unique()}")
    if '新计划号' in df.columns:
        print(f"  新计划号列值: {df['新计划号'].unique()}")

print()
print("=" * 100)
print("检查第一列（那个空列）的详细内容")
print("=" * 100)
first_col_1 = df1.columns[0]
first_col_2 = df2.columns[0]
print(f"\nH1552.xls 第一列名: '{first_col_1}'")
print(f"  所有唯一值: {df1[first_col_1].unique()}")

print(f"\nH5179.xls 第一列名: '{first_col_2}'")
print(f"  所有唯一值: {df2[first_col_2].unique()}")
