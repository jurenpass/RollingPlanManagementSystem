#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 py2exe 打包项目
"""

import os
import sys
from distutils.core import setup
import py2exe
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
    ('总计划号列表.xls', '.'),
    ('装炉顺序.xls', '.'),
    ('settings_window.ui', '.'),
    ('settings_window_ui.py', '.'),
    ('start.vbs', '.'),
    ('APS.txt', '.')
]

# 配置打包选项
options = {
    'py2exe': {
        'packages': ['pandas', 'xlrd', 'xlwt', 'xlutils', 'pyautogui', 'openpyxl', 'pynput', 'sqlite3', 'win32gui', 'win32con', 'win32api'],
        'bundle_files': 1,  # 打包成单个文件
        'compressed': True,  # 压缩文件
    }
}

# 执行打包
setup(
    name='轧制计划管理系统',
    version='1.0',
    description='宝钢股份多基地制造管理系统运行环境',
    options=options,
    windows=[{
        'script': 'furnace_order_manager_pyqt5.py',
        'dest_base': f'轧制计划管理系统_{current_time}',
    }],
    data_files=added_files,
    zipfile=None  # 不创建 zip 文件，将所有内容打包到 exe 中
)
