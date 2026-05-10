#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改：将刷新操作从 finally 块移到导出完成事件处理中
old_finally = """            finally:
                # 结束时间
                end_time = datetime.datetime.now()
                execution_time = end_time - start_time
                print(f"\\n=== 自动导出结束 ===")
                print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"执行时间: {execution_time.total_seconds():.2f} 秒")
                print("="*60)
                
                # 无论执行是否成功,都释放线程锁和重置运行标志
                if hasattr(self, 'auto_export_lock'):
                    try:
                        self.auto_export_lock.release()
                    except:
                        pass
                # 重置运行标志
                self.is_auto_export_running = False
                print("自动导出运行标志已重置为False")
                
                # 自动执行模式下，打开装炉明细画面并更新数据
                if not from_main_window:
                    # 自动执行完打开装炉明细画面，刷新数据而不关闭窗口
                    print("10秒后刷新装炉明细窗口数据...")
                    # 直接在单独的线程中刷新装炉明细窗口数据，避免事件循环冲突
                    import threading
                    def refresh_furnace_details():
                        # 延迟10秒执行
                        import time
                        time.sleep(10)
                        # 先检查是否已有装炉明细窗口
                        from PyQt5.QtWidgets import QApplication
                        existing_furnace_details = []
                        for widget in QApplication.topLevelWidgets():
                            if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                                existing_furnace_details.append(widget)

                        if existing_furnace_details:
                            # 如果有装炉明细窗口，刷新数据而不关闭
                            for widget in existing_furnace_details:
                                print(f"刷新装炉明细窗口数据")
                                # 调用刷新方法
                                if hasattr(widget, 'refresh_data'):
                                    widget.refresh_data()
                                # 激活窗口
                                widget.activateWindow()
                                widget.raise_()
                                widget.show()
                            print("装炉明细窗口数据已刷新")
                        else:
                            # 如果没有装炉明细窗口，打开新的
                            print("未找到装炉明细窗口，打开新的装炉明细画面")
                            try:
                                self.open_furnace_details()
                                print("成功打开装炉明细窗口")
                            except Exception as e:
                                print(f"打开装炉明细窗口失败: {str(e)}")
                    # 启动新线程
                    threading.Thread(target=refresh_furnace_details, daemon=True).start()
        
        # 启动后台线程执行导出操作"""

new_finally = """            finally:
                # 结束时间
                end_time = datetime.datetime.now()
                execution_time = end_time - start_time
                print(f"\\n=== 自动导出结束 ===")
                print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"执行时间: {execution_time.total_seconds():.2f} 秒")
                print("="*60)
                
                # 无论执行是否成功,都释放线程锁和重置运行标志
                if hasattr(self, 'auto_export_lock'):
                    try:
                        self.auto_export_lock.release()
                    except:
                        pass
                # 重置运行标志
                self.is_auto_export_running = False
                print("自动导出运行标志已重置为False")
        
        # 启动后台线程执行导出操作"""

content = content.replace(old_finally, new_finally)

# 修改导出完成事件处理，在完成后启动刷新装炉明细的线程
old_finished = """                    # 发送事件到主线程
                    finished_event = FinishedEvent(True, f"自动导出全部完成\\n\\n成功导出 {len(exported_plans)} 个计划号\\n失败 {len(failed_plans)} 个计划号", exported_plans, failed_plans, coord_map)
                    QCoreApplication.postEvent(self, finished_event)"""

new_finished = """                    # 发送事件到主线程
                    finished_event = FinishedEvent(True, f"自动导出全部完成\\n\\n成功导出 {len(exported_plans)} 个计划号\\n失败 {len(failed_plans)} 个计划号", exported_plans, failed_plans, coord_map)
                    QCoreApplication.postEvent(self, finished_event)

                    # 自动执行模式下，导出完成后打开装炉明细画面并更新数据
                    if not from_main_window:
                        # 导出完成后打开装炉明细画面，刷新数据而不关闭窗口
                        print("10秒后刷新装炉明细窗口数据...")
                        # 直接在单独的线程中刷新装炉明细窗口数据，避免事件循环冲突
                        import threading
                        def refresh_furnace_details():
                            # 延迟10秒执行
                            import time
                            time.sleep(10)
                            # 先检查是否已有装炉明细窗口
                            from PyQt5.QtWidgets import QApplication
                            existing_furnace_details = []
                            for widget in QApplication.topLevelWidgets():
                                if hasattr(widget, 'windowTitle') and '装炉明细' in widget.windowTitle():
                                    existing_furnace_details.append(widget)

                            if existing_furnace_details:
                                # 如果有装炉明细窗口，刷新数据而不关闭
                                for widget in existing_furnace_details:
                                    print(f"刷新装炉明细窗口数据")
                                    # 调用刷新方法
                                    if hasattr(widget, 'refresh_data'):
                                        widget.refresh_data()
                                    # 激活窗口
                                    widget.activateWindow()
                                    widget.raise_()
                                    widget.show()
                                print("装炉明细窗口数据已刷新")
                            else:
                                # 如果没有装炉明细窗口，打开新的
                                print("未找到装炉明细窗口，打开新的装炉明细画面")
                                try:
                                    self.open_furnace_details()
                                    print("成功打开装炉明细窗口")
                                except Exception as e:
                                    print(f"打开装炉明细窗口失败: {str(e)}")
                        # 启动新线程
                        threading.Thread(target=refresh_furnace_details, daemon=True).start()"""

content = content.replace(old_finished, new_finished)

with open('g:/newplan/furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('修改完成')
