#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出所有可见的窗口
"""

import win32gui

def list_windows():
    """列出所有可见的窗口"""
    print("=== 列出所有可见的窗口 ===")
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                windows.append((hwnd, window_text))
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    print(f"共找到 {len(windows)} 个可见窗口：")
    print("=" * 80)
    
    for hwnd, window_text in windows:
        print(f"{hwnd}: {window_text}")
    
    print("=" * 80)
    
    # 搜索包含"宝钢"的窗口
    print("\n=== 搜索包含'宝钢'的窗口 ===")
    found = False
    for hwnd, window_text in windows:
        if "宝钢" in window_text:
            print(f"{hwnd}: {window_text}")
            found = True
    
    if not found:
        print("未找到包含'宝钢'的窗口")

if __name__ == "__main__":
    list_windows()
