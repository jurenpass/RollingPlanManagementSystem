import pandas as pd

print("=" * 100)
print("深入分析H1552.xls处理失败的原因")
print("=" * 100)
print()

# 读取两个文件
file1 = r'g:\newplan\计划号\H1552.xls'
file2 = r'g:\newplan\计划号\H5179.xls'

df1 = pd.read_excel(file1, engine='xlrd')
df2 = pd.read_excel(file2, engine='xlrd')

# 程序需要的关键列
required_columns = [
    "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", 
    "轧宽+（余量）", "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", 
    "中间坯厚度设定值", "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式", 
    "板坯头部宽度", "板坯尾部宽度", "计划号", "热轧产品分类", "炼钢钢种", 
    "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽", "装炉顺序号"
]

print("=" * 100)
print("检查H1552.xls是否缺少关键列：")
print("=" * 100)
missing_in_h1552 = []
for col in required_columns:
    if col not in df1.columns:
        missing_in_h1552.append(col)
        print(f"❌ {col} - 缺失！")
    else:
        print(f"✅ {col}")

print()
if missing_in_h1552:
    print(f"⚠️  H1552.xls缺失 {len(missing_in_h1552)} 个关键列")
else:
    print("✅ H1552.xls包含所有关键列！")

print()
print("=" * 100)
print("检查列名是否有空格或特殊字符差异：")
print("=" * 100)

# 检查列名是否完全一致（包括空格）
df1_cols = set(df1.columns)
df2_cols = set(df2.columns)

print("\nH1552.xls特有的列：")
for col in sorted(df1_cols - df2_cols):
    print(f"  - '{col}'")

print("\nH5179.xls特有的列：")
for col in sorted(df2_cols - df1_cols):
    print(f"  - '{col}'")

# 检查是否有看起来相同但实际不同的列名
print()
print("=" * 100)
print("检查可能的列名差异（空格、换行符等）：")
print("=" * 100)
for col in df1.columns:
    # 检查列名是否包含空格或不可见字符
    if ' ' in col or '\t' in col or '\n' in col:
        print(f"⚠️  '{col}' 包含空格或特殊字符")

print()
print("=" * 100)
print("检查关键列的数据类型：")
print("=" * 100)
key_cols = ['计划号', '钢卷号', '顺序号', '轧宽', '坯宽']
for col in key_cols:
    if col in df1.columns and col in df2.columns:
        print(f"{col}:")
        print(f"  H1552: {df1[col].dtype} - 示例值: {df1[col].iloc[0]}")
        print(f"  H5179: {df2[col].dtype} - 示例值: {df2[col].iloc[0]}")