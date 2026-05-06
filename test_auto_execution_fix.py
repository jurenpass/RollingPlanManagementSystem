#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动执行功能修复效果
"""

import time
import threading
import datetime

class TestAutoExecution:
    def __init__(self):
        self.is_auto_exec_running = False
        self.auto_exec_timer = None
        self.last_executed_datetime = None
        self.interval_target_execution_time = None
        self.auto_exec_interval = 5  # 5秒间隔，方便测试
    
    def calculate_next_execution_time(self):
        """计算下一次执行时间"""
        if self.interval_target_execution_time is not None:
            next_time = self.interval_target_execution_time
        else:
            next_time = time.time() + self.auto_exec_interval
            self.interval_target_execution_time = next_time
        return time.strftime("%H:%M:%S", time.localtime(next_time))
    
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
        self.interval_target_execution_time = time.time() + self.auto_exec_interval
        print(f"初始化目标执行时间: {datetime.datetime.fromtimestamp(self.interval_target_execution_time).strftime('%H:%M:%S')}")
        
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
                wait_time = self.interval_target_execution_time - time.time()
                target_time = datetime.datetime.fromtimestamp(self.interval_target_execution_time)
                print(f"等待 {wait_time:.0f} 秒后执行...")
                
                # 分小段等待
                while wait_time > 0 and self.is_auto_exec_running:
                    wait_chunk = min(wait_time, 1)
                    time.sleep(wait_chunk)
                    wait_time -= wait_chunk
                
                if not self.is_auto_exec_running:
                    break
                
                # 检查是否到达目标时间
                now = datetime.datetime.now()
                current_time = time.time()
                
                if current_time >= self.interval_target_execution_time:
                    print(f"执行时间到达，当前时间: {now.strftime('%H:%M:%S')}，目标时间: {target_time.strftime('%H:%M:%S')}")
                    
                    # 检查是否最近执行过
                    if self.last_executed_datetime is None or (now - self.last_executed_datetime).total_seconds() > 5:
                        print("执行自动导出...")
                        self.last_executed_datetime = now
                        self.auto_export()
                        
                        # 重新计算下一次执行时间
                        self.interval_target_execution_time = time.time() + self.auto_exec_interval
                        print(f"重新计算下一次目标执行时间: {datetime.datetime.fromtimestamp(self.interval_target_execution_time).strftime('%H:%M:%S')}")
                    else:
                        print("最近已执行过，跳过")
                else:
                    print(f"时间未到达，当前时间: {now.strftime('%H:%M:%S')}，目标时间: {target_time.strftime('%H:%M:%S')}")
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
    test = TestAutoExecution()
    test.start_auto_execution()
    
    # 运行15秒后停止
    print("测试运行15秒...")
    time.sleep(15)
    test.stop_auto_execution()
    print("测试完成")
