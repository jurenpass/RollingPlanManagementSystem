# 读取文件
with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 在第5885行之后插入代码（行号从0开始）
insert_position = 5884  # 在第5885行之后插入

insert_code = '''            # 确保所有Excel进程都已关闭（避免文件占用）
            add_debug_log(f"")
            add_debug_log(f"【关闭Excel进程】")
            try:
                import subprocess
                # 强制关闭所有Excel进程
                subprocess.run(
                    ['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                add_debug_log(f"  延迟: 2000ms")
                time.sleep(2)
                print("[√] Excel进程已强制关闭")
                add_debug_log("[√] Excel进程已强制关闭")
            except Exception as e:
                print(f"[×] 强制关闭Excel进程失败: {str(e)}")
                add_debug_log(f"[×] 强制关闭Excel进程失败: {str(e)}")
            
            # 原子性文件替换：将临时文件替换为正式文件（添加.xls扩展名）
            add_debug_log(f"")
            add_debug_log(f"【原子性文件替换】")
            try:
                # 临时文件实际保存时会自动添加.xls扩展名
                temp_zhizhi_file_with_ext = temp_total_plan_file + ".xls"
                add_debug_log(f"  临时文件: {temp_zhizhi_file_with_ext}")
                add_debug_log(f"  目标文件: {total_plan_file}")
                
                if os.path.exists(temp_zhizhi_file_with_ext):
                    # 执行原子性替换,使用重试机制
                    success = self.atomic_file_replace(temp_zhizhi_file_with_ext, total_plan_file, max_retries=5, retry_delay=1.0)
                    if success:
                        # 清理文件缓存,确保读取到最新数据
                        self.clear_file_cache(total_plan_file)
                        print("[√] 原子性文件替换成功")
                        add_debug_log("[√] 原子性文件替换成功")
                        add_debug_log("[√] 文件缓存已清理")
                    else:
                        print("[×] 原子性文件替换失败")
                        add_debug_log("[×] 原子性文件替换失败")
                else:
                    # 尝试不带扩展名的临时文件
                    if os.path.exists(temp_total_plan_file):
                        temp_zhizhi_file_with_ext = temp_total_plan_file
                        add_debug_log(f"  尝试不带扩展名的临时文件: {temp_zhizhi_file_with_ext}")
                        success = self.atomic_file_replace(temp_zhizhi_file_with_ext, total_plan_file, max_retries=5, retry_delay=1.0)
                        if success:
                            self.clear_file_cache(total_plan_file)
                            print("[√] 原子性文件替换成功")
                            add_debug_log("[√] 原子性文件替换成功")
                        else:
                            print("[×] 原子性文件替换失败")
                            add_debug_log("[×] 原子性文件替换失败")
                    else:
                        print(f"[×] 临时文件不存在: {temp_total_plan_file}")
                        add_debug_log(f"[×] 临时文件不存在: {temp_total_plan_file}")
            except Exception as e:
                print(f"[×] 原子性文件替换异常: {str(e)}")
                add_debug_log(f"[×] 原子性文件替换异常: {str(e)}")
'''

# 将代码拆分为行
insert_lines = [line + '\n' for line in insert_code.split('\n')]

# 在指定位置插入代码
lines[insert_position:insert_position] = insert_lines

# 写入文件
with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('修改完成')
