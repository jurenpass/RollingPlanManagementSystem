import pandas as pd

print("=" * 100)
print("最终验证修复后的H1552.xls")
print("=" * 100)
print()

# 读取修复后的文件和H5179.xls
file_fixed = r'g:\newplan\计划号\H1552_fixed.xlsx'
file2 = r'g:\newplan\计划号\H5179.xls'

df_fixed = pd.read_excel(file_fixed, engine='openpyxl')
df2 = pd.read_excel(file2, engine='xlrd')

print("=" * 100)
print("对比前25列的完整顺序")
print("=" * 100)
max_cols = min(len(df_fixed.columns), len(df2.columns), 25)
all_match = True

for i in range(max_cols):
    col1 = df_fixed.columns[i] if i < len(df_fixed.columns) else '(无)'
    col2 = df2.columns[i] if i < len(df2.columns) else '(无)'
    
    if col1 != col2:
        print(f"第{i+1}列: ❌ H1552_fixed='{col1}' | H5179='{col2}'")
        all_match = False
    else:
        print(f"第{i+1}列: ✅ H1552_fixed='{col1}' | H5179='{col2}'")

print()
if all_match:
    print("✅ 前25列完全一致！")
else:
    print("❌ 还有列不一致")
print()

print("=" * 100)
print("数据预览（前3行，前10列）")
print("=" * 100)
print("\nH1552_fixed.xlsx:")
print(df_fixed.iloc[:3, :10])
print("\nH5179.xls:")
print(df2.iloc[:3, :10])
