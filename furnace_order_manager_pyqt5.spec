# -*- mode: python ; coding: utf-8 -*-

import datetime

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# 收集所有必要的文件和目录
added_files = [
    ('settings.json', '.'),
    ('default_settings.json', '.'),
    ('export_coordinates.json', '.'),
    ('export_coordinates_default.json', '.'),
    ('furnace_order.db', '.'),
    ('annotation_conditions.json', '.'),
    ('总计划号列表.xls', '计划号'),
    ('装炉顺序.xls', '计划号'),
    ('settings_window.ui', '.'),
    ('settings_window_ui.py', '.'),
    ('start.vbs', '.'),
    ('APS.txt', '.')
]

# 收集 pywin32 的二进制文件
import sysconfig
import os
site_packages = sysconfig.get_paths()['purelib']
pywin32_path = os.path.join(site_packages, 'win32')

# 添加 pywin32 的二进制文件
pywin32_binaries = []
if os.path.exists(pywin32_path):
    for file in os.listdir(pywin32_path):
        if file.endswith('.pyd') or file.endswith('.dll'):
            pywin32_binaries.append((os.path.join(pywin32_path, file), 'win32'))

# 添加 pywin32com 的二进制文件
pywin32com_path = os.path.join(site_packages, 'win32com')
if os.path.exists(pywin32com_path):
    for file in os.listdir(pywin32com_path):
        if file.endswith('.pyd') or file.endswith('.dll'):
            pywin32_binaries.append((os.path.join(pywin32com_path, file), 'win32com'))

# 添加 pywin32com.genpy 的二进制文件
pywin32com_genpy_path = os.path.join(site_packages, 'win32com', 'genpy')
if os.path.exists(pywin32com_genpy_path):
    for file in os.listdir(pywin32com_genpy_path):
        if file.endswith('.pyd') or file.endswith('.dll'):
            pywin32_binaries.append((os.path.join(pywin32com_genpy_path, file), 'win32com/genpy'))

a = Analysis(
    ['furnace_order_manager_pyqt5.py'],
    pathex=[],
    binaries=pywin32_binaries,
    datas=added_files,
    hiddenimports=['pandas', 'xlrd', 'xlwt', 'xlutils', 'pyautogui', 'pyscreeze', 'pygetwindow', 'pymsgbox', 'pytweening', 'mouseinfo', 'pyperclip', 'pyrect', 'openpyxl', 'pynput', 'sqlite3', 'win32gui', 'win32con', 'win32api', 'win32process', 'win32com', 'win32com.client', 'win32com.shell', 'psutil', 'shutil', 'math', 'json', 'time', 'datetime', 'traceback', 'subprocess', 'threading'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'轧制计划管理系统_修复版_{current_time}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)