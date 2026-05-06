#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试窗口激活功能
"""

import win32gui
import win32con
import time
import pyautogui

def test_activate_window(window_title):
    """测试激活窗口"""
    print(f"=== 测试激活窗口: {window_title} ===")
    
    # 查找窗口
    def callback(hwnd, handles):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_title in window_text:
                print(f"找到窗口: {window_text}")
                handles.append(hwnd)
    
    handles = []
    win32gui.EnumWindows(callback, handles)
    
    if not handles:
        print("未找到窗口")
        return False
    
    hwnd = handles[0]
    print(f"窗口句柄: {hwnd}")
    print(f"窗口标题: {win32gui.GetWindowText(hwnd)}")
    print(f"窗口可见: {win32gui.IsWindowVisible(hwnd)}")
    print(f"窗口最小化: {win32gui.IsIconic(hwnd)}")
    
    # 恢复窗口（如果最小化）
    if win32gui.IsIconic(hwnd):
        print("窗口被最小化，正在恢复...")
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)
    
    # 尝试多种方法激活窗口
    methods = [
        ("ShowWindow", lambda: win32gui.ShowWindow(hwnd, win32con.SW_SHOW)),
        ("SetWindowPos(TOPMOST)", lambda: win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)),
        ("SetWindowPos(NOTOPMOST)", lambda: win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)),
        ("SetForegroundWindow", lambda: win32gui.SetForegroundWindow(hwnd)),
        ("SetActiveWindow", lambda: win32gui.SetActiveWindow(hwnd)),
        ("SetFocus", lambda: win32gui.SetFocus(hwnd)),
        ("BringWindowToTop", lambda: win32gui.BringWindowToTop(hwnd)),
    ]
    
    success = False
    for method_name, method in methods:
        try:
            method()
            print(f"✓ {method_name} 成功")
            success = True
        except Exception as e:
            print(f"✗ {method_name} 失败: {str(e)}")
        time.sleep(0.2)
    
    # 尝试使用 pyautogui 点击窗口
    if not success:
        try:
            print("尝试使用 pyautogui 点击窗口...")
            rect = win32gui.GetWindowRect(hwnd)
            print(f"窗口矩形: {rect}")
            x = (rect[0] + rect[2]) // 2
            y = (rect[1] + rect[3]) // 2
            print(f"点击坐标: ({x}, {y})")
            pyautogui.click(x, y)
            print("✓ pyautogui 点击成功")
            success = True
        except Exception as e:
            print(f"✗ pyautogui 点击失败: {str(e)}")
    
    # 检查最终状态
    if success:
        print("窗口激活成功")
        # 验证窗口是否在前台
        foreground_hwnd = win32gui.GetForegroundWindow()
        print(f"当前前台窗口: {win32gui.GetWindowText(foreground_hwnd)}")
        print(f"是否为目标窗口: {foreground_hwnd == hwnd}")
    else:
        print("窗口激活失败")
    
    return success

if __name__ == "__main__":
    # 测试激活宝钢股份多基地制造管理系统窗口
    window_title = "BCMS1-宝钢股份多基地制造管理系统运行环境"
    test_activate_window(window_title)
    
    # 测试激活当前窗口
    print("\n=== 测试完成 ===")
