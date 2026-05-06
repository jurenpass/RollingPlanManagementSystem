#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试指定时间执行功能
"""

import time
import threading
import datetime

class TestTimeModeExecution:
    def __init__(self):
        self.is_auto_exec_running = False
        self.auto_exec_timer = None
        self.last_executed_datetime = None
        self.time_mode_target_execution_time = None
        self.auto_exec_times = "15:21,15:22"  # 测试时间
    
    def calculate_next_execution_time(self):
        """计算下一次执行时间"""
        exec_times = self.auto_exec_times.strip()
        if exec_times:
            # 解析时间
            times = [t.strip() for t in exec_times.split(',')]
            valid_times = []
            for t in times:
                if len(t) == 5 and t[2] == ':':
                    try:
                        hour = int(t[:2])
                        minute = int(t[3:])
                        if 0 <= hour < 24 and 0 <= minute < 60:
                            valid_times.append((hour, minute))
                    except:
                        pass
            
            if valid_times:
                # 获取当前系统时间
                now = time.localtime()
                current_hour = now.tm_hour
                current_minute = now.tm_min
                current_second = now.tm_sec
                
                # 找到下一个执行时间
                next_exec_time = None
                min_time_diff = float('inf')
                target_hour = 0
                target_minute = 0
                
                for hour, minute in valid_times:
                    # 计算时间差（秒）
                    time_diff = (hour - current_hour) * 3600 + (minute - current_minute) * 60 - current_second
                    if time_diff <= 0:
                        # 今天的时间已经过了，使用明天的时间
                        time_diff += 24 * 3600
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        next_exec_time = (hour, minute)
                        target_hour = hour
                        target_minute = minute
                
                if next_exec_time:
                    # 构造下一次执行时间
                    today = datetime.date.today()
                    target_time = datetime.datetime(today.year, today.month, today.day, target_hour, target_minute, current_second)
                    # 如果目标时间已过，使用明天的日期
                    if target_time < datetime.datetime.now():
                        target_time += datetime.timedelta(days=1)
                    # 格式化时间
                    next_time_str = target_time.strftime("%H:%M:%S")
                    return next_time_str
        return "无"
    
    def auto_export(self):
        """模拟自动导出"""
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 执行自动导出...")
        time.sleep(2)  # 模拟导出过程
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] 自动导出完成")
    
    def start_auto_execution(self):
        """启动自动执行服务"""
        print("启动自动执行服务...")
        
        # 停止现有服务
        if self.is_auto_exec_running:
            self.is_auto_exec_running = False
            if self.auto_exec_timer:
                self.auto_exec_timer.join(timeout=2)
                self.auto_exec_timer = None
        
        # 初始化目标执行时间
        next_time_str = self.calculate_next_execution_time()
        if next_time_str and next_time_str != "无":
            try:
                # 解析时间字符串
                target_hour, target_minute, target_second = map(int, next_time_str.split(':'))
                # 构造目标时间
                now = datetime.datetime.now()
                target_time = datetime.datetime(now.year, now.month, now.day, target_hour, target_minute, target_second)
                # 如果目标时间已过，使用明天的日期
                if target_time < now:
                    target_time += datetime.timedelta(days=1)
                # 转换为时间戳并存储
                self.time_mode_target_execution_time = target_time.timestamp()
                print(f"初始化指定时间模式目标执行时间: {target_time.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"初始化指定时间模式目标执行时间失败: {e}")
        
        # 启动新服务
        self.is_auto_exec_running = True
        self.auto_exec_timer = threading.Thread(target=self.auto_execution_function, daemon=True)
        self.auto_exec_timer.start()
        print("自动执行服务已启动")
    
    def auto_execution_function(self):
        """自动执行服务函数"""
        print("自动执行服务线程已启动")
        
        while self.is_auto_exec_running:
            try:
                # 计算下一次执行时间
                next_exec_time_str = self.calculate_next_execution_time()
                print(f"下一次执行时间: {next_exec_time_str}")
                
                # 计算等待时间
                now = datetime.datetime.now()
                if hasattr(self, 'time_mode_target_execution_time') and self.time_mode_target_execution_time is not None:
                    wait_time = self.time_mode_target_execution_time - time.time()
                    target_time = datetime.datetime.fromtimestamp(self.time_mode_target_execution_time)
                    print(f"等待 {wait_time:.0f} 秒后执行...")
                    
                    # 分小段等待
                    while wait_time > 0 and self.is_auto_exec_running:
                        wait_chunk = min(wait_time, 1)
                        time.sleep(wait_chunk)
                        wait_time -= wait_chunk
                    
                    if not self.is_auto_exec_running:
                        break
                    
                    # 检查是否到达目标时间
                    current_time = time.time()
                    if current_time >= self.time_mode_target_execution_time:
                        print(f"执行时间到达，当前时间: {now.strftime('%H:%M:%S')}，目标时间: {target_time.strftime('%H:%M:%S')}")
                        
                        # 检查是否最近执行过
                        if self.last_executed_datetime is None or (now - self.last_executed_datetime).total_seconds() > 60:
                            print("执行自动导出...")
                            self.last_executed_datetime = now
                            self.auto_export()
                            
                            # 重新计算下一次执行时间
                            next_time_str = self.calculate_next_execution_time()
                            if next_time_str and next_time_str != "无":
                                try:
                                    # 解析时间字符串
                                    target_hour, target_minute, target_second = map(int, next_time_str.split(':'))
                                    # 构造目标时间
                                    now = datetime.datetime.now()
                                    target_time = datetime.datetime(now.year, now.month, now.day, target_hour, target_minute, target_second)
                                    # 如果目标时间已过，使用明天的日期
                                    if target_time < now:
                                        target_time += datetime.timedelta(days=1)
                                    # 转换为时间戳并存储
                                    self.time_mode_target_execution_time = target_time.timestamp()
                                    print(f"重新计算指定时间模式下一次目标执行时间: {target_time.strftime('%H:%M:%S')}")
                                except Exception as e:
                                    print(f"重新计算指定时间模式目标执行时间失败: {e}")
                        else:
                            print("最近已执行过，跳过")
                    else:
                        print(f"时间未到达，当前时间: {now.strftime('%H:%M:%S')}，目标时间: {target_time.strftime('%H:%M:%S')}")
                else:
                    print("没有有效的执行时间，等待1分钟后重新检查")
                    time.sleep(60)
            except Exception as e:
                print(f"自动执行服务错误: {e}")
                time.sleep(5)
    
    def stop_auto_execution(self):
        """停止自动执行服务"""
        print("停止自动执行服务...")
        self.is_auto_exec_running = False
        if self.auto_exec_timer:
            self.auto_exec_timer.join(timeout=2)
            self.auto_exec_timer = None
        print("自动执行服务已停止")

if __name__ == "__main__":
    test = TestTimeModeExecution()
    test.start_auto_execution()
    
    # 运行10分钟后停止
    print("测试运行10分钟...")
    time.sleep(600)
    test.stop_auto_execution()
    print("测试完成")
