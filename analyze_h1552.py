import pandas as pd
import os

file_path = r'g:\newplan\计划号\H1552.xls'

print("=" * 60)
print("H1552.xls 文件分析")
print("=" * 60)

# 检查文件是否存在
if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
else:
    print(f"✅ 文件存在: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path)} bytes")
    print()

    # 尝试读取文件
    try:
        # 尝试使用xlrd读取
        df = pd.read_excel(file_path, engine='xlrd')
        print("✅ 成功使用xlrd引擎读取文件")
        print()
        print("=" * 60)
        print("文件列名：")
        print("=" * 60)
        print(list(df.columns))
        print()
        print("=" * 60)
        print("数据前5行：")
        print("=" * 60)
        print(df.head())
        print()
        print("=" * 60)
        print("数据形状：")
        print("=" * 60)
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print()

        # 检查是否有空列
        empty_cols = df.columns[df.isna().all()].tolist()
        if empty_cols:
            print("⚠️  完全为空的列：")
            print(empty_cols)
            print()

        # 检查数据类型
        print("=" * 60)
        print("列数据类型：")
        print("=" * 60)
        print(df.dtypes)

    except Exception as e:
        print(f"❌ 使用xlrd读取失败: {e}")
        print()

        # 尝试其他方法
        try:
            # 尝试使用openpyxl读取（针对.xlsx）
            df = pd.read_excel(file_path, engine='openpyxl')
            print("✅ 成功使用openpyxl引擎读取文件（可能是.xlsx格式）")
            print()
            print("=" * 60)
            print("文件列名：")
            print("=" * 60)
            print(list(df.columns))
        except Exception as e2:
            print(f"❌ 使用openpyxl也失败: {e2}")
            print()

            # 检查文件头
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(20)
                    print("=" * 60)
                    print("文件头（HEX）：")
                    print("=" * 60)
                    print(header.hex())
                    print()

                    # 判断文件类型
                    if header.startswith(b'\xd0\xcf\x11\xe0'):
                        print("📄 文件类型: OLE2格式（可能是旧版Excel .xls）")
                    elif header.startswith(b'PK'):
                        print("📄 文件类型: ZIP格式（可能是新版Excel .xlsx）")
                    elif header.startswith(b'\xff\xd8\xff'):
                        print("📷 文件类型: JPEG图片")
                    else:
                        print("📄 文件类型: 未知")
            except Exception as e3:
                print(f"❌ 无法读取文件头: {e3}")

print()
print("=" * 60)
print("分析完成")
print("=" * 60)