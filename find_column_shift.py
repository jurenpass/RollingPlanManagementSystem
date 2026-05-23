import pandas as pd

print("=" * 100)
print("对比列顺序的关键差异！")
print("=" * 100)
print()

# 读取两个文件
file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

df1 = pd.read_excel(file1, engine='xlrd')
df2 = pd.read_excel(file2, engine='xlrd')

print("=" * 100)
print("对比前20列的顺序差异")
print("=" * 100)
max_cols = min(len(df1.columns), len(df2.columns), 30)
for i in range(max_cols):
    col1 = df1.columns[i] if i < len(df1.columns) else '(无)'
    col2 = df2.columns[i] if i < len(df2.columns) else '(无)'
    
    if col1 != col2:
        print(f"第{i+1}列: ❌ H1552='{col1}' | H5179='{col2}'")
    else:
        print(f"第{i+1}列: ✅ H1552='{col1}' | H5179='{col2}'")

print()
print("=" * 100)
print("找到钢卷号列在两个文件中的位置")
print("=" * 100)

for df, name in [(df1, 'H1552.xls'), (df2, 'H5179.xls')]:
    if '钢卷号' in df.columns:
        idx = df.columns.get_loc('钢卷号')
        print(f"{name}: 钢卷号在第{idx+1}列")
        print(f"  前几列: {list(df.columns[max(0, idx-3):idx+1])}")

print()
print("=" * 100)
print("结论！")
print("=" * 100)
print("\n问题发现：H1552.xls 多了几列！")
print("  - H1552.xls: 第5-7列是 ['违规标记', '违规说明', '特殊指令']")
print("  - H5179.xls: 第5列就是 '钢卷号'")
print("\n这就是为什么H1552.xls处理失败的原因！")
print("钢卷号列的位置偏移了！")
