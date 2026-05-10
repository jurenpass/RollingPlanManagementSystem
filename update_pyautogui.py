#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改1: 在 pyautogui 导入后添加设置
old_pyautogui_import = """            # 检查pyautogui是否可用
            try:
                import pyautogui
                PYAUTOGUI_AVAILABLE = True
            except ImportError as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log('pyautogui 不可用,无法执行计划明细导出')
                print(f'pyautogui 不可用,无法执行计划明细导出: {e}')
                result = False
                return result
            except Exception as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log(f'pyautogui 初始化失败: {e}')
                print(f'pyautogui 初始化失败: {e}')
                result = False
                return result"""

new_pyautogui_import = """            # 检查pyautogui是否可用
            try:
                import pyautogui
                # 禁用 pyautogui 的自动暂停机制，避免操作卡住
                pyautogui.PAUSE = 0
                # 禁用 failsafe，避免误触导致程序停止
                pyautogui.FAILSAFE = False
                PYAUTOGUI_AVAILABLE = True
            except ImportError as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log('pyautogui 不可用,无法执行计划明细导出')
                print(f'pyautogui 不可用,无法执行计划明细导出: {e}')
                result = False
                return result
            except Exception as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log(f'pyautogui 初始化失败: {e}')
                print(f'pyautogui 初始化失败: {e}')
                result = False
                return result"""

content = content.replace(old_pyautogui_import, new_pyautogui_import)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
