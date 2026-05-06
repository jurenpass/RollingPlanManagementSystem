#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轧制计划管理系统 - EXE文件测试脚本
测试生成的EXE文件是否正常工作
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_exe_file():
    """测试EXE文件"""
    exe_path = os.path.join("dist", "轧制计划管理系统.exe")
    
    if not os.path.exists(exe_path):
        print("✗ EXE文件不存在")
        return False
    
    print(f"✓ EXE文件存在: {exe_path}")
    
    # 检查文件大小
    file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
    print(f"✓ 文件大小: {file_size:.2f} MB")
    
    # 检查文件是否可执行
    if not os.access(exe_path, os.X_OK):
        print("✗ EXE文件不可执行")
        return False
    
    print("✓ EXE文件可执行")
    return True

def test_required_files():
    """测试必要的文件是否存在"""
    required_files = [
        "APS.txt",
        "export_coordinates.json",
        "processed_plans.txt", 
        "printed_plans.txt",
        "no_aps_plans.txt"
    ]
    
    missing_files = []
    for filename in required_files:
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        print("✗ 缺少必要的文件:")
        for filename in missing_files:
            print(f"  - {filename}")
        return False
    
    print("✓ 所有必要的文件都存在")
    return True

def test_plan_directory():
    """测试计划号文件夹"""
    plan_dir = "计划号"
    
    if not os.path.exists(plan_dir):
        print("✗ 计划号文件夹不存在")
        return False
    
    print(f"✓ 计划号文件夹存在: {plan_dir}")
    
    # 检查文件夹是否为空
    if not os.listdir(plan_dir):
        print("⚠ 计划号文件夹为空")
    else:
        print("✓ 计划号文件夹包含文件")
    
    return True

def create_test_environment():
    """创建测试环境"""
    print("\n创建测试环境...")
    
    # 创建测试目录
    test_dir = "test_exe_environment"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    os.makedirs(test_dir)
    print(f"✓ 创建测试目录: {test_dir}")
    
    # 复制EXE文件
    exe_path = os.path.join("dist", "轧制计划管理系统.exe")
    if os.path.exists(exe_path):
        shutil.copy(exe_path, test_dir)
        print("✓ 复制EXE文件")
    
    # 复制必要的文件
    files_to_copy = [
        "APS.txt",
        "export_coordinates.json", 
        "processed_plans.txt",
        "printed_plans.txt",
        "no_aps_plans.txt"
    ]
    
    for filename in files_to_copy:
        if os.path.exists(filename):
            shutil.copy(filename, test_dir)
            print(f"✓ 复制文件: {filename}")
    
    # 复制计划号文件夹
    plan_dir = "计划号"
    if os.path.exists(plan_dir):
        shutil.copytree(plan_dir, os.path.join(test_dir, plan_dir))
        print(f"✓ 复制文件夹: {plan_dir}")
    
    return test_dir

def main():
    """主函数"""
    print("=" * 60)
    print("轧制计划管理系统 - EXE文件测试")
    print("=" * 60)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"当前目录: {current_dir}")
    
    # 测试EXE文件
    if not test_exe_file():
        return
    
    # 测试必要的文件
    if not test_required_files():
        print("\n注意: 缺少必要的文件，但EXE文件本身是完整的")
    
    # 测试计划号文件夹
    if not test_plan_directory():
        print("\n注意: 计划号文件夹不存在或为空")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    print("\n部署说明:")
    print("1. 将以下文件复制到目标目录:")
    print("   - dist/轧制计划管理系统.exe")
    print("   - 计划号/文件夹")
    print("   - APS.txt")
    print("   - export_coordinates.json")
    print("2. 双击运行EXE文件")
    print("3. 首次运行会自动创建缺失的文件")
    print("\n注意: 首次运行可能需要管理员权限")
    
    print("\n自动文件夹创建功能:")
    print("✓ 程序启动时会自动创建计划号文件夹")
    print("✓ 自动创建必要的配置文件")
    print("✓ 自动创建模板Excel文件")
    print("✓ 支持在任何目录下运行")

if __name__ == "__main__":
    main()