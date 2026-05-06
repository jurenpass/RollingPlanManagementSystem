# -*- coding: utf-8 -*-

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除 pywin32 纸张设置代码（保存时的设置）
old_text = """        finally:
            # 释放资源
            if hasattr(workbook, 'release_resources'):
                workbook.release_resources()
        
        # 11. 使用 pywin32 设置纸张大小（确保生效）
        try:
            import win32com.client as win32
            print("[纸张设置] 尝试使用 pywin32 设置纸张大小...")
            
            # 创建 Excel 应用程序实例
            excel = win32.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False  # 禁用警告
            
            # 打开文件
            workbook_obj = excel.Workbooks.Open(new_file_path)
            ws = workbook_obj.ActiveSheet
            
            # 强制使用 xlPaperFanfoldUS (137) - 美国连续折叠纸
            preferred_size = 137  # xlPaperFanfoldUS
            
            # 尝试设置首选纸张
            try:
                ws.PageSetup.PaperSize = preferred_size
                print(f"[纸张设置] ✓ 成功设置纸张：FanfoldUS (14.875 x 11 inch)")
            except Exception as e:
                print(f"[纸张设置] ✗ 首选纸张设置失败：{str(e)}")
                # 尝试备选纸张
                fallback_papers = [39, 118, 119, 1, 9]
                for paper_code in fallback_papers:
                    if paper_code == preferred_size:
                        continue
                    try:
                        ws.PageSetup.PaperSize = paper_code
                        print(f"[纸张设置] ✓ 成功设置备选纸张：{paper_code}")
                        break
                    except Exception as e:
                        print(f"[纸张设置] ✗ 备选纸张 {paper_code} 设置失败：{str(e)}")
                        continue
            
            # 设置页边距为 0
            try:
                ws.PageSetup.TopMargin = 0.0
                ws.PageSetup.BottomMargin = 0.0
                ws.PageSetup.LeftMargin = 0.0
                ws.PageSetup.RightMargin = 0.0
                print("[纸张设置] ✓ 页边距设置为 0")
            except Exception as e:
                print(f"[纸张设置] ✗ 页边距设置失败：{str(e)}")
            
            # 设置页眉页脚为空
            ws.PageSetup.LeftHeader = ""
            ws.PageSetup.CenterHeader = ""
            ws.PageSetup.RightHeader = ""
            ws.PageSetup.LeftFooter = ""
            ws.PageSetup.CenterFooter = ""
            ws.PageSetup.RightFooter = ""
            
            # 保存并关闭
            workbook_obj.Save()
            workbook_obj.Close()
            excel.Quit()
            print("[纸张设置] ✓ pywin32 设置完成")
        except ImportError:
            print("[纸张设置] pywin32 未安装，跳过纸张大小设置")
        except Exception as e:
            print(f"[纸张设置] pywin32 设置失败：{str(e)}")
        
        return has_low_roll_width"""

new_text = """        finally:
            # 释放资源
            if hasattr(workbook, 'release_resources'):
                workbook.release_resources()
        
        return has_low_roll_width"""

content = content.replace(old_text, new_text)

with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已删除保存时的 pywin32 纸张设置代码，保留打印时的设置")
