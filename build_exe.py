#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本，按日期生成exe文件，并包含必要的配置文件
"""

import os
import shutil
import datetime
import subprocess

# 获取当前日期时间
current_datetime = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# 项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

# 配置文件路径
aps_file = os.path.join(project_root, 'APS.txt')
export_coordinates_file = os.path.join(project_root, 'export_coordinates.json')
settings_file = os.path.join(project_root, 'settings.json')
default_settings_file = os.path.join(project_root, 'default_settings.json')
db_file = os.path.join(project_root, 'furnace_order.db')
annotation_file = os.path.join(project_root, 'annotation_conditions.json')
settings_ui_file = os.path.join(project_root, 'settings_window.ui')
settings_ui_py_file = os.path.join(project_root, 'settings_window_ui.py')
start_vbs_file = os.path.join(project_root, 'start.vbs')

# 检查配置文件是否存在
required_files = [
    (aps_file, 'APS.txt'),
    (export_coordinates_file, 'export_coordinates.json'),
    (settings_file, 'settings.json'),
    (default_settings_file, 'default_settings.json'),
    (db_file, 'furnace_order.db'),
    (annotation_file, 'annotation_conditions.json'),
    (settings_ui_file, 'settings_window.ui'),
    (settings_ui_py_file, 'settings_window_ui.py'),
    (start_vbs_file, 'start.vbs')
]

for file_path, file_name in required_files:
    if not os.path.exists(file_path):
        print(f"警告: {file_name} 文件不存在")

# 生成输出文件名
output_name = f"轧制计划管理系统_{current_datetime}"
output_dir = os.path.join(project_root, 'dist')

# 清理之前的打包文件
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
    print(f"已清理之前的打包目录: {output_dir}")

# 构建PyInstaller命令
cmd = [
    'pyinstaller',
    '--name', output_name,
    '--onefile',
    '--windowed',
    '--add-data', f"{aps_file};.",
    '--add-data', f"{export_coordinates_file};.",
    '--add-data', f"{settings_file};.",
    '--add-data', f"{default_settings_file};.",
    '--add-data', f"{db_file};.",
    '--add-data', f"{annotation_file};.",
    '--add-data', f"{settings_ui_file};.",
    '--add-data', f"{settings_ui_py_file};.",
    '--add-data', f"{start_vbs_file};.",
    '--hidden-import', 'pandas',
    '--hidden-import', 'xlrd',
    '--hidden-import', 'xlwt',
    '--hidden-import', 'xlutils',
    '--hidden-import', 'pyautogui',
    '--hidden-import', 'openpyxl',
    '--hidden-import', 'psutil',
    '--hidden-import', 'win32gui',
    '--hidden-import', 'win32con',
    '--hidden-import', 'win32api',
    '--hidden-import', 'win32process',
    '--hidden-import', 'win32com.client',
    '--hidden-import', 'sqlite3',
    'furnace_order_manager_pyqt5.py'
]

print(f"开始打包，输出文件名: {output_name}.exe")
print(f"命令: {' '.join(cmd)}")

# 执行打包命令
try:
    subprocess.run(cmd, cwd=project_root, check=True)
    print("打包成功!")
    
    # 显示生成的文件路径
    exe_path = os.path.join(output_dir, f"{output_name}.exe")
    if os.path.exists(exe_path):
        print(f"生成的exe文件: {exe_path}")
    else:
        print("警告: 未找到生成的exe文件")
        
        # 检查dist目录
        if os.path.exists(output_dir):
            print("dist目录内容:")
            for file in os.listdir(output_dir):
                print(f"  - {file}")
        
    print("打包完成!")
    
except subprocess.CalledProcessError as e:
    print(f"打包失败: {e}")
    exit(1)
except Exception as e:
    print(f"打包过程中发生错误: {e}")
    import traceback
    traceback.print_exc()
    exit(1)