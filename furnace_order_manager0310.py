import tkinter as tk
from tkinter import ttk, messagebox
from collections import OrderedDict
import os
import warnings
import pandas as pd
import xlrd

# 隐藏xlrd警告
warnings.filterwarnings('ignore')

class FurnaceOrderManager:
    def __init__(self, root):
        self.root = root
        self.root.title("轧制计划管理系统")
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口大小并居中
        window_width = 1500
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建统一样式
        self.style = ttk.Style()
        self.style.configure('TButton', font=('宋体', 20))
        self.style.configure('TLabel', font=('宋体', 20))
        self.style.configure('TFrame', font=('宋体', 20))
        
        # 数据存储
        self.plan_data = []
        self.selected_items = set()
        
        # 自动导出相关配置
        self.plan_dir = os.path.dirname(os.path.abspath(__file__))  # 计划文件目录
        self.coordinates = self.load_coordinate_config()  # 加载坐标配置
        self.processed_plans = set()  # 已处理的计划号集合
        self.printed_plans = set()  # 已打印的计划号集合
        self.no_aps_plans = set()  # 包含无APS钢种的计划号集合
        
        # 总计划号列表缓存
        self.zhizhi_plan_list = []  # 存储序号和计划号信息：[(序号, 计划号), ...]
        self.zhizhi_plan_coord_map = {}  # 存储计划号到坐标的映射
        
        self.create_ui()
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_data()
    
    def create_ui(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="轧制计划管理系统", 
            font=("宋体", 20, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=15)
        
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        # 列表标题
        list_title = tk.Label(
            main_frame, 
            text="计划号列表", 
            font=("宋体", 20),
            bg='#f0f0f0',
            anchor='w'
        )
        list_title.pack(fill=tk.X, pady=(0, 5))
        
        # 创建列表框和滚动条
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 列表框
        self.listbox = tk.Listbox(
            list_frame,
            font=("宋体", 30),
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=1,
            width=50,
            height=8
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # 绑定选择事件
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # 统计信息
        self.stats_label = tk.Label(
            main_frame,
            text="总块数: 0",
            font=("宋体", 20),
            bg='#f0f0f0',
            fg='blue',
            anchor='w'
        )
        self.stats_label.pack(fill=tk.X, pady=10)
        
        # 按钮框架
        btn_frame = tk.Frame(self.root, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 左侧按钮框架
        left_btn_frame = tk.Frame(btn_frame, bg='#f0f0f0')
        left_btn_frame.pack(side=tk.LEFT)
        
        # 创建按钮（使用ttk统一样式）
        self.create_style_button(left_btn_frame, "全选", self.select_all, width=6)
        self.create_style_button(left_btn_frame, "取消全选", self.deselect_all, width=8)
        self.refresh_btn = self.create_style_button(left_btn_frame, "刷新", self.refresh_data, width=6, is_active=True)
        self.create_style_button(left_btn_frame, "自动导出", self.auto_export, width=8)
        self.create_style_button(left_btn_frame, "⚙ 设置", self.settings, width=8)
        self.create_style_button(left_btn_frame, "装炉明细", self.furnace_details, width=8)
        self.create_style_button(left_btn_frame, "处理计划", self.process_plans, width=8)
        # 右侧按钮框架
        right_btn_frame = tk.Frame(btn_frame, bg='#f0f0f0')
        right_btn_frame.pack(side=tk.RIGHT)
        
        self.create_style_button(right_btn_frame, "显示", self.show_selected, width=6)
        self.create_style_button(right_btn_frame, "打印", self.print_selected, width=6)
    
    def create_style_button(self, parent, text, command, width=6, is_active=False):
        """创建ttk风格按钮"""
        btn = ttk.Button(
            parent,
            text=text,
            command=command,
            width=width
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        return btn
    
    def custom_messagebox(self, title, message, msg_type='info'):
        """自定义消息框 - 更大的窗口和字体
        
        Args:
            title: 窗口标题
            message: 消息内容
            msg_type: 消息类型 ('info', 'warning', 'error', 'yesno')
            
        Returns:
            bool: 对于yesno类型，返回用户的选择
        """
        import tkinter as tk
        from tkinter import ttk
        
        # 创建自定义窗口
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.geometry("600x500")
        msg_window.resizable(True, True)
        
        # 计算居中位置
        screen_width = msg_window.winfo_screenwidth()
        screen_height = msg_window.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (500 // 2)
        msg_window.geometry(f"600x500+{x}+{y}")
        
        # 设置窗口样式
        msg_window.configure(bg='#f0f0f0')
        
        # 创建主框架
        main_frame = tk.Frame(msg_window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 消息内容
        message_label = tk.Label(
            main_frame,
            text=message,
            font=('宋体', 14),
            bg='#f0f0f0',
            justify=tk.LEFT,
            wraplength=550
        )
        message_label.pack(expand=True, fill=tk.BOTH)
        
        # 按钮框架
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(side=tk.BOTTOM, pady=20)
        
        if msg_type == 'yesno':
            # 是/否按钮
            self.user_choice = False
            
            def on_yes():
                self.user_choice = True
                msg_window.destroy()
            
            def on_no():
                self.user_choice = False
                msg_window.destroy()
            
            yes_btn = ttk.Button(
                btn_frame,
                text="是",
                command=on_yes,
                width=10
            )
            yes_btn.pack(side=tk.LEFT, padx=10)
            
            no_btn = ttk.Button(
                btn_frame,
                text="否",
                command=on_no,
                width=10
            )
            no_btn.pack(side=tk.LEFT, padx=10)
            
            # 确保主窗口和弹窗都到最前面
            try:
                self.root.lift()
                self.root.focus_force()
                print("主窗口已提升到前面")
            except Exception as e:
                print(f"提升主窗口失败: {e}")
            
            # 确保弹窗在最前面
            msg_window.transient(self.root)
            msg_window.grab_set()
            msg_window.lift()
            msg_window.focus_force()
            msg_window.wait_window()
            
            return self.user_choice
        else:
            # 确定按钮
            ok_btn = ttk.Button(
                btn_frame,
                text="确定",
                command=msg_window.destroy,
                width=10
            )
            ok_btn.pack()
            
            # 确保主窗口和弹窗都到最前面
            try:
                self.root.lift()
                self.root.focus_force()
                print("主窗口已提升到前面")
            except Exception as e:
                print(f"提升主窗口失败: {e}")
            
            # 确保弹窗在最前面
            msg_window.transient(self.root)
            msg_window.grab_set()
            msg_window.lift()
            msg_window.focus_force()
            msg_window.wait_window()
    
    def load_data(self):
        """加载Excel数据 - 调用刷新计划号列表方法"""
        # 重新加载已处理和已打印的状态
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_no_aps_plans()
        # 刷新计划号列表
        self.refresh_plan_list()
    
    def refresh_plan_list_from_file(self):
        """刷新计划号列表 - 从装炉顺序.xls读取数据，采用副本读取方案，避免文件占用问题
        
        此方法供以下场景使用：
        1. 启动主程序时加载数据
        2. 点击刷新按钮时
        3. 导出装炉顺序文件后更新列表
        
        Returns:
            bool: 是否成功加载数据
        """
        try:
            import os
            # 使用计划号文件夹中的装炉顺序.xls
            plan_dir = os.path.join(self.plan_dir, "计划号")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            if not os.path.exists(excel_file):
                self.custom_messagebox("错误", f"找不到文件: {excel_file}")
                return False
            
            import shutil
            import tempfile
            
            temp_file_path = None
            try:
                temp_file = tempfile.NamedTemporaryFile(suffix='.xls', delete=False)
                temp_file_path = temp_file.name
                temp_file.close()
                shutil.copy2(excel_file, temp_file_path)
                print(f"已创建临时副本: {temp_file_path}")
            except Exception as e:
                print(f"创建临时副本失败: {str(e)}")
                temp_file_path = excel_file
            
            try:
                import xlrd
                workbook = xlrd.open_workbook(temp_file_path)
                sheet = workbook.sheet_by_index(0)
                
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                
                plan_col_idx = None
                order_col_idx = None
                for idx, header in enumerate(headers):
                    if '计划号' in str(header):
                        plan_col_idx = idx
                    if '装炉顺序号' in str(header):
                        order_col_idx = idx
                
                if plan_col_idx is None:
                    self.custom_messagebox("错误", "找不到'计划号'列")
                    return False
                
                data_rows = []
                for row_idx in range(1, sheet.nrows):
                    plan_no = str(sheet.cell_value(row_idx, plan_col_idx)).strip()
                    order_no = sheet.cell_value(row_idx, order_col_idx) if order_col_idx else row_idx
                    try:
                        order_no = float(order_no)
                    except:
                        order_no = row_idx
                    
                    if plan_no and plan_no != 'nan':
                        data_rows.append((order_no, plan_no))
                
                data_rows.sort(key=lambda x: x[0])
                
                plan_counts = OrderedDict()
                for _, plan_no in data_rows:
                    if plan_no not in plan_counts:
                        plan_counts[plan_no] = 0
                    plan_counts[plan_no] += 1
                
                self.plan_data = []
                total_count = 0
                no_file_count = 0
                
                # 获取计划号文件夹中的所有xls文件
                plan_files = set()
                if os.path.exists(plan_dir):
                    for f in os.listdir(plan_dir):
                        if f.endswith('.xls') or f.endswith('.xlsx'):
                            # 去掉扩展名获取计划号
                            plan_no_from_file = os.path.splitext(f)[0]
                            plan_files.add(plan_no_from_file)
                
                print(f"计划号文件夹中找到 {len(plan_files)} 个文件")
                
                for plan_no, count in plan_counts.items():
                    # 检查是否有对应的文件
                    status = ''
                    if plan_no not in plan_files:
                        status = '无文件'
                        no_file_count += 1
                        print(f"计划号 {plan_no} 无对应文件")
                    
                    self.plan_data.append({
                        'plan_no': plan_no,
                        'count': count,
                        'status': status
                    })
                    total_count += count
                
                self.update_listbox()
                self.stats_label.config(text=f"总块数: {total_count} | 无文件: {no_file_count}")
                
                print(f"成功加载 {len(self.plan_data)} 个计划号，总计 {total_count} 块，无文件 {no_file_count} 个")
                return True
                
            except ImportError:
                self.custom_messagebox("错误", "请先安装xlrd库: pip install xlrd==1.2.0")
                return False
            finally:
                if temp_file_path and temp_file_path != excel_file:
                    try:
                        os.unlink(temp_file_path)
                        print(f"已删除临时副本: {temp_file_path}")
                    except:
                        pass
                
        except Exception as e:
            self.custom_messagebox("错误", f"加载数据失败: {str(e)}")
            return False
    
    def update_listbox(self):
        """更新列表框显示"""
        self.listbox.delete(0, tk.END)
        
        for item in self.plan_data:
            plan_no = item['plan_no']
            count = item['count']
            status = item['status']
            
            # 格式化显示 - 数字左对齐，块字右对齐
            display_text = f"{plan_no:<12} [{count:<3}块]"
            
            # 分开标注状态
            if status:
                display_text += f"  [{status}]"
            if plan_no in self.processed_plans:
                display_text += f"  [已处理]"
            if plan_no in self.printed_plans:
                display_text += f"  [已打印]"
            if plan_no in self.no_aps_plans:
                display_text += f"  [无APS]"
            
            self.listbox.insert(tk.END, display_text)
    
    def on_select(self, event):
        """选择事件处理"""
        selection = self.listbox.curselection()
        self.selected_items = set(selection)
    
    def select_all(self):
        """全选"""
        self.listbox.select_set(0, tk.END)
        self.selected_items = set(range(len(self.plan_data)))
    
    def deselect_all(self):
        """取消全选"""
        self.listbox.selection_clear(0, tk.END)
        self.selected_items.clear()
    
    def refresh_data(self):
        """刷新数据"""
        # 刷新计划号列表（load_data会自动加载状态）
        self.load_data()
    
    def auto_export(self):
        """自动导出"""
        import time
        import tkinter as tk
        from tkinter import messagebox
        try:
            import pyautogui
            PYAUTOGUI_AVAILABLE = True
        except ImportError:
            PYAUTOGUI_AVAILABLE = False
            self.custom_messagebox("错误", "pyautogui未安装，请先安装: pip install pyautogui")
            return
        
        # 显示操作提示（根据配置）
        show_warning = self.coordinates.get("show_operation_warning", True)
        if show_warning:
            warning_window = tk.Toplevel(self.root)
            warning_window.title("⚠️ 操作提示")
            
            window_width = 500
            window_height = 350
            screen_width = warning_window.winfo_screenwidth()
            screen_height = warning_window.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            warning_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            warning_window.transient(self.root)
            warning_window.grab_set()
            warning_window.resizable(False, False)
            
            title_label = tk.Label(
                warning_window, 
                text="⚠️ 自动导出即将开始！", 
                font=('微软雅黑', 16, 'bold'),
                fg='red'
            )
            title_label.pack(pady=20)
            
            content_frame = tk.Frame(warning_window)
            content_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
            
            tips = [
                "• 导出过程中请勿操作鼠标和键盘",
                "• 请勿切换窗口或进行其他操作",
                "• 导出完成后会自动跳回主画面"
            ]
            for tip in tips:
                tk.Label(
                    content_frame, 
                    text=tip, 
                    font=('微软雅黑', 12),
                    anchor='w',
                    justify=tk.LEFT
                ).pack(fill=tk.X, pady=8)
            
            btn_frame = tk.Frame(warning_window)
            btn_frame.pack(pady=20)
            
            result = [None]
            
            def on_ok():
                result[0] = True
                warning_window.destroy()
            
            def on_cancel():
                result[0] = False
                warning_window.destroy()
            
            tk.Button(
                btn_frame, 
                text="确定", 
                font=('微软雅黑', 12),
                width=10,
                command=on_ok
            ).pack(side=tk.LEFT, padx=20)
            
            tk.Button(
                btn_frame, 
                text="取消", 
                font=('微软雅黑', 12),
                width=10,
                command=on_cancel
            ).pack(side=tk.LEFT, padx=20)
            
            warning_window.wait_window()
            
            if not result[0]:
                return
        else:
            print("跳过操作提示（已在设置中禁用）")
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("自动导出进度")
        
        window_width = 450
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="准备开始自动导出...", font=("宋体", 12))
        progress_label.pack(pady=20)
        
        detail_label = tk.Label(progress_window, text="", font=("宋体", 10), fg="gray")
        detail_label.pack(pady=10)
        
        progress_window.update()
        
        # 检查是否有未设置的坐标
        unset_coords = []
        coord_names = {
            "zhuanglu_tab": "装炉顺作成管理标签",
            "zhuanglu_export_btn": "装炉顺序导出按钮",
            "zhizhi_tab": "轧制计划管理标签",
            "plan_select": "选择计划号",
            "zhizhi_export_btn": "导出总计划号列表按钮",
            "first_plan": "第一个计划号",
            "plan_detail_export": "计划明细导出按钮"
        }
        
        for key, name in coord_names.items():
            if not self.coordinates.get(key):
                unset_coords.append(name)
        
        if unset_coords:
            progress_window.destroy()
            self.custom_messagebox("警告", f"以下坐标未设置:\n" + "\n".join(f"  - {n}" for n in unset_coords) + "\n\n请先设置这些坐标后再测试")
            return
        
        # 实际导出流程
        import time
        
        def update_progress(main_msg, detail_msg=""):
            """更新进度显示"""
            progress_label.config(text=main_msg)
            if detail_msg:
                detail_label.config(text=detail_msg)
            progress_window.update()
            print(f"[进度] {main_msg} {detail_msg}")
        
        try:
            # 步骤1：导出装炉顺序
            update_progress("【步骤1/5】正在导出装炉顺序...")
            print("\n=== 步骤1：导出装炉顺序 ===")
            
            success1, log1 = self.export_zhuanglu_shunxu()
            print(log1)
            
            if not success1:
                progress_window.destroy()
                self.custom_messagebox("错误", log1)
                return
            
            update_progress("✓ 装炉顺序导出完成", "等待文件保存...")
            time.sleep(1)
            
            # 检查文件是否存在（使用计划号文件夹）
            plan_dir = os.path.join(self.plan_dir, "计划号")
            装炉顺序文件 = os.path.join(plan_dir, "装炉顺序.xls")
            if not os.path.exists(装炉顺序文件):
                progress_window.destroy()
                self.custom_messagebox("错误", f"装炉顺序文件不存在:\n{装炉顺序文件}")
                return
            
            # 步骤2：读取装炉顺序并标注（使用副本读取方案）
            update_progress("【步骤2/5】正在读取装炉顺序并标注...")
            print("\n=== 步骤2：读取装炉顺序并标注 ===")
            
            self.refresh_plan_list_from_file()
            
            zhuanglu_plans = [item['plan_no'] for item in self.plan_data]
            
            if not zhuanglu_plans:
                progress_window.destroy()
                self.custom_messagebox("错误", "无法读取装炉顺序文件\n列表为空")
                return
            
            update_progress("✓ 装炉顺序读取完成", f"共 {len(zhuanglu_plans)} 个计划号")
            time.sleep(0.5)
            
            # 步骤3：导出总计划号列表
            update_progress("【步骤3/5】正在导出总计划号列表...")
            print("\n=== 步骤3：导出总计划号列表 ===")
            
            test_window_zhizhi = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            success3 = self.export_zhizhi_plan_list(test_window=test_window_zhizhi)
            
            if not success3:
                progress_window.destroy()
                return
            
            update_progress("✓ 总计划号列表导出完成", "等待文件保存...")
            time.sleep(1)
            
            # 步骤4：重新计算坐标
            update_progress("【步骤4/5】正在重新计算坐标...")
            print("\n=== 步骤4：重新计算坐标 ===")
            
            # 读取总计划号列表并计算坐标（会自动更新缓存）
            coord_map = self.read_zhizhi_plan_list_with_coords()
            
            if not coord_map:
                progress_window.destroy()
                # 检查文件是否存在
                plan_dir = os.path.join(self.plan_dir, "计划号")
                plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
                if not os.path.exists(plan_list_file):
                    self.custom_messagebox("错误", f"无法计算计划号坐标\n\n原因：总计划号列表文件不存在\n路径：{plan_list_file}\n\n请先执行步骤3导出总计划号列表")
                else:
                    self.custom_messagebox("错误", "无法计算计划号坐标\n\n原因：读取总计划号列表文件失败\n\n可能原因：\n1. 文件被占用\n2. 文件格式错误\n3. 未找到计划号列")
                return
            
            update_progress("✓ 坐标计算完成", f"共 {len(coord_map)} 个计划号坐标")
            time.sleep(0.5)
            
            # 步骤5：导出无文件计划号的明细
            update_progress("【步骤5/5】正在导出无文件计划号明细...")
            print("\n=== 步骤5：导出无文件计划号明细 ===")
            
            # 获取标识为"无文件"的计划号
            no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
            print(f"找到 {len(no_file_plans)} 个无文件的计划号: {no_file_plans}")
            
            if not no_file_plans:
                progress_window.destroy()
                self.custom_messagebox("完成", "没有需要导出的计划号")
                return
            
            print(f"获取了 {len(no_file_plans)} 个计划号: {no_file_plans}")
            update_progress(f"正在导出 {len(no_file_plans)} 个计划号明细...", "")
            
            test_window = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            test_speed = self.coordinates.get("export_speed", "中")
            
            speed_delays = {"慢": 1.5, "中": 1.0, "快": 0.5}
            delay_time = speed_delays.get(test_speed, 1.0)
            
            plan_detail_export_btn = self.coordinates.get("plan_detail_export")
            if not plan_detail_export_btn:
                progress_window.destroy()
                self.custom_messagebox("错误", "未设置计划明细导出按钮坐标")
                return
            
            exported_plans = []
            failed_plans = []
            
            for i, plan_no in enumerate(no_file_plans):
                update_progress(f"【{i+1}/{len(no_file_plans)}】正在导出 {plan_no}...", f"剩余 {len(no_file_plans)-i-1} 个")
                print(f"\n[{i+1}/{len(no_file_plans)}] 导出计划: {plan_no}")
                
                coord = coord_map.get(plan_no)
                if not coord:
                    print(f"✗ 找不到计划号 {plan_no} 的坐标")
                    failed_plans.append(plan_no)
                    continue
                
                success = self.export_single_plan_detail(plan_no, coord, plan_detail_export_btn, test_window)
                
                if success:
                    exported_plans.append(plan_no)
                    self.mark_plan_as_exported(plan_no)
                else:
                    failed_plans.append(plan_no)
                
                if i < len(no_file_plans) - 1:
                    time.sleep(delay_time)
            
            progress_window.destroy()
            
            print("\n=== 自动导出全部完成 ===")
            print(f"装炉顺序: ✓")
            print(f"总计划号列表: ✓")
            print(f"坐标重新计算: ✓")
            print(f"计划号明细导出: {len(exported_plans)} 个成功, {len(failed_plans)} 个失败")
            
            # 检查是否需要自动处理
            auto_process = self.coordinates.get("auto_process_after_export", False)
            
            if auto_process and exported_plans:
                # 自动执行计划处理功能（处理刚刚导出的计划号）
                print("\n=== 自动执行计划处理 ===")
                # 选中刚刚导出的计划号
                if not isinstance(self.selected_items, set):
                    self.selected_items = set()
                else:
                    self.selected_items.clear()
                for i, plan_data in enumerate(self.plan_data):
                    if plan_data['plan_no'] in exported_plans:
                        self.selected_items.add(i)
                # 自动处理选中的计划号（自动导出流程中启用自动打印）
                self.process_plans(auto_print=True)
            else:
                # 构建详细信息，包含计划号及其坐标
                detail_info = f"自动导出流程已完成！\n\n成功: {len(exported_plans)} 个\n失败: {len(failed_plans)} 个\n\n导出计划号及其坐标:\n"
                for plan_no in exported_plans:
                    coord = coord_map.get(plan_no, "未知")
                    detail_info += f"- {plan_no}: {coord}\n"
                
                detail_info += "\n是否对导出的计划进行处理？"
                
                # 询问是否处理导出的计划
                # 先将主窗口提升到前面
                try:
                    self.root.lift()
                    self.root.focus_force()
                    print("主窗口已提升到前面")
                except Exception as e:
                    print(f"提升主窗口失败: {e}")
                
                # 创建一个临时窗口作为父窗口，确保弹窗在最前面
                temp_window = tk.Toplevel(self.root)
                temp_window.withdraw()  # 隐藏临时窗口
                temp_window.lift()
                temp_window.focus_force()
                temp_window.transient(self.root)  # 设置为临时窗口
                temp_window.grab_set()  # 模态化，阻止操作其他窗口
                
                try:
                    # 显示弹窗并获取用户选择
                    user_choice = self.custom_messagebox("完成", detail_info, msg_type='yesno')
                    # 释放模态抓取
                    temp_window.grab_release()
                    # 销毁临时窗口
                    temp_window.destroy()
                except Exception as e:
                    # 如果应用程序已销毁，直接设置为不处理
                    user_choice = False
                    print(f"弹窗处理异常: {e}")
                    try:
                        temp_window.grab_release()
                        temp_window.destroy()
                    except:
                        pass
                
                if user_choice:
                    # 自动执行计划处理功能（处理刚刚导出的计划号）
                    print("\n=== 自动执行计划处理 ===")
                    # 选中刚刚导出的计划号
                    if not isinstance(self.selected_items, set):
                        self.selected_items = set()
                    else:
                        self.selected_items.clear()
                    for i, plan_data in enumerate(self.plan_data):
                        if plan_data['plan_no'] in exported_plans:
                            self.selected_items.add(i)
                    # 自动处理选中的计划号（自动导出流程中启用自动打印）
                    self.process_plans(auto_print=True)
            
        except Exception as e:
            print(f"✗ 自动导出失败: {str(e)}")
            import traceback
            traceback.print_exc()
            try:
                if 'progress_window' in locals():
                    progress_window.destroy()
            except:
                pass
            try:
                self.custom_messagebox("错误", f"自动导出失败: {str(e)}")
            except:
                pass
        
        # 刷新界面（使用副本读取方案，避免文件占用）
        print("刷新计划号列表...")
        try:
            self.refresh_plan_list_from_file()
            self.root.lift()
            self.root.focus_force()
        except Exception as e:
            print(f"刷新界面失败: {e}")
    
    def auto_print(self):
        """自动打印"""
        self.custom_messagebox("提示", "自动打印功能待实现")
    
    def full_auto_print(self):
        """全自动打印"""
        self.custom_messagebox("提示", "全自动打印功能待实现")
    
    def settings(self):
        """打开设置窗口"""
        self.open_export_config()
    
    def open_export_config(self):
        """打开坐标配置窗口"""
        # 检查设置窗口是否已存在
        if hasattr(self, 'config_window') and self.config_window is not None and self.config_window.winfo_exists():
            # 如果窗口已存在，将其提升到前面
            self.config_window.lift()
            self.config_window.focus_force()
            return
        
        # 创建新窗口
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("自动导出设置")
        
        # 直接计算居中位置并设置窗口几何形状
        width = 950
        height = 700
        screen_width = self.config_window.winfo_screenwidth()
        screen_height = self.config_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # 直接设置完整的几何形状，包括位置
        self.config_window.geometry(f"{width}x{height}+{x}+{y}")
        self.config_window.minsize(900, 600)
        
        # 创建设置界面，传递MainApp实例以便实时更新配置
        ExportConfigGUI(self.config_window, self.plan_dir, self)
        
        # 窗口关闭时重新加载坐标配置并清空引用
        def on_close():
            self.coordinates = self.load_coordinate_config()
            self.config_window.destroy()
            self.config_window = None
        
        self.config_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def furnace_details(self):
        """装炉明细"""
        self.custom_messagebox("提示", "装炉明细功能待实现")
    
    def process_plans(self, auto_print=False):
        """处理计划号文件 - 使用 pandas + xlwt 方案
        
        Args:
            auto_print: 是否在处理完成后自动打印（默认False，仅自动导出流程中为True）
        """
        try:
            # 检查是否选择了计划号
            if not self.selected_items:
                self.custom_messagebox("警告", "请先在计划号列表中选择要处理的计划号")
                return
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            if not os.path.exists(plan_dir):
                self.custom_messagebox("错误", f"计划号文件夹不存在: {plan_dir}")
                return
            
            # 获取选中的计划号
            selected_plans = [self.plan_data[i]['plan_no'] for i in self.selected_items]
            
            # 检查选中的计划号中是否有已处理的
            already_processed = [plan_no for plan_no in selected_plans if plan_no in self.processed_plans]
            if already_processed:
                self.custom_messagebox("提示", f"以下计划号已处理过，无需重复处理：\n\n{', '.join(already_processed)}")
                return
            
            # 构建选中计划号的文件路径列表
            selected_files = []
            for plan_no in selected_plans:
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    selected_files.append((plan_no, file_path))
                else:
                    print(f"✗ 文件不存在: {plan_no}.xls")
            
            if not selected_files:
                self.custom_messagebox("提示", "选中的计划号没有对应的文件")
                return
            
            # 直接处理，不显示确认窗口
            
            # 处理每个文件
            processed_count = 0
            failed_count = 0
            skipped_count = 0
            success_files = []
            failed_files = []
            skipped_files = []
            
            for plan_no, file_path in selected_files:
                try:
                    print(f"开始处理: {plan_no}.xls")
                    self.run_excel_macro_with_pandas(file_path)
                    processed_count += 1
                    success_files.append(plan_no)
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_count > 0:
                self.save_processed_plans()
                # 刷新列表显示
                self.update_listbox()
            
            # 检查是否需要自动打印（仅在自动导出流程中）
            if auto_print and success_files:
                # 自动执行打印功能（打印刚刚处理的计划号）
                print("\n=== 自动执行计划打印 ===")
                # 选中刚刚处理成功的计划号
                if not isinstance(self.selected_items, set):
                    self.selected_items = set()
                else:
                    self.selected_items.clear()
                for i, plan_data in enumerate(self.plan_data):
                    if plan_data['plan_no'] in success_files:
                        self.selected_items.add(i)
                # 自动打印选中的计划号
                self.print_selected()
            
            # 显示结果 - 使用自定义窗口
            import tkinter as tk
            from tkinter import ttk
            
            # 创建自定义窗口
            result_window = tk.Toplevel(self.root)
            result_window.title("完成")
            result_window.geometry("600x450")
            result_window.resizable(True, True)
            
            # 计算居中位置
            screen_width = result_window.winfo_screenwidth()
            screen_height = result_window.winfo_screenheight()
            x = (screen_width // 2) - (600 // 2)
            y = (screen_height // 2) - (450 // 2)
            result_window.geometry(f"600x450+{x}+{y}")
            
            # 设置窗口样式
            result_window.configure(bg='#f0f0f0')
            
            # 创建主框架
            main_frame = tk.Frame(result_window, bg='#f0f0f0', padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text="处理完成！",
                font=('宋体', 24, 'bold'),
                bg='#f0f0f0'
            )
            title_label.pack(pady=10)
            
            # 统计信息
            stats_frame = tk.Frame(main_frame, bg='#f0f0f0')
            stats_frame.pack(fill=tk.X, pady=10)
            
            stats_label = tk.Label(
                stats_frame,
                text=f"成功: {processed_count} 个 | 失败: {failed_count} 个 | 跳过: {skipped_count} 个",
                font=('宋体', 16),
                bg='#f0f0f0'
            )
            stats_label.pack()
            
            # 成功的计划号
            if success_files:
                success_frame = tk.Frame(main_frame, bg='#f0f0f0')
                success_frame.pack(fill=tk.X, pady=10)
                
                success_label = tk.Label(
                    success_frame,
                    text=f"成功的计划号: {', '.join(success_files)}",
                    font=('宋体', 14),
                    bg='#f0f0f0',
                    justify=tk.LEFT,
                    wraplength=500
                )
                success_label.pack(anchor='w')
            
            # 失败的计划号
            if failed_files:
                failed_frame = tk.Frame(main_frame, bg='#f0f0f0')
                failed_frame.pack(fill=tk.X, pady=10)
                
                failed_label = tk.Label(
                    failed_frame,
                    text=f"失败的计划号: {', '.join(failed_files)}",
                    font=('宋体', 14),
                    bg='#f0f0f0',
                    justify=tk.LEFT,
                    wraplength=500
                )
                failed_label.pack(anchor='w')
            
            # 跳过的计划号
            if skipped_files:
                skipped_frame = tk.Frame(main_frame, bg='#f0f0f0')
                skipped_frame.pack(fill=tk.X, pady=10)
                
                skipped_label = tk.Label(
                    skipped_frame,
                    text=f"跳过的计划号: {', '.join(skipped_files)}",
                    font=('宋体', 14),
                    bg='#f0f0f0',
                    justify=tk.LEFT,
                    wraplength=500
                )
                skipped_label.pack(anchor='w')
            
            # 确定按钮
            btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
            btn_frame.pack(side=tk.BOTTOM, pady=20)
            
            ok_btn = ttk.Button(
                btn_frame,
                text="确定",
                command=result_window.destroy,
                width=10
            )
            ok_btn.pack()
            
            # 确保窗口在最前面
            result_window.transient(self.root)
            result_window.grab_set()
            result_window.lift()
            result_window.focus_force()
            
        except Exception as e:
            self.custom_messagebox("错误", f"处理计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def run_excel_macro_with_pandas(self, file_path):
        """使用 pandas + xlwt 处理Excel文件（xls格式）
        
        提取指定字段，删除其他字段，添加"轧宽+（余量）"和"装炉顺序号"字段
        """
        import os
        import xlwt
        from xlutils.copy import copy
        
        # 1. 使用xlrd读取原文件
        success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
        if not success:
            raise Exception(f"读取文件失败: {result}")
        workbook = result
        sheet = workbook.sheet_by_index(0)
        
        # 2. 加载装炉顺序数据，构建映射
        装炉顺序映射 = {}
        轧宽余量映射 = {}
        装炉顺序文件 = os.path.join(self.plan_dir, "计划号", "装炉顺序.xls")
        
        # 加载第5工作表的钢种列表
        钢种列表 = []
        第5工作表文件 = os.path.join(self.plan_dir, "计划号", "装炉顺序.xls")  # 假设第5工作表在同一个文件中
        if os.path.exists(第5工作表文件):
            success, result = self.safe_read_excel(第5工作表文件, max_retries=3, retry_delay=0.5)
            if success:
                workbook3 = result
                try:
                    if workbook3.nsheets >= 5:
                        sheet3 = workbook3.sheet_by_index(4)  # 第5工作表（索引4）
                        for row_idx in range(sheet3.nrows):
                            钢种值 = sheet3.cell_value(row_idx, 0)
                            if 钢种值:
                                钢种列表.append(str(钢种值).strip())
                except Exception:
                    pass
                finally:
                    workbook3.release_resources()
        
        # 构建钢种集合用于快速查找
        钢种集合 = set(钢种列表)
        
        # 加载除鳞钢种列表
        removePhosphorusList = self.load_remove_phosphorus_list()
        
        # 加载APS钢种列表
        apsGrades = self.load_aps_grades()
        
        if os.path.exists(装炉顺序文件):
            success, result = self.safe_read_excel(装炉顺序文件, max_retries=3, retry_delay=0.5)
            if success:
                workbook2 = result
                sheet2 = workbook2.sheet_by_index(0)
                
                headers = []
                for col_idx in range(sheet2.ncols):
                    headers.append(sheet2.cell_value(0, col_idx))
                
                装炉钢卷号列 = headers.index("钢卷号") if "钢卷号" in headers else -1
                装炉顺序号列 = headers.index("装炉顺序号") if "装炉顺序号" in headers else -1
                轧宽余量列 = -1
                if "轧宽（+余量）" in headers:
                    轧宽余量列 = headers.index("轧宽（+余量）")
                elif "轧宽+（余量）" in headers:
                    轧宽余量列 = headers.index("轧宽+（余量）")
                
                if 装炉钢卷号列 != -1:
                    # 首先收集所有钢卷号和对应的装炉顺序号
                    钢卷号顺序号列表 = []
                    for row_idx in range(1, sheet2.nrows):
                        钢卷号 = sheet2.cell_value(row_idx, 装炉钢卷号列)
                        if 钢卷号:
                            钢卷号字符串 = str(钢卷号)
                            原装炉顺序号 = None
                            
                            if 装炉顺序号列 != -1:
                                try:
                                    原装炉顺序号 = int(sheet2.cell_value(row_idx, 装炉顺序号列))
                                except (ValueError, TypeError):
                                    原装炉顺序号 = 0
                            
                            钢卷号顺序号列表.append((钢卷号字符串, 原装炉顺序号))
                    
                    # 按装炉顺序号排序
                    钢卷号顺序号列表.sort(key=lambda x: x[1])
                    
                    # 为每个钢卷号分配装炉顺：等于装炉顺序号
                    for 钢卷号字符串, 原装炉顺序号 in 钢卷号顺序号列表:
                        轧宽余量值 = None
                        
                        # 重新读取轧宽余量值
                        for row_idx in range(1, sheet2.nrows):
                            钢卷号 = sheet2.cell_value(row_idx, 装炉钢卷号列)
                            if 钢卷号 and str(钢卷号) == 钢卷号字符串:
                                if 轧宽余量列 != -1:
                                    轧宽余量值 = sheet2.cell_value(row_idx, 轧宽余量列)
                                break
                        
                        # 存储原始装炉顺序号和装炉顺（装炉顺等于装炉顺序号）
                        装炉顺序映射[钢卷号字符串] = {
                            "原装炉顺序号": 原装炉顺序号,
                            "装炉顺": 原装炉顺序号
                        }
                        
                        if 轧宽余量值 is not None:
                            轧宽余量映射[钢卷号字符串] = 轧宽余量值
                
                workbook2.release_resources()
        
        # 3. 定义目标列（按照图片上的顺序）
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "层号", "去向", "坯厚", "坯宽", "坯长",
            "中间坯厚度设定值", "轧厚", "轧宽+（余量）", "订货宽度", "切边方式",
            "板坯宽度调宽标记", "侧压量", "碳", "RT2目标值", "硬度组", "粗轧报信",
            "装炉顺序号", "板坯头部宽度", "板坯尾部宽度", "计划号", "热轧产品分类",
            "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽"
        ]
        
        # 定义字段名映射（按照图片上的显示名称）
        字段名映射 = {
            "顺序号": "序号",
            "钢卷号": "钢卷号",
            "牌号（钢级）": "牌号（钢级）",
            "层号": "除鳞",
            "去向": "去向",
            "坯厚": "坯厚",
            "坯宽": "坯宽",
            "坯长": "坯长",
            "中间坯厚度设定值": "中厚",
            "轧厚": "轧厚",
            "轧宽+（余量）": "轧宽",  # 图片上的"轧宽"来自"轧宽+（余量）"
            "订货宽度": "订宽",
            "切边方式": "切边",
            "板坯宽度调宽标记": "调宽",
            "侧压量": "减宽",
            "碳": "公差带",
            "RT2目标值": "RT2",
            "硬度组": "强度",
            "粗轧报信": "粗轧报信",
            "装炉顺序号": "装炉顺",
            "板坯头部宽度": "坯头部宽",
            "板坯尾部宽度": "坯尾部宽",
            "计划号": "计划号",
            "热轧产品分类": "热轧产品分类",
            "炼钢钢种": "炼钢钢种",
            "宽度负公差": "负公差",
            "宽度正公差": "正公差",
            "板坯炉后拒收次数": "回炉坯",
            "轧宽": "原轧宽"  # 图片上的"原轧宽"来自原来的"轧宽"
        }
        
        # 定义反向映射（从映射后的名称到原始名称）
        反向字段名映射 = {}
        for 原始名称, 映射名称 in 字段名映射.items():
            反向字段名映射[映射名称] = 原始名称
        
        # 4. 查找当前列名
        current_columns = []
        for i in range(sheet.ncols):
            current_columns.append(sheet.cell_value(0, i))
        
        # 5. 创建新的工作簿
        new_workbook = xlwt.Workbook()
        new_sheet = new_workbook.add_sheet(sheet.name)
        
        # 设置页面属性
        # 设置纸张大小为美国Fanfold (标准值为39)
        # 注意：xlwt的paper_size值对应Excel的纸张类型枚举
        # 39 = xlPaperFanfoldUS (14.875 x 11 inches)
        new_sheet.paper_size = 39
        # 设置页边距为0（使用inches为单位）
        new_sheet.left_margin = 0.0
        new_sheet.right_margin = 0.0
        new_sheet.top_margin = 0.0
        new_sheet.bottom_margin = 0.0
        # 设置页眉页脚为空（使用bytes类型）
        new_sheet.header_str = b''
        new_sheet.footer_str = b''
        # 设置文档缩放比例为140%
        new_sheet.normal_magn = 140
        
        # 6. 定义样式
        # 大标题样式
        style_title = xlwt.XFStyle()
        font_title = xlwt.Font()
        font_title.name = '仿宋'
        font_title.height = 280  # 14pt
        font_title.bold = True
        style_title.font = font_title
        alignment_title = xlwt.Alignment()
        alignment_title.horz = xlwt.Alignment.HORZ_CENTER
        alignment_title.vert = xlwt.Alignment.VERT_CENTER
        style_title.alignment = alignment_title
        
        # 信息行样式（计划号、块数、提示信息）
        style_header_info = xlwt.XFStyle()
        font_header_info = xlwt.Font()
        font_header_info.name = '仿宋'
        font_header_info.height = 280  # 14pt
        font_header_info.bold = True
        style_header_info.font = font_header_info
        alignment_header_info = xlwt.Alignment()
        alignment_header_info.horz = xlwt.Alignment.HORZ_LEFT
        alignment_header_info.vert = xlwt.Alignment.VERT_CENTER
        alignment_header_info.wrap = True
        style_header_info.alignment = alignment_header_info
        
        # 字段列名样式（带边框）
        style_header_border = xlwt.XFStyle()
        font_header_border = xlwt.Font()
        font_header_border.name = '仿宋'
        font_header_border.height = 280  # 14pt
        font_header_border.bold = True
        style_header_border.font = font_header_border
        alignment_header_border = xlwt.Alignment()
        alignment_header_border.horz = xlwt.Alignment.HORZ_CENTER
        alignment_header_border.vert = xlwt.Alignment.VERT_CENTER
        style_header_border.alignment = alignment_header_border
        borders_header = xlwt.Borders()
        borders_header.left = xlwt.Borders.THIN
        borders_header.right = xlwt.Borders.THIN
        borders_header.top = xlwt.Borders.THIN
        borders_header.bottom = xlwt.Borders.THIN
        style_header_border.borders = borders_header
        
        # 打印时间样式（右对齐）
        style_time = xlwt.XFStyle()
        font_time = xlwt.Font()
        font_time.name = '仿宋'
        font_time.height = 280  # 14pt
        font_time.bold = True
        style_time.font = font_time
        alignment_time = xlwt.Alignment()
        alignment_time.horz = xlwt.Alignment.HORZ_RIGHT
        alignment_time.vert = xlwt.Alignment.VERT_CENTER
        style_time.alignment = alignment_time
        
        # 数据行样式（带边框，去掉竖线）
        style_data = xlwt.XFStyle()
        font_data = xlwt.Font()
        font_data.name = '仿宋'
        font_data.height = 220  # 11pt
        font_data.bold = True
        style_data.font = font_data
        alignment_data = xlwt.Alignment()
        alignment_data.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data.vert = xlwt.Alignment.VERT_CENTER
        style_data.alignment = alignment_data
        borders_data = xlwt.Borders()
        borders_data.left = xlwt.Borders.NO_LINE
        borders_data.right = xlwt.Borders.NO_LINE
        borders_data.top = xlwt.Borders.THIN
        borders_data.bottom = xlwt.Borders.THIN
        style_data.borders = borders_data
        
        # 特殊字体大小样式
        # 12pt 样式（加粗，去掉竖线）
        style_data_12pt = xlwt.XFStyle()
        font_data_12pt = xlwt.Font()
        font_data_12pt.name = '仿宋'
        font_data_12pt.height = 240  # 12pt
        font_data_12pt.bold = True
        style_data_12pt.font = font_data_12pt
        alignment_data_12pt = xlwt.Alignment()
        alignment_data_12pt.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_12pt.vert = xlwt.Alignment.VERT_CENTER
        style_data_12pt.alignment = alignment_data_12pt
        borders_data_12pt = xlwt.Borders()
        borders_data_12pt.left = xlwt.Borders.NO_LINE
        borders_data_12pt.right = xlwt.Borders.NO_LINE
        borders_data_12pt.top = xlwt.Borders.THIN
        borders_data_12pt.bottom = xlwt.Borders.THIN
        style_data_12pt.borders = borders_data_12pt
        
        # 12pt 左对齐样式（用于牌号钢级）
        style_data_12pt_left = xlwt.XFStyle()
        font_data_12pt_left = xlwt.Font()
        font_data_12pt_left.name = '仿宋'
        font_data_12pt_left.height = 240  # 12pt
        font_data_12pt_left.bold = True
        style_data_12pt_left.font = font_data_12pt_left
        alignment_data_12pt_left = xlwt.Alignment()
        alignment_data_12pt_left.horz = xlwt.Alignment.HORZ_LEFT
        alignment_data_12pt_left.vert = xlwt.Alignment.VERT_CENTER
        style_data_12pt_left.alignment = alignment_data_12pt_left
        borders_data_12pt_left = xlwt.Borders()
        borders_data_12pt_left.left = xlwt.Borders.NO_LINE
        borders_data_12pt_left.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left.top = xlwt.Borders.THIN
        borders_data_12pt_left.bottom = xlwt.Borders.THIN
        style_data_12pt_left.borders = borders_data_12pt_left
        
        # 14pt 样式（加粗，去掉竖线）
        style_data_14pt = xlwt.XFStyle()
        font_data_14pt = xlwt.Font()
        font_data_14pt.name = '仿宋'
        font_data_14pt.height = 280  # 14pt
        font_data_14pt.bold = True
        style_data_14pt.font = font_data_14pt
        alignment_data_14pt = xlwt.Alignment()
        alignment_data_14pt.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_14pt.vert = xlwt.Alignment.VERT_CENTER
        style_data_14pt.alignment = alignment_data_14pt
        borders_data_14pt = xlwt.Borders()
        borders_data_14pt.left = xlwt.Borders.NO_LINE
        borders_data_14pt.right = xlwt.Borders.NO_LINE
        borders_data_14pt.top = xlwt.Borders.THIN
        borders_data_14pt.bottom = xlwt.Borders.THIN
        style_data_14pt.borders = borders_data_14pt
        
        # 16pt 样式（加粗，去掉竖线）
        style_data_16pt = xlwt.XFStyle()
        font_data_16pt = xlwt.Font()
        font_data_16pt.name = '仿宋'
        font_data_16pt.height = 320  # 16pt
        font_data_16pt.bold = True
        style_data_16pt.font = font_data_16pt
        style_data_16pt.alignment = alignment_data
        style_data_16pt.borders = borders_data
        
        # 虚线边框样式（用于除鳞、轧宽、公差带）
        style_data_dashed = xlwt.XFStyle()
        font_data_dashed = xlwt.Font()
        font_data_dashed.name = '仿宋'
        font_data_dashed.height = 220  # 11pt
        font_data_dashed.bold = True
        style_data_dashed.font = font_data_dashed
        alignment_data_dashed = xlwt.Alignment()
        alignment_data_dashed.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_dashed.vert = xlwt.Alignment.VERT_CENTER
        style_data_dashed.alignment = alignment_data_dashed
        borders_data_dashed = xlwt.Borders()
        borders_data_dashed.left = xlwt.Borders.DASHED
        borders_data_dashed.right = xlwt.Borders.DASHED
        borders_data_dashed.top = xlwt.Borders.THIN
        borders_data_dashed.bottom = xlwt.Borders.THIN
        style_data_dashed.borders = borders_data_dashed
        
        # 12pt 虚线边框样式（用于除鳞、轧宽、公差带）
        style_data_12pt_dashed = xlwt.XFStyle()
        font_data_12pt_dashed = xlwt.Font()
        font_data_12pt_dashed.name = '仿宋'
        font_data_12pt_dashed.height = 240  # 12pt
        font_data_12pt_dashed.bold = True
        style_data_12pt_dashed.font = font_data_12pt_dashed
        style_data_12pt_dashed.alignment = alignment_data_12pt
        borders_data_12pt_dashed = xlwt.Borders()
        borders_data_12pt_dashed.left = xlwt.Borders.DASHED
        borders_data_12pt_dashed.right = xlwt.Borders.DASHED
        borders_data_12pt_dashed.top = xlwt.Borders.THIN
        borders_data_12pt_dashed.bottom = xlwt.Borders.THIN
        style_data_12pt_dashed.borders = borders_data_12pt_dashed
        
        # 14pt 虚线边框样式（用于轧宽）
        style_data_14pt_dashed = xlwt.XFStyle()
        font_data_14pt_dashed = xlwt.Font()
        font_data_14pt_dashed.name = '仿宋'
        font_data_14pt_dashed.height = 280  # 14pt
        font_data_14pt_dashed.bold = True
        style_data_14pt_dashed.font = font_data_14pt_dashed
        style_data_14pt_dashed.alignment = alignment_data_14pt
        borders_data_14pt_dashed = xlwt.Borders()
        borders_data_14pt_dashed.left = xlwt.Borders.DASHED
        borders_data_14pt_dashed.right = xlwt.Borders.DASHED
        borders_data_14pt_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_dashed.borders = borders_data_14pt_dashed
        
        # 自动换行样式（用于粗轧报信）
        style_data_wrap = xlwt.XFStyle()
        font_data_wrap = xlwt.Font()
        font_data_wrap.name = '仿宋'
        font_data_wrap.height = 240  # 12pt
        font_data_wrap.bold = True
        style_data_wrap.font = font_data_wrap
        alignment_data_wrap = xlwt.Alignment()
        alignment_data_wrap.horz = xlwt.Alignment.HORZ_CENTER
        alignment_data_wrap.vert = xlwt.Alignment.VERT_CENTER
        alignment_data_wrap.wrap = True
        style_data_wrap.alignment = alignment_data_wrap
        borders_data_wrap = xlwt.Borders()
        borders_data_wrap.left = xlwt.Borders.NO_LINE
        borders_data_wrap.right = xlwt.Borders.NO_LINE
        borders_data_wrap.top = xlwt.Borders.THIN
        borders_data_wrap.bottom = xlwt.Borders.THIN
        style_data_wrap.borders = borders_data_wrap
        
        # 14pt 自动换行样式（用于粗轧报信）- 左对齐
        style_data_wrap_14pt = xlwt.XFStyle()
        font_data_wrap_14pt = xlwt.Font()
        font_data_wrap_14pt.name = '仿宋'
        font_data_wrap_14pt.height = 280  # 14pt
        font_data_wrap_14pt.bold = True
        style_data_wrap_14pt.font = font_data_wrap_14pt
        alignment_data_wrap_14pt = xlwt.Alignment()
        alignment_data_wrap_14pt.horz = xlwt.Alignment.HORZ_LEFT
        alignment_data_wrap_14pt.vert = xlwt.Alignment.VERT_CENTER
        alignment_data_wrap_14pt.wrap = True
        style_data_wrap_14pt.alignment = alignment_data_wrap_14pt
        style_data_wrap_14pt.borders = borders_data_wrap
        
        # 14pt 双横线样式（用于减宽超标）
        style_data_14pt_double = xlwt.XFStyle()
        font_data_14pt_double = xlwt.Font()
        font_data_14pt_double.name = '仿宋'
        font_data_14pt_double.height = 280  # 14pt
        font_data_14pt_double.bold = True
        style_data_14pt_double.font = font_data_14pt_double
        style_data_14pt_double.alignment = alignment_data_14pt
        borders_data_14pt_double = xlwt.Borders()
        borders_data_14pt_double.left = xlwt.Borders.NO_LINE
        borders_data_14pt_double.right = xlwt.Borders.NO_LINE
        borders_data_14pt_double.top = xlwt.Borders.DOUBLE
        borders_data_14pt_double.bottom = xlwt.Borders.DOUBLE
        style_data_14pt_double.borders = borders_data_14pt_double
        
        # 第一列左侧实线边框样式（12pt）
        style_data_12pt_left_border = xlwt.XFStyle()
        font_data_12pt_left_border = xlwt.Font()
        font_data_12pt_left_border.name = '仿宋'
        font_data_12pt_left_border.height = 240  # 12pt
        font_data_12pt_left_border.bold = True
        style_data_12pt_left_border.font = font_data_12pt_left_border
        style_data_12pt_left_border.alignment = alignment_data_12pt
        borders_data_12pt_left_border = xlwt.Borders()
        borders_data_12pt_left_border.left = xlwt.Borders.THIN
        borders_data_12pt_left_border.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left_border.top = xlwt.Borders.THIN
        borders_data_12pt_left_border.bottom = xlwt.Borders.THIN
        style_data_12pt_left_border.borders = borders_data_12pt_left_border
        
        # 第一列左侧实线边框样式（16pt - 用于钢卷号）
        style_data_16pt_left_border = xlwt.XFStyle()
        font_data_16pt_left_border = xlwt.Font()
        font_data_16pt_left_border.name = '仿宋'
        font_data_16pt_left_border.height = 320  # 16pt
        font_data_16pt_left_border.bold = True
        style_data_16pt_left_border.font = font_data_16pt_left_border
        style_data_16pt_left_border.alignment = alignment_data
        borders_data_16pt_left_border = xlwt.Borders()
        borders_data_16pt_left_border.left = xlwt.Borders.THIN
        borders_data_16pt_left_border.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left_border.top = xlwt.Borders.THIN
        borders_data_16pt_left_border.bottom = xlwt.Borders.THIN
        style_data_16pt_left_border.borders = borders_data_16pt_left_border
        
        # 装炉顺列右侧实线边框样式（12pt）
        style_data_12pt_right_border = xlwt.XFStyle()
        font_data_12pt_right_border = xlwt.Font()
        font_data_12pt_right_border.name = '仿宋'
        font_data_12pt_right_border.height = 240  # 12pt
        font_data_12pt_right_border.bold = True
        style_data_12pt_right_border.font = font_data_12pt_right_border
        style_data_12pt_right_border.alignment = alignment_data_12pt
        borders_data_12pt_right_border = xlwt.Borders()
        borders_data_12pt_right_border.left = xlwt.Borders.NO_LINE
        borders_data_12pt_right_border.right = xlwt.Borders.THIN
        borders_data_12pt_right_border.top = xlwt.Borders.THIN
        borders_data_12pt_right_border.bottom = xlwt.Borders.THIN
        style_data_12pt_right_border.borders = borders_data_12pt_right_border
        
        # 7. 获取计划号和块数
        计划号 = ""
        块数 = sheet.nrows - 1
        
        for row_idx in range(1, sheet.nrows):
            if "计划号" in current_columns:
                计划号值 = sheet.cell_value(row_idx, current_columns.index("计划号"))
                if 计划号值:
                    计划号 = str(计划号值)
                    break
        
        # 获取当前时间
        from datetime import datetime
        当前时间 = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        # 找到"装炉顺"列的索引（最后一列）
        装炉顺列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
                break
        
        # 如果找到装炉顺列，标题只跨列到该列；否则跨所有列
        if 装炉顺列索引 >= 0:
            标题结束列 = 装炉顺列索引
        else:
            标题结束列 = len(target_columns) - 1
        
        # 8. 设置列宽（根据用户提供的最后显示的列宽值，在写入表头之前设置）
        # 根据实际测试，调整转换系数以确保显示正确的列宽
        # 对于较小的列宽值，需要使用更大的转换系数
        # 基础转换公式：设置值 = 目标显示值 * 256 * 1.04
        # 对于序号、去向、切边、强度等小列宽，使用转换系数1.2
        # 对于除鳞等中等列宽，使用转换系数1.08
        # 对于公差带、轧宽、减宽、装炉顺等列，使用特定转换系数
        col_widths = [
            int(3.6 * 256 * 1.2),       # 序号（使用1.2转换系数）
            int(18 * 256 * 1.04),       # 钢卷号
            int(18 * 256 * 1.09),       # 牌号（钢级）（使用1.09转换系数）
            int(6 * 256 * 1.08),        # 除鳞（层号）（使用1.08转换系数）
            int(3.6 * 256 * 1.2),       # 去向（使用1.2转换系数）
            int(4.86 * 256 * 1.04),     # 坯厚
            int(5.9 * 256 * 1.04),       # 坯宽
            int(6.2 * 256 * 1.13),       # 坯长（使用1.13转换系数）
            int(4 * 256 * 1.04),         # 中厚（中间坯厚度设定值）
            int(4.57 * 256 * 1.04),      # 轧厚
            int(6.5 * 256 * 1.13),       # 轧宽（轧宽+（余量））（使用1.13转换系数）
            int(5 * 256 * 1.17),       # 订宽（订货宽度）（使用1.17转换系数）
            int(3.6 * 256 * 1.2),       # 切边（切边方式）（使用1.2转换系数）
            int(5.6 * 256 * 1.04),       # 调宽（板坯宽度调宽标记）
            int(7 * 256 * 1.05),         # 减宽（侧压量）（使用1.05转换系数）
            int(9 * 256 * 1.03),         # 公差带（碳）（使用1.03转换系数）
            int(6.0 * 256 * 1.04),       # RT2（RT2目标值）
            int(3.6 * 256 * 1.2),       # 强度（硬度组）（使用1.2转换系数）
            int(33 * 256 * 1.04),        # 粗轧报信（动态计算）
            int(5.0 * 256 * 1.1),       # 装炉顺（装炉顺序号）（使用1.1转换系数）
            int(8.0 * 256 * 1.04),       # 坯头部宽（板坯头部宽度）
            int(8.0 * 256 * 1.04),       # 坯尾部宽（板坯尾部宽度）
            int(8.0 * 256 * 1.04),       # 计划号
            int(8.0 * 256 * 1.04),       # 轧产品分（热轧产品分类）
            int(8.0 * 256 * 1.04),       # 炼钢钢种
            int(8.0 * 256 * 1.04),       # 负公差（宽度负公差）
            int(8.0 * 256 * 1.04),       # 正公差（宽度正公差）
            int(8.0 * 256 * 1.04),       # 回炉坯（板坯炉后拒收次数）
            int(8.0 * 256 * 1.04)        # 原轧宽（轧宽）
        ]
        # 设置固定列宽
        for col_idx, width in enumerate(col_widths):
            if col_idx < len(target_columns):
                new_sheet.col(col_idx).width = width
                # 设置为固定列宽（不允许自动调整）
                new_sheet.col(col_idx).width_mismatch = True
        
        # 8. 写入数据
        # 初始化统计变量
        无APS钢种数 = 0
        无APS块数 = 0
        已添加无APS的钢种 = set()
        包含无APS = False
        减宽超标块数 = 0
        逆宽轧制板坯数 = 0
        低轧宽板坯数 = 0
        极低轧宽板坯数 = 0
        
        # 收集所有行数据
        all_row_data = []
        
        for row_idx in range(1, sheet.nrows):
            # 构建当前行的数据映射
            row_data = {}
            for col_idx, col_name in enumerate(current_columns):
                row_data[col_name] = sheet.cell_value(row_idx, col_idx)
            
            # 填充"装炉顺序号"字段
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                if 钢卷号值:
                    钢卷号字符串 = str(钢卷号值)
                    if 钢卷号字符串 in 装炉顺序映射:
                        # 保持原始装炉顺序号
                        原装炉顺序号 = 装炉顺序映射[钢卷号字符串]["原装炉顺序号"]
                        row_data["装炉顺序号"] = 原装炉顺序号
                        # 存储装炉顺用于后续写入
                        row_data["装炉顺"] = 装炉顺序映射[钢卷号字符串]["装炉顺"]
            
            # 填充"轧宽+（余量）"字段
            if "钢卷号" in row_data:
                钢卷号值 = row_data["钢卷号"]
                if 钢卷号值:
                    钢卷号字符串 = str(钢卷号值)
                    if 钢卷号字符串 in 轧宽余量映射:
                        row_data["轧宽+（余量）"] = 轧宽余量映射[钢卷号字符串]
            
            # 钢种转换逻辑
            if "牌号（钢级）" in row_data and "炼钢钢种" in row_data and "热轧产品分类" in row_data:
                牌号值 = str(row_data.get("牌号（钢级）", "")).strip()
                炼钢钢种值 = str(row_data.get("炼钢钢种", "")).strip()
                热轧产品分类值 = str(row_data.get("热轧产品分类", "")).strip()
                
                # 规则1：如果牌号（钢级）列是"SPHC"且炼钢钢种列是"P3A1"，则牌号（钢级）列值添加"-P"
                if 牌号值 == "SPHC" and 炼钢钢种值 == "P3A1":
                    row_data["牌号（钢级）"] = 牌号值 + "-P"
                else:
                    # 规则2：在第5工作表A列中查找当前行的牌号（钢级）字段和炼钢钢种字段值
                    牌号在列表中 = 牌号值 in 钢种集合
                    炼钢钢种在列表中 = 炼钢钢种值 in 钢种集合
                    
                    # 规则3：如果都找不到
                    if not 牌号在列表中 and not 炼钢钢种在列表中:
                        # 若热轧产品分类字段是"L"、"M"或"O"，则牌号（钢级）字段值设为炼钢钢种字段值
                        if 热轧产品分类值 in ["L", "M", "O"]:
                            row_data["牌号（钢级）"] = 炼钢钢种值
                        # 若热轧产品分类字段列是"X"且C列值末尾不是"-P"，则添加"-P"
                        elif 热轧产品分类值 == "X" and not 牌号值.endswith("-P"):
                            row_data["牌号（钢级）"] = 牌号值 + "-P"
            
            # 1. 清空除鳞字段所有数据
            if "层号" in target_columns:
                row_data["层号"] = ""
            
            # 2. 填充除鳞字段 - 与HTML文件中的逻辑一致
            if "层号" in target_columns and "牌号（钢级）" in row_data:
                # 获取转换后的牌号
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                
                # 检查牌号是否匹配除鳞钢种列表
                需要除鳞 = self.匹配除鳞钢种(brand, removePhosphorusList)
                
                # 检查是否为回炉坯（尝试多种可能的字段名）
                回炉坯值 = ""
                是回炉坯 = False
                
                # 尝试不同的回炉坯字段名
                回炉坯字段名列表 = ["回炉坯", "板坯炉后拒收次数"]
                
                for 字段名 in 回炉坯字段名列表:
                    if 字段名 in row_data:
                        回炉坯值 = row_data.get(字段名, "")
                        break
                
                # 检查回炉坯值
                是回炉坯 = (回炉坯值 != 0 and 回炉坯值 != "" and 回炉坯值 is not None)
                
                # 根据需要填充除鳞字段
                除鳞值 = ""
                if 需要除鳞:
                    除鳞值 = "Y"
                else:
                    # 如果没有匹配，填充空白
                    除鳞值 = ""
                
                # 如果是回炉坯，在除鳞字段前添加"回"
                if 是回炉坯:
                    if 除鳞值:
                        除鳞值 = "回" + 除鳞值
                    else:
                        除鳞值 = "回"
                
                # 检查牌号是否在APS钢种列表中
                if brand and apsGrades:
                    在APS列表中 = brand in apsGrades
                    if not 在APS列表中:
                        # 如果不在APS列表中，添加"无APS"标识
                        if 除鳞值:
                            除鳞值 = 除鳞值 + "无APS"
                        else:
                            除鳞值 = "无APS"
                
                # 最后设置除鳞字段的值
                row_data["层号"] = 除鳞值
            
            # 3. 添加标记逻辑
            # 重置需标注标记
            row_data["需标注"] = False
            row_data["减宽超标"] = False
            row_data["低轧宽标记"] = False
            
            # 检查坯厚是否>230，如果是则标记需标注
            if "坯厚" in row_data:
                坯厚值 = row_data.get("坯厚", 0)
                try:
                    坯厚数值 = float(坯厚值) if 坯厚值 != "" else 0
                    if 坯厚数值 > 230:
                        row_data["需标注"] = True
                except (ValueError, TypeError):
                    pass
            
            # 检查牌号是否在APS列表中，如果不在则标记需标注
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无APS块数 += 1
                    row_data["需标注"] = True
                    包含无APS = True
                    if brand not in 已添加无APS的钢种:
                        已添加无APS的钢种.add(brand)
                        无APS钢种数 += 1
            
            # 处理调宽字段 - 如果调宽为"1"，则进行特殊处理
            if "板坯宽度调宽标记" in row_data and str(row_data.get("板坯宽度调宽标记", "")).strip() == "1":
                if "板坯头部宽度" in row_data and "板坯尾部宽度" in row_data and "坯宽" in row_data:
                    板坯头部宽度值 = row_data.get("板坯头部宽度", 0)
                    板坯尾部宽度值 = row_data.get("板坯尾部宽度", 0)
                    
                    try:
                        板坯头部宽度值 = float(板坯头部宽度值) if 板坯头部宽度值 != "" else 0
                        板坯尾部宽度值 = float(板坯尾部宽度值) if 板坯尾部宽度值 != "" else 0
                    except (ValueError, TypeError):
                        板坯头部宽度值 = 0
                        板坯尾部宽度值 = 0
                    
                    调宽差值 = 板坯头部宽度值 - 板坯尾部宽度值
                    row_data["板坯宽度调宽标记"] = 调宽差值
                    
                    坯宽新值 = max(板坯头部宽度值, 板坯尾部宽度值)
                    row_data["坯宽"] = 坯宽新值
                    
                    if "轧宽" in row_data:
                        轧宽值 = row_data.get("轧宽", 0)
                        try:
                            轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                        except (ValueError, TypeError):
                            轧宽值 = 0
                        减宽新值 = 坯宽新值 - 轧宽值
                        if 减宽新值 >= 240:
                            减宽超标块数 += 1
                            row_data["减宽超标"] = True
                            row_data["需标注"] = True
                        elif 减宽新值 < 0:
                            逆宽轧制板坯数 += 1
                            row_data["减宽超标"] = True
                            row_data["需标注"] = True
                        row_data["侧压量"] = 减宽新值
            
            # 只有在调宽不为"1"时，才检查"侧压量"字段
            if "板坯宽度调宽标记" not in row_data or str(row_data.get("板坯宽度调宽标记", "")).strip() != "1":
                减宽值 = 0
                if "侧压量" in row_data:
                    减宽值 = row_data.get("侧压量", 0)
                
                try:
                    减宽值 = float(减宽值) if 减宽值 != "" else 0
                except (ValueError, TypeError):
                    减宽值 = 0
                
                if 减宽值 >= 240:
                    减宽超标块数 += 1
                    row_data["减宽超标"] = True
                    row_data["需标注"] = True
                elif 减宽值 < 0:
                    逆宽轧制板坯数 += 1
                    row_data["减宽超标"] = True
                    row_data["需标注"] = True
            
            # 检查轧宽+（余量）是否<=920，如果是则添加标记
            if "轧宽+（余量）" in row_data:
                轧宽余量值 = row_data.get("轧宽+（余量）", "")
                try:
                    轧宽余量数值 = float(轧宽余量值) if 轧宽余量值 != "" else 0
                    if 轧宽余量数值 <= 920:
                        row_data["轧宽+（余量）"] = str(int(轧宽余量数值)) + "Δ"
                        row_data["低轧宽标记"] = True
                        row_data["需标注"] = True
                        低轧宽板坯数 += 1
                        if 轧宽余量数值 < 860:
                            极低轧宽板坯数 += 1
                except (ValueError, TypeError):
                    pass
            
            # 5. 填充公差带字段
            if "碳" in row_data and "宽度负公差" in row_data and "宽度正公差" in row_data:
                负公差值 = row_data.get("宽度负公差", "")
                正公差值 = row_data.get("宽度正公差", "")
                
                # 处理负公差值
                if isinstance(负公差值, (int, float)):
                    if 负公差值.is_integer():
                        负公差值 = str(int(负公差值))
                    else:
                        负公差值 = f"{负公差值:.1f}"
                else:
                    负公差值 = str(负公差值).strip()
                
                # 处理正公差值
                if isinstance(正公差值, (int, float)):
                    if 正公差值.is_integer():
                        正公差值 = str(int(正公差值))
                    else:
                        正公差值 = f"{正公差值:.1f}"
                else:
                    正公差值 = str(正公差值).strip()
                
                # 填充公差带：负公差 + "～" + 正公差
                row_data["碳"] = 负公差值 + "～" + 正公差值
                
                # 检查正公差是否<=15，如果是则标注*
                try:
                    正公差数值 = float(row_data.get("宽度正公差", 0))
                    if 正公差数值 <= 15:
                        # 在公差带标注*
                        row_data["碳"] = row_data["碳"] + "*"
                        # 在钢卷号标注*
                        if "钢卷号" in row_data:
                            row_data["钢卷号"] = str(row_data["钢卷号"]) + "*"
                except (ValueError, TypeError):
                    pass
            
            # 将处理后的数据添加到列表
            all_row_data.append(row_data)
        
        # 9. 写入表头
        # 第一行：大标题"轧制计划明细表"
        new_sheet.write_merge(0, 0, 0, 标题结束列, "轧制计划明细表", style_title)
        
        # 准备提示信息列表
        提示信息列表 = []
        序号 = 1
        
        if 无APS钢种数 > 0:
            无APS钢种列表 = ", ".join(sorted(已添加无APS的钢种))
            提示信息列表.append(f"{序号}.无APS钢种{无APS钢种数}个{无APS块数}块({无APS钢种列表})")
            序号 += 1
        if 减宽超标块数 > 0:
            提示信息列表.append(f"{序号}.减宽量超标{减宽超标块数}块")
            序号 += 1
        if 逆宽轧制板坯数 > 0:
            提示信息列表.append(f"{序号}.逆宽轧制板坯{逆宽轧制板坯数}块")
            序号 += 1
        if 低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有轧宽低于930板坯{低轧宽板坯数}块，注意定宽最小辊缝要求")
            序号 += 1
        if 极低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有低于860的板坯{极低轧宽板坯数}块，注意E2设定值")
            序号 += 1
        
        # 计算提示信息行数（先左右再上下，每行显示2条）
        if len(提示信息列表) == 0:
            提示信息行数 = 1  # 至少有一行（空行）
        else:
            提示信息行数 = (len(提示信息列表) + 1) // 2  # 向上取整，每行2条
        
        # 字段列名行号 = 提示信息起始行(1) + 提示信息行数
        字段列名行号 = 1 + 提示信息行数
        
        # 找到各列的索引
        轧宽列索引 = -1
        订宽列索引 = -1
        除鳞列索引 = -1
        强度列索引 = -1
        粗轧报信列索引 = -1
        装炉顺列索引 = -1
        牌号列索引 = -1
        序号列索引 = 0  # 假设序号是第一列
        钢卷号列索引 = 1  # 假设钢卷号是第二列
        
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "轧宽":
                轧宽列索引 = col_idx
            elif 映射后的列名 == "订宽":
                订宽列索引 = col_idx
            elif 映射后的列名 == "除鳞":
                除鳞列索引 = col_idx
            elif 映射后的列名 == "强度":
                强度列索引 = col_idx
            elif 映射后的列名 == "粗轧报信":
                粗轧报信列索引 = col_idx
            elif 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
            elif 映射后的列名 == "牌号（钢级）":
                牌号列索引 = col_idx
        
        # 第二行及以下：计划号、块数、提示信息、打印时间
        # 序号和钢卷号列合并，填充计划号信息
        new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 序号列索引, 钢卷号列索引, f"计划号：{计划号}", style_header_info)
        
        # 牌号（钢级）列填充块数信息
        if 牌号列索引 >= 0:
            new_sheet.write(字段列名行号 - 1, 牌号列索引, f"块数：{块数} 块", style_header_info)
        
        # 除鳞到轧宽列和订宽到强度列合并填充提示信息
        # 提示信息显示顺序：先左右，再上下
        if 除鳞列索引 >= 0 and 轧宽列索引 >= 0 and 订宽列索引 >= 0 and 强度列索引 >= 0:
            # 计算需要的行数（每行显示2条提示信息）
            提示信息总行数 = (len(提示信息列表) + 1) // 2  # 向上取整
            for i in range(提示信息总行数):
                # 左列（除鳞到轧宽）：显示第 i*2 条提示信息
                左列索引 = i * 2
                if 左列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 除鳞列索引, 轧宽列索引, 提示信息列表[左列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 除鳞列索引, 轧宽列索引, "", style_header_info)
                
                # 右列（订宽到强度）：显示第 i*2+1 条提示信息
                右列索引 = i * 2 + 1
                if 右列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 订宽列索引, 强度列索引, 提示信息列表[右列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 订宽列索引, 强度列索引, "", style_header_info)
        elif 除鳞列索引 >= 0 and 轧宽列索引 >= 0:
            # 如果只有除鳞到轧宽列
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 除鳞列索引, 轧宽列索引, 提示信息, style_header_info)
        elif 订宽列索引 >= 0 and 强度列索引 >= 0:
            # 如果只有订宽到强度列
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 订宽列索引, 强度列索引, 提示信息, style_header_info)
        
        # 粗轧报信列填充打印时间
        if 粗轧报信列索引 >= 0:
            new_sheet.write(字段列名行号 - 1, 粗轧报信列索引, f"打印时间：{当前时间}", style_time)
        
        # 设置行高（固定23pt = 460 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 460
            new_sheet.row(i).height_mismatch = True
        
        # 字段列名（使用内外边框线样式）
        粗轧报信字段名 = ""
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            new_sheet.write(字段列名行号, col_idx, 映射后的列名, style_header_border)
            # 记录粗轧报信字段名用于计算行高
            if 映射后的列名 == "粗轧报信":
                粗轧报信字段名 = 映射后的列名
        
        # 设置字段列名行的行高（固定23pt = 460 twips）
        new_sheet.row(字段列名行号).height = 460
        new_sheet.row(字段列名行号).height_mismatch = True
        
        # 10. 写入数据
        for row_idx, row_data in enumerate(all_row_data):
            new_row_idx = 字段列名行号 + row_idx + 1
            for col_idx, col_name in enumerate(target_columns):
                value = row_data.get(col_name, "")
                映射后的列名 = 字段名映射.get(col_name, col_name)
                
                # 判断是否为第一列或装炉顺列（用于边框处理）
                is_first_column = (col_idx == 0)
                is_last_column = (col_idx == 装炉顺列索引)
                
                # 根据列名应用不同的样式
                if 映射后的列名 == "粗轧报信":
                    # 粗轧报信使用14pt自动换行样式（左对齐）
                    new_sheet.write(new_row_idx, col_idx, value, style_data_wrap_14pt)
                elif 映射后的列名 == "轧宽":
                    # 轧宽使用14pt虚线边框样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_14pt_dashed)
                elif 映射后的列名 == "减宽":
                    # 减宽使用14pt样式
                    # 检查减宽值是否>=240或<0，如果是，则使用双横线样式
                    减宽超标 = row_data.get("减宽超标", False)
                    需标注 = row_data.get("需标注", False)
                    # 减宽字段不要小数点，转为整数
                    try:
                        if value:
                            减宽数值 = float(value)
                            value = str(int(减宽数值))
                    except (ValueError, TypeError):
                        pass
                    if 需标注:
                        value = str(value) + "Δ"
                    if 减宽超标:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_14pt)
                elif 映射后的列名 == "除鳞" or 映射后的列名 == "公差带":
                    # 除鳞和公差带使用12pt虚线边框样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_dashed)
                elif 映射后的列名 == "牌号（钢级）":
                    # 牌号（钢级）使用12pt左对齐样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_left)
                elif 映射后的列名 == "轧厚":
                    # 轧厚使用12pt样式，并保留小数点后1位（不四舍五入）
                    try:
                        import math
                        if isinstance(value, (int, float)):
                            # 使用math.floor保留1位小数，不四舍五入
                            if value >= 0:
                                value = math.floor(value * 10) / 10
                            else:
                                value = math.ceil(value * 10) / 10
                        elif isinstance(value, str) and value.strip():
                            # 处理字符串类型的数字
                            num_val = float(value)
                            if num_val >= 0:
                                value = math.floor(num_val * 10) / 10
                            else:
                                value = math.ceil(num_val * 10) / 10
                        # 格式化为带1位小数的字符串，确保Excel正确显示
                        value = f"{value:.1f}"
                    except (ValueError, TypeError):
                        pass  # 如果转换失败，保持原值
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt)
                elif 映射后的列名 in ["去向", "坯厚", "坯宽", "坯长", "中厚", "RT2"]:
                    # 这些字段使用12pt样式
                    # 坯厚字段 - 检查是否需要标注（坯厚>230添加三角符号）
                    if 映射后的列名 == "坯厚":
                        # 坯厚值转为整数，去掉小数点
                        try:
                            if value:
                                坯厚数值 = float(value)
                                if 坯厚数值 == int(坯厚数值):
                                    value = str(int(坯厚数值))
                                else:
                                    value = str(坯厚数值)
                                # 只在坯厚>230时添加标注
                                if 坯厚数值 > 230:
                                    value = value + "Δ"
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt)
                elif 映射后的列名 == "钢卷号":
                    # 钢卷号使用16pt样式
                    # 检查是否需要标注（添加三角符号）
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    # 第一列左侧需要实线边框
                    if is_first_column:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_16pt_left_border)
                    else:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_16pt)
                elif 映射后的列名 == "强度":
                    # 强度字段只取个位数值
                    try:
                        if value:
                            强度数值 = float(value)
                            # 只取个位数值
                            个位数值 = int(强度数值) % 10
                            value = str(个位数值)
                    except (ValueError, TypeError):
                        pass
                    # 装炉顺列右侧需要实线边框
                    if is_last_column:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_right_border)
                    else:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_12pt)
                elif 映射后的列名 == "序号":
                    # 序号列（第一列）左侧需要实线边框
                    if is_first_column:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_left_border)
                    else:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_12pt)
                elif 映射后的列名 == "装炉顺":
                    # 装炉顺列（最后一列）右侧需要实线边框
                    # 使用存储的装炉顺值
                    装炉顺 = row_data.get("装炉顺", "")
                    if is_last_column:
                        new_sheet.write(new_row_idx, col_idx, 装炉顺, style_data_12pt_right_border)
                    else:
                        new_sheet.write(new_row_idx, col_idx, 装炉顺, style_data_12pt)
                else:
                    # 其他列使用默认样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data)
            
            # 设置数据行行高为23pt（460 twips）
            # 检查粗轧报信字段内容长度，如果内容较长需要增加行高
            粗轧报信列索引 = -1
            for col_idx, col_name in enumerate(target_columns):
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "粗轧报信":
                    粗轧报信列索引 = col_idx
                    break
            
            # 根据内容长度计算行高（至少23pt）
            if 粗轧报信列索引 >= 0:
                粗轧报信值 = row_data.get("粗轧报信", "")
                if 粗轧报信值:
                    内容 = str(粗轧报信值)
                    内容长度 = len(内容)
                    # 粗轧报信列宽33字符，但14pt字体下实际每行约显示18-20个字符
                    每行字符数 = 19  # 进一步减少，确保准确
                    # 计算需要的行数
                    需要行数 = max(1, (内容长度 + 每行字符数 - 1) // 每行字符数)
                    # 增加安全系数，确保完整显示（增加1行）
                    需要行数 = 需要行数 + 1
                    # 每行高度（14pt字体需要约25pt行高）
                    每行高度 = 460  # 23pt
                    # 计算总行高（至少23pt）
                    计算行高 = max(460, 每行高度 * 需要行数)
                    # 设置行高（固定23pt或根据内容动态调整）
                    new_sheet.row(new_row_idx).height = 计算行高
                    new_sheet.row(new_row_idx).height_mismatch = True
                else:
                    # 无内容时使用默认行高（23pt = 460 twips）
                    new_sheet.row(new_row_idx).height = 460
                    new_sheet.row(new_row_idx).height_mismatch = True
            else:
                # 其他行使用默认行高（23pt = 460 twips）
                new_sheet.row(new_row_idx).height = 460
                new_sheet.row(new_row_idx).height_mismatch = True
        
        # 11. 保存文件
        new_workbook.save(file_path)
        
        # 释放资源
        workbook.release_resources()
        
        # 处理无APS标记
        # 从文件路径中提取计划号
        plan_no = os.path.basename(file_path).replace('.xls', '')
        # 根据包含无APS标记更新no_aps_plans集合
        if 包含无APS:
            self.no_aps_plans.add(plan_no)
            print(f"✓ 计划 {plan_no} 标注为无APS")
        else:
            # 如果之前标注了无APS，现在移除
            if plan_no in self.no_aps_plans:
                self.no_aps_plans.remove(plan_no)
                print(f"✓ 计划 {plan_no} 移除无APS标注")
        # 保存无APS计划状态
        self.save_no_aps_plans()
    
    def show_selected(self):
        """显示选中项 - 打开选定计划文件到最前面"""
        if not self.selected_items:
            self.custom_messagebox("警告", "请先选择计划号")
            return
        
        # 加载最新的状态
        self.load_data()
        
        # 获取选中的计划号
        selected_plans = [self.plan_data[i]['plan_no'] for i in self.selected_items]
        
        # 获取计划号文件夹路径
        plan_dir = os.path.join(self.plan_dir, "计划号")
        backup_dir = os.path.join(plan_dir, "backup")
        
        # 检查选中的计划是否满足显示条件
        invalid_plans = []
        valid_files = []
        
        for plan_no in selected_plans:
            # 获取计划数据
            plan_info = None
            for item in self.plan_data:
                if item['plan_no'] == plan_no:
                    plan_info = item
                    break
            
            if plan_info is None:
                invalid_plans.append(f"{plan_no} (计划不存在)")
                continue
            
            # 检查是否标注为无文件
            if plan_info['status'] == '无文件':
                invalid_plans.append(f"{plan_no} (标注为无文件)")
                continue
            
            # 检查文件是否存在（先检查计划号文件夹，再检查backup目录）
            file_path = os.path.join(plan_dir, f"{plan_no}.xls")
            if not os.path.exists(file_path):
                # 如果已打印，检查backup目录
                if plan_no in self.printed_plans:
                    backup_file_path = os.path.join(backup_dir, f"{plan_no}.xls")
                    if os.path.exists(backup_file_path):
                        file_path = backup_file_path
                        print(f"✓ 从backup目录找到文件: {plan_no}.xls")
                    else:
                        invalid_plans.append(f"{plan_no} (文件不存在)")
                        continue
                else:
                    invalid_plans.append(f"{plan_no} (文件不存在)")
                    continue
            
            # 如果未处理，先处理该计划
            if plan_no not in self.processed_plans:
                print(f"计划 {plan_no} 未处理，正在处理...")
                try:
                    self.run_excel_macro_with_pandas(file_path)
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                except Exception as e:
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    invalid_plans.append(f"{plan_no} (处理失败: {str(e)})")
                    continue
            
            valid_files.append((plan_no, file_path))
        
        # 如果有不符合条件的计划，显示提示
        # 保存已处理计划状态
        if valid_files:
            self.save_processed_plans()
            # 刷新列表显示
            self.update_listbox()
        
        if invalid_plans:
            self.custom_messagebox("警告", f"以下计划号不符合显示条件：\n\n" + "\n".join(invalid_plans) + "\n\n只有没有标注无文件且已处理的计划才能显示")
            return
        
        if not valid_files:
            self.custom_messagebox("提示", "没有符合条件的计划可以显示")
            return
        
        # 打开符合条件的文件
        import subprocess
        import time
        
        for plan_no, file_path in valid_files:
            try:
                print(f"正在打开: {plan_no}.xls")
                # 使用start命令打开文件
                subprocess.Popen(['start', '', file_path], shell=True)
                print(f"✓ 已打开: {plan_no}.xls")
            except Exception as e:
                print(f"✗ 打开失败 {plan_no}.xls: {str(e)}")
                self.custom_messagebox("错误", f"打开文件失败: {plan_no}.xls\n\n{str(e)}")
    
    def print_selected(self):
        """打印选中项 - 打印第一列到装炉顺列，包括表头"""
        if not self.selected_items:
            self.custom_messagebox("警告", "请先选择计划号")
            return
        
        # 加载最新的状态
        self.load_data()
        
        # 获取选中的计划号
        selected_plans = [self.plan_data[i]['plan_no'] for i in self.selected_items]
        
        # 创建进度窗口
        import tkinter as tk
        from tkinter import ttk
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("打印进度")
        progress_window.geometry("600x400")
        progress_window.resizable(True, True)
        
        # 计算居中位置
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (400 // 2)
        progress_window.geometry(f"600x400+{x}+{y}")
        
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="准备开始打印...", font=("宋体", 14))
        progress_label.pack(pady=20)
        
        detail_label = tk.Label(progress_window, text="", font=("宋体", 12), fg="gray")
        detail_label.pack(pady=10)
        
        progress_window.update()
        
        def update_progress(main_msg, detail_msg=""):
            """更新进度显示"""
            progress_label.config(text=main_msg)
            if detail_msg:
                detail_label.config(text=detail_msg)
            progress_window.update()
            print(f"[打印进度] {main_msg} {detail_msg}")
        
        # 获取计划号文件夹路径
        plan_dir = os.path.join(self.plan_dir, "计划号")
        backup_dir = os.path.join(plan_dir, "backup")
        
        # 构建选中计划号的文件路径列表
        selected_files = []
        update_progress("正在检查文件...", f"共 {len(selected_plans)} 个计划号")
        
        for plan_no in selected_plans:
            # 首先检查计划号文件夹
            file_path = os.path.join(plan_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                selected_files.append((plan_no, file_path))
                update_progress("正在检查文件...", f"找到文件: {plan_no}.xls")
            else:
                # 如果已打印，检查backup目录
                if plan_no in self.printed_plans:
                    backup_file_path = os.path.join(backup_dir, f"{plan_no}.xls")
                    if os.path.exists(backup_file_path):
                        selected_files.append((plan_no, backup_file_path))
                        update_progress("正在检查文件...", f"从backup目录找到文件: {plan_no}.xls")
                        print(f"✓ 从backup目录找到文件: {plan_no}.xls")
                    else:
                        update_progress("正在检查文件...", f"文件不存在: {plan_no}.xls")
                        print(f"✗ 文件不存在: {plan_no}.xls")
                else:
                    update_progress("正在检查文件...", f"文件不存在: {plan_no}.xls")
                    print(f"✗ 文件不存在: {plan_no}.xls")
        
        if not selected_files:
            progress_window.destroy()
            self.custom_messagebox("提示", "选中的计划号没有对应的文件")
            return
        
        # 检查并处理未处理的计划
        processed_plans = []
        failed_plans = []
        
        update_progress("正在处理计划...", f"共 {len(selected_files)} 个计划需要处理")
        
        for i, (plan_no, file_path) in enumerate(selected_files):
            # 如果未处理，先处理该计划
            if plan_no not in self.processed_plans:
                update_progress("正在处理计划...", f"处理 {plan_no} ({i+1}/{len(selected_files)})")
                try:
                    self.run_excel_macro_with_pandas(file_path)
                    update_progress("正在处理计划...", f"已处理: {plan_no}")
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    processed_plans.append(plan_no)
                except Exception as e:
                    error_msg = f"处理失败: {str(e)}"
                    update_progress("正在处理计划...", f"{plan_no}: {error_msg}")
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    failed_plans.append(f"{plan_no} (处理失败: {str(e)})")
                    import traceback
                    traceback.print_exc()
        
        # 保存已处理计划状态
        if processed_plans:
            self.save_processed_plans()
            # 保存无APS计划状态
            self.save_no_aps_plans()
            # 刷新列表显示
            self.update_listbox()
        
        # 如果有处理失败的计划，显示提示
        if failed_plans:
            progress_window.destroy()
            self.custom_messagebox("警告", f"以下计划号处理失败：\n\n" + "\n".join(failed_plans) + "\n\n这些计划将不会被打印")
            # 移除处理失败的计划
            selected_files = [(plan_no, file_path) for plan_no, file_path in selected_files if plan_no not in [p.split(' ')[0] for p in failed_plans]]
            
            # 重新创建进度窗口
            progress_window = tk.Toplevel(self.root)
            progress_window.title("打印进度")
            progress_window.geometry("600x400")
            progress_window.resizable(True, True)
            
            # 计算居中位置
            screen_width = progress_window.winfo_screenwidth()
            screen_height = progress_window.winfo_screenheight()
            x = (screen_width // 2) - (600 // 2)
            y = (screen_height // 2) - (400 // 2)
            progress_window.geometry(f"600x400+{x}+{y}")
            
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = tk.Label(progress_window, text="准备开始打印...", font=("宋体", 14))
            progress_label.pack(pady=20)
            
            detail_label = tk.Label(progress_window, text="", font=("宋体", 12), fg="gray")
            detail_label.pack(pady=10)
            
            progress_window.update()
            
            def update_progress(main_msg, detail_msg=""):
                """更新进度显示"""
                progress_label.config(text=main_msg)
                if detail_msg:
                    detail_label.config(text=detail_msg)
                progress_window.update()
                print(f"[打印进度] {main_msg} {detail_msg}")
        
        if not selected_files:
            progress_window.destroy()
            self.custom_messagebox("提示", "没有符合条件的计划可以打印")
            return
        
        # 打印每个文件
        success_count = 0
        failed_count = 0
        failed_files = []
        success_files = []
        
        update_progress("正在打印文件...", f"共 {len(selected_files)} 个计划需要打印")
        
        for i, (plan_no, file_path) in enumerate(selected_files):
            try:
                update_progress("正在打印文件...", f"打印 {plan_no} ({i+1}/{len(selected_files)})")
                print(f"开始打印: {plan_no}.xls")
                success = self.print_excel_file(file_path)
                if success:
                    success_count += 1
                    success_files.append(plan_no)
                    update_progress("正在打印文件...", f"已打印: {plan_no}")
                    print(f"✓ 已打印: {plan_no}.xls")
                    # 标记为已打印
                    self.printed_plans.add(plan_no)
                else:
                    failed_count += 1
                    failed_files.append(plan_no)
                    update_progress("正在打印文件...", f"打印失败: {plan_no}")
                    print(f"✗ 打印失败 {plan_no}.xls")
            except Exception as e:
                failed_count += 1
                failed_files.append(plan_no)
                error_msg = f"打印失败: {str(e)}"
                update_progress("正在打印文件...", f"{plan_no}: {error_msg}")
                print(f"✗ 打印失败 {plan_no}.xls: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # 保存已打印计划状态
        if success_count > 0:
            self.save_printed_plans()
            # 刷新列表显示
            self.update_listbox()
        
        # 将打印成功的文件移动到backup目录
        if success_files:
            update_progress("正在移动文件...", "将打印成功的文件移动到backup目录")
            import shutil
            plan_dir = os.path.join(self.plan_dir, "计划号")
            backup_dir = os.path.join(plan_dir, "backup")
            
            # 创建backup目录（如果不存在）
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
                update_progress("正在移动文件...", f"创建backup目录: {backup_dir}")
                print(f"✓ 创建backup目录: {backup_dir}")
            
            # 移动文件
            moved_count = 0
            for i, plan_no in enumerate(success_files):
                update_progress("正在移动文件...", f"移动 {plan_no} ({i+1}/{len(success_files)})")
                src_file = os.path.join(plan_dir, f"{plan_no}.xls")
                dst_file = os.path.join(backup_dir, f"{plan_no}.xls")
                
                try:
                    if os.path.exists(src_file):
                        # 如果目标文件已存在，先删除
                        if os.path.exists(dst_file):
                            os.remove(dst_file)
                            print(f"✓ 删除已存在的备份文件: {plan_no}.xls")
                        
                        shutil.move(src_file, dst_file)
                        print(f"✓ 已移动文件到backup: {plan_no}.xls")
                        moved_count += 1
                except Exception as e:
                    print(f"✗ 移动文件失败 {plan_no}.xls: {str(e)}")
            
            update_progress("正在移动文件...", f"成功移动 {moved_count} 个文件到backup目录")
            print(f"\n文件移动完成: 成功移动 {moved_count} 个文件到backup目录")
        
        # 销毁进度窗口
        progress_window.destroy()
        
        # 显示结果 - 使用自定义窗口
        import tkinter as tk
        from tkinter import ttk
        
        # 创建自定义窗口
        result_window = tk.Toplevel(self.root)
        result_window.title("完成")
        result_window.geometry("600x450")
        result_window.resizable(True, True)
        
        # 计算居中位置
        screen_width = result_window.winfo_screenwidth()
        screen_height = result_window.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (450 // 2)
        result_window.geometry(f"600x450+{x}+{y}")
        
        # 设置窗口样式
        result_window.configure(bg='#f0f0f0')
        
        # 创建主框架
        main_frame = tk.Frame(result_window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="打印完成！",
            font=('宋体', 24, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # 统计信息
        stats_frame = tk.Frame(main_frame, bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, pady=10)
        
        stats_label = tk.Label(
            stats_frame,
            text=f"成功: {success_count} 个 | 失败: {failed_count} 个",
            font=('宋体', 16),
            bg='#f0f0f0'
        )
        stats_label.pack()
        
        # 成功的计划号
        if success_files:
            success_frame = tk.Frame(main_frame, bg='#f0f0f0')
            success_frame.pack(fill=tk.X, pady=10)
            
            success_label = tk.Label(
                success_frame,
                text=f"成功的计划号: {', '.join(success_files)}",
                font=('宋体', 14),
                bg='#f0f0f0',
                justify=tk.LEFT,
                wraplength=500
            )
            success_label.pack(anchor='w')
        
        # 失败的计划号
        if failed_files:
            failed_frame = tk.Frame(main_frame, bg='#f0f0f0')
            failed_frame.pack(fill=tk.X, pady=10)
            
            failed_label = tk.Label(
                failed_frame,
                text=f"失败的计划号: {', '.join(failed_files)}",
                font=('宋体', 14),
                bg='#f0f0f0',
                justify=tk.LEFT,
                wraplength=500
            )
            failed_label.pack(anchor='w')
        
        # 确定按钮
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(side=tk.BOTTOM, pady=20)
        
        ok_btn = ttk.Button(
            btn_frame,
            text="确定",
            command=result_window.destroy,
            width=10
        )
        ok_btn.pack()
        
        # 确保窗口在最前面
        result_window.transient(self.root)
        result_window.grab_set()
        result_window.lift()
        result_window.focus_force()
    
    def print_excel_file(self, file_path):
        """打印Excel文件 - 打印第一列到装炉顺列，包括表头
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            bool: 是否成功打印
        """
        try:
            import xlrd
            
            # 读取Excel文件
            success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
            if not success:
                raise Exception(f"读取文件失败: {result}")
            
            workbook = result
            sheet = workbook.sheet_by_index(0)
            
            # 先查找字段列名行（包含"序号"、"钢卷号"等字段名的行）
            字段列名行号 = -1
            for row_idx in range(min(10, sheet.nrows)):  # 检查前10行
                row_has_field_names = False
                for col_idx in range(sheet.ncols):
                    cell_value = str(sheet.cell_value(row_idx, col_idx))
                    # 检查是否包含常见字段名
                    if any(field in cell_value for field in ["序号", "钢卷号", "牌号", "坯厚", "轧厚", "轧宽", "装炉顺"]):
                        row_has_field_names = True
                        break
                if row_has_field_names:
                    字段列名行号 = row_idx
                    break
            
            if 字段列名行号 == -1:
                print("未找到字段列名行，假设为第2行")
                字段列名行号 = 2
            
            print(f"字段列名行号: {字段列名行号}")
            
            # 从字段列名行获取所有列名
            current_columns = []
            for i in range(sheet.ncols):
                current_columns.append(sheet.cell_value(字段列名行号, i))
            
            print(f"列名: {current_columns}")
            
            # 字段名映射
            字段名映射 = {
                "序号": "序号",
                "钢卷号": "钢卷号",
                "牌号": "牌号（钢级）",
                "牌号（钢级）": "牌号（钢级）",
                "坯厚": "坯厚",
                "坯宽": "坯宽",
                "坯长": "坯长",
                "中厚": "中厚",
                "RT2": "RT2",
                "去向": "去向",
                "轧厚": "轧厚",
                "轧宽": "轧宽",
                "减宽": "减宽",
                "订宽": "订宽",
                "除鳞": "除鳞",
                "公差带": "公差带",
                "强度": "强度",
                "粗轧报信": "粗轧报信",
                "装炉顺序号": "装炉顺序号",
                "装炉顺": "装炉顺"
            }
            
            # 找到装炉顺列的索引（查找"装炉顺序号"列，因为实际存储的列名是"装炉顺序号"）
            装炉顺列索引 = -1
            for col_idx, col_name in enumerate(current_columns):
                # 直接查找"装炉顺序号"列（实际存储的列名）
                if col_name == "装炉顺序号":
                    装炉顺列索引 = col_idx
                    break
                # 如果没有找到，尝试通过映射查找"装炉顺"
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "装炉顺":
                    装炉顺列索引 = col_idx
                    break
            
            if 装炉顺列索引 == -1:
                print("未找到装炉顺序号/装炉顺列，将打印所有列")
                装炉顺列索引 = sheet.ncols - 1
            else:
                print(f"找到装炉顺序号/装炉顺列，索引: {装炉顺列索引}")
            
            # 计算打印范围：第一列(0)到装炉顺列
            print_col_start = 0
            print_col_end = 装炉顺列索引
            
            # 表头总行数 = 字段列名行号 + 1（包括字段列名行）
            header_row_count = 字段列名行号 + 1
            
            print(f"字段列名行号: {字段列名行号}, 表头总行数: {header_row_count}")
            
            # 使用win32com调用Excel打印
            try:
                import win32com.client as win32
                excel = win32.Dispatch("Excel.Application")
                excel.Visible = False
                
                # 打开工作簿
                workbook_obj = excel.Workbooks.Open(file_path)
                worksheet = workbook_obj.Worksheets(1)
                
                # 设置打印区域：第一列到装炉顺列，包括表头和数据行
                def get_column_letter(col_idx):
                    """将列索引转换为Excel列字母（A, B, ..., Z, AA, AB, ...）"""
                    if col_idx < 26:
                        return chr(65 + col_idx)
                    else:
                        first_letter = chr(65 + (col_idx // 26) - 1)
                        second_letter = chr(65 + (col_idx % 26))
                        return first_letter + second_letter
                
                col_start_letter = get_column_letter(print_col_start)  # 第一列
                col_end_letter = get_column_letter(print_col_end)  # 装炉顺列对应的字母
                # 打印所有行：从第1行到最后一行（包括表头和数据）
                print_area = f"{col_start_letter}1:{col_end_letter}{sheet.nrows}"
                worksheet.PageSetup.PrintArea = print_area
                
                print(f"打印区域: {print_area} (共{sheet.nrows}行)")
                
                # 打印
                worksheet.PrintOut()
                
                # 关闭工作簿
                workbook_obj.Close(False)
                excel.Quit()
                
                # 释放资源
                workbook.release_resources()
                
                return True
                
            except ImportError:
                print("win32com未安装，使用默认打印方式")
                # 释放资源
                workbook.release_resources()
                
                # 使用系统默认打印
                import subprocess
                import os
                
                # 在Windows上使用默认程序打开并打印
                os.startfile(file_path)
                
                return True
                
        except Exception as e:
            print(f"打印文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== 自动导出依赖方法 ====================
    
    def export_zhuanglu_shunxu(self):
        """导出装炉顺序 - 严格按照点点精灵脚本步骤执行"""
        import time
        log_lines = ["开始导出装炉顺序..."]
        
        # 文件路径 - 使用计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        # 从配置中读取窗口标题
        window_title = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
        
        # 从配置中读取坐标
        zhuanglu_tab = self.coordinates.get("zhuanglu_tab", (261, 87))
        zhuanglu_export = self.coordinates.get("zhuanglu_export_btn", (990, 831))
        
        # 步骤1: 激活目标窗口
        log_lines.append(f"[1/9] 激活目标窗口: {window_title}...")
        try:
            if not self.activate_window(window_title):
                log_lines.append("✗ 激活窗口失败")
                return False, "\n".join(log_lines)
            log_lines.append(f"✓ 已激活窗口: {window_title}")
            time.sleep(0.5)  # 激活窗口后延迟
        except Exception as e:
            log_lines.append(f"✗ 激活窗口失败: {str(e)}")
            return False, "\n".join(log_lines)
        
        # 步骤2: 鼠标点击 - 装炉顺作成管理画面
        log_lines.append(f"[2/9] 鼠标点击: 装炉顺作成管理画面 @ {zhuanglu_tab}...")
        pyautogui.moveTo(zhuanglu_tab[0], zhuanglu_tab[1])
        pyautogui.click()
        time.sleep(0.5)  # 点击后延迟
        log_lines.append("点击完成")
        
        # 步骤3: 键盘按键 - F2
        log_lines.append("[3/9] 键盘按键: F2...")
        pyautogui.press('f2')
        time.sleep(0.5)  # F2后延迟
        log_lines.append("F2键已按下")

        # 步骤4: 延迟 - 500ms
        log_lines.append("[4/9] 延迟: 500ms...")
        time.sleep(0.5)
        log_lines.append("延迟完成")

        # 步骤5: 鼠标点击 - 导出按钮
        log_lines.append(f"[5/9] 鼠标点击: 导出按钮 @ {zhuanglu_export}...")
        pyautogui.moveTo(zhuanglu_export[0], zhuanglu_export[1])
        pyautogui.click()
        time.sleep(1.0)  # 点击后延迟，等待保存对话框弹出
        log_lines.append("导出按钮点击完成，等待保存对话框...")

        # 步骤6: 键盘按键 - 输入"装炉顺序"
        log_lines.append("[6/9] 键盘按键: 输入'装炉顺序'...")
        # 等待对话框完全弹出并获取焦点
        time.sleep(1.0)
        # 使用剪贴板粘贴方式输入，更可靠
        import pyperclip
        pyperclip.copy("装炉顺序")
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)  # 输入后延迟
        log_lines.append("文本已输入")

        # 步骤7: 键盘按键 - Return
        log_lines.append("[7/9] 键盘按键: Return...")
        pyautogui.press('return')
        time.sleep(0.3)  # 回车后延迟
        log_lines.append("回车键已按下")

        # 步骤8: 键盘按键 - Left
        log_lines.append("[8/9] 键盘按键: Left...")
        pyautogui.press('left')
        time.sleep(0.2)  # 左方向键后延迟
        log_lines.append("左方向键已按下")

        # 步骤9: 键盘按键 - Return
        log_lines.append("[9/9] 键盘按键: Return...")
        pyautogui.press('return')
        log_lines.append("回车键已按下")
        
        # 等待导出完成
        log_lines.append("等待导出完成...")
        time.sleep(3)
        
        # 确保所有Excel进程都已关闭（避免文件占用）
        log_lines.append("确保Excel进程已关闭...")
        try:
            import subprocess
            # 强制关闭所有Excel进程
            subprocess.run(['taskkill', '/f', '/im', 'EXCEL.EXE'], capture_output=True)
            time.sleep(2)
            log_lines.append("Excel进程已强制关闭")
        except Exception as e:
            log_lines.append(f"强制关闭Excel进程失败: {str(e)}")
        
        # 刷新计划号列表（使用副本读取方案，避免文件占用）
        log_lines.append("刷新计划号列表...")
        try:
            self.scan_and_rename_plan_files()
            self.refresh_plan_list_from_file()
            log_lines.append("计划号列表刷新完成")
        except Exception as e:
            log_lines.append(f"刷新计划号列表失败: {str(e)}")
        
        log_lines.append("装炉顺序导出操作完成")
        return True, "\n".join(log_lines)
    
    def export_zhizhi_plan_list(self, test_window=None, test_mode=False):
        """导出总计划号列表
        
        参数:
            test_window: 测试窗口标题，如果为None则自动选择
            test_mode: 是否为测试模式（简化版不再使用）
        """
        try:
            import pyautogui
            import time
            
            # 选择测试窗口
            if test_window is None:
                test_window = self.select_test_window()
            if not test_window:
                print("✗ 用户取消选择测试窗口")
                return False
            
            print("\n=== 导出总计划号列表 ===")
            
            # 从配置中读取坐标
            zhizhi_tab = self.coordinates.get("zhizhi_tab", (92, 85))
            plan_select = self.coordinates.get("plan_select", (860, 134))
            zhizhi_export_btn = self.coordinates.get("zhizhi_export_btn", (77, 501))
            
            # 步骤1: 激活窗口
            print("[1/7] 激活窗口...")
            if not self.activate_window(test_window):
                print("✗ 激活窗口失败")
                return False
            time.sleep(0.5)
            
            # 步骤2: 点击轧制计划管理标签
            print(f"[2/7] 点击轧制计划管理标签...")
            pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
            pyautogui.click()
            time.sleep(0.5)
            
            # 步骤3: 选择计划号
            print(f"[3/7] 选择计划号...")
            pyautogui.moveTo(plan_select[0], plan_select[1])
            pyautogui.click()
            time.sleep(0.3)
            
            # 步骤4: 按Home键全选 + 回车确认
            print("[4/7] 按Home键选择所有计划号...")
            pyautogui.press('home')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(0.5)
            
            # 步骤5: 按F2刷新
            print("[5/7] 按F2刷新...")
            pyautogui.press('f2')
            time.sleep(0.5)
            
            # 步骤6: 点击导出按钮
            print(f"[6/7] 点击导出按钮...")
            pyautogui.moveTo(zhizhi_export_btn[0], zhizhi_export_btn[1])
            pyautogui.click()
            time.sleep(1.5)
            
            # 步骤7: 输入文件名并保存
            print("[7/7] 输入文件名并保存...")
            import pyperclip
            pyperclip.copy("总计划号列表")
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('return')
            time.sleep(0.3)
            pyautogui.press('left')
            time.sleep(0.2)
            pyautogui.press('return')
            time.sleep(2)
            
            # 移动文件到计划号文件夹
            print("移动总计划号列表到计划号文件夹...")
            import shutil
            import os
            plan_dir = os.path.join(self.plan_dir, "计划号")
            source_file = os.path.join(self.plan_dir, "总计划号列表.xls")
            target_file = os.path.join(plan_dir, "总计划号列表.xls")
            if os.path.exists(source_file):
                shutil.move(source_file, target_file)
                print(f"✓ 总计划号列表已移动到: {target_file}")
            
            # 重新读取总计划号列表文件，更新缓存并计算坐标
            print("重新读取总计划号列表文件，更新缓存并计算坐标...")
            self.read_zhizhi_plan_list_with_coords()
            
            print("✓ 总计划号列表导出成功")
            return True
            
        except Exception as e:
            print(f"✗ 导出总计划号列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_zhizhi_plan_list_with_coords(self):
        """读取总计划号列表文件，返回计划号到坐标的映射字典
        
        根据设置页面中的第一个计划号坐标和计划号间距，
        计算每个计划号的实际屏幕坐标。
        
        返回: {计划号: (x, y)} 的字典
        """
        try:
            import os
            import shutil
            import xlrd
            
            # 总计划号列表文件路径 - 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            file_path = os.path.join(plan_dir, "总计划号列表.xls")
            
            if not os.path.exists(file_path):
                print(f"总计划号列表文件不存在: {file_path}")
                return None
            
            print(f"读取总计划号列表文件并计算坐标: {file_path}")
            
            # 使用副本读取策略
            temp_file = None
            try:
                # 尝试直接读取
                success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
                if not success:
                    print(f"直接读取失败: {result}，尝试使用副本...")
                    raise PermissionError(result)
            except PermissionError:
                print(f"原文件被占用，尝试使用副本读取...")
                temp_file = file_path + ".tmp"
                shutil.copy2(file_path, temp_file)
                print(f"已创建临时副本: {temp_file}")
                success, result = self.safe_read_excel(temp_file, max_retries=3, retry_delay=0.5)
                if not success:
                    print(f"副本读取也失败: {result}")
                    return None
            
            workbook = result
            sheet = workbook.sheet_by_index(0)
            
            # 查找"序号"列和"计划号"列
            seq_col = -1  # 序号列
            plan_col = -1  # 计划号列
            
            for col in range(sheet.ncols):
                cell_value = sheet.cell_value(0, col)
                if cell_value == "序号":
                    seq_col = col
                elif cell_value == "计划号":
                    plan_col = col
            
            if plan_col == -1:
                print("未找到'计划号'列，尝试使用第一列")
                plan_col = 0
            
            print(f"找到列: 序号列={seq_col}, 计划号列={plan_col}")
            
            # 从配置中读取第一个计划号坐标、间距和偏移量
            first_plan = self.coordinates.get("first_plan", (239, 208))
            plan_spacing = self.coordinates.get("plan_spacing", 21)
            # 第一个计划号的纵坐标偏移量（用于校准中点位置）
            first_plan_offset = self.coordinates.get("first_plan_offset", 0)
            
            first_x = first_plan[0]
            first_y = first_plan[1] + first_plan_offset  # 应用偏移量校准
            
            print(f"第一个计划号原始坐标: ({first_plan[0]}, {first_plan[1]})")
            print(f"第一个计划号偏移量: {first_plan_offset}")
            print(f"第一个计划号校准后坐标: ({first_x}, {first_y})")
            print(f"计划号间距: {plan_spacing} 像素")
            
            # 读取计划号并计算坐标
            plan_coord_map = {}
            zhizhi_plan_list = []  # 临时存储序号和计划号
            
            for row in range(1, sheet.nrows):
                # 读取序号（如果有序号列）
                seq_value = None
                if seq_col != -1:
                    seq_cell = sheet.cell_value(row, seq_col)
                    if seq_cell:
                        if isinstance(seq_cell, float):
                            seq_value = int(seq_cell)
                        else:
                            try:
                                seq_value = int(str(seq_cell).strip())
                            except:
                                seq_value = row  # 如果转换失败，使用行号
                else:
                    seq_value = row  # 如果没有序号列，使用行号作为序号
                
                # 读取计划号
                cell_value = sheet.cell_value(row, plan_col)
                if cell_value:
                    # 处理可能的浮点数格式
                    if isinstance(cell_value, float):
                        if cell_value == int(cell_value):
                            plan_no = str(int(cell_value)).strip()
                        else:
                            plan_no = str(cell_value).strip()
                    else:
                        plan_no = str(cell_value).strip()
                    
                    if plan_no:
                        # 计算坐标：序号从1开始，所以减1得到索引
                        # 第一个计划号(序号=1)的索引是0，使用first_y
                        # 第二个计划号(序号=2)的索引是1，使用first_y + plan_spacing
                        index = seq_value - 1 if seq_value else row - 1
                        coord_y = first_y + (index * plan_spacing)
                        coord_x = first_x
                        
                        plan_coord_map[plan_no] = (coord_x, coord_y)
                        zhizhi_plan_list.append((seq_value, plan_no))
                        print(f"  计划号 {plan_no}: 序号={seq_value}, 索引={index}, 坐标=({coord_x}, {coord_y})")
            
            print(f"\n从总计划号列表计算了 {len(plan_coord_map)} 个计划号的坐标")
            
            # 更新缓存
            self.zhizhi_plan_list = zhizhi_plan_list
            self.zhizhi_plan_coord_map = plan_coord_map
            print(f"已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            
            # 释放workbook资源
            try:
                workbook.release_resources()
            except:
                pass
            
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    print(f"已删除临时副本")
                except:
                    pass
            
            return plan_coord_map
            
        except Exception as e:
            print(f"读取总计划号列表并计算坐标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 确保释放资源
            try:
                if 'workbook' in locals():
                    workbook.release_resources()
            except:
                pass
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return None
    
    def export_single_plan_detail(self, plan_no, plan_coord, plan_detail_export_btn=None, test_window=None):
        """导出单个计划号的明细
        
        按照图片中的步骤执行：
        1. 鼠标点击计划号坐标
        2. 延迟500ms
        3. 鼠标点击导出计划明细按钮
        4. 键盘输入计划号
        5. 按回车确认
        6. 按左方向键（替换覆盖）
        7. 按回车确认
        
        参数:
            plan_no: 计划号
            plan_coord: 计划号的坐标 (x, y)
            plan_detail_export_btn: 导出计划明细按钮坐标，如果为None则使用配置中的坐标
            test_window: 测试窗口标题
            
        返回:
            True - 导出成功
            False - 导出失败
        """
        try:
            import pyautogui
            import time
            
            print(f"\n=== 导出计划 {plan_no} 的明细 ===")
            print(f"计划号坐标: {plan_coord}")
            
            # 选择测试窗口
            if test_window is None:
                test_window = self.select_test_window()
            if not test_window:
                print("✗ 用户取消选择测试窗口")
                return False
            
            # 激活窗口
            if not self.activate_window(test_window):
                print("✗ 激活窗口失败")
                return False
            time.sleep(0.3)
            
            # 获取导出计划明细按钮坐标
            if plan_detail_export_btn is None:
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", (79, 870))
            
            # 步骤1: 鼠标点击计划号坐标
            print(f"[1/7] 点击计划号 {plan_no} 坐标 {plan_coord}...")
            pyautogui.moveTo(plan_coord[0], plan_coord[1])
            pyautogui.click()
            time.sleep(0.5)  # 延迟500ms
            
            # 步骤2: 鼠标点击导出计划明细按钮
            print(f"[2/7] 点击导出计划明细按钮 {plan_detail_export_btn}...")
            pyautogui.moveTo(plan_detail_export_btn[0], plan_detail_export_btn[1])
            pyautogui.click()
            time.sleep(0.5)  # 等待保存对话框弹出
            
            # 步骤3: 键盘输入计划号（使用剪贴板粘贴）
            print(f"[3/7] 输入计划号 '{plan_no}'...")
            import pyperclip
            pyperclip.copy(plan_no)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            
            # 步骤4: 按回车确认
            print("[4/7] 按回车确认...")
            pyautogui.press('return')
            time.sleep(0.3)
            
            # 步骤5: 按左方向键（替换覆盖旧文件）
            print("[5/7] 按左方向键选择覆盖...")
            pyautogui.press('left')
            time.sleep(0.2)
            
            # 步骤6: 按回车确认保存
            print("[6/7] 按回车确认保存...")
            pyautogui.press('return')
            time.sleep(2)  # 等待保存完成
            
            print(f"✓ 计划 {plan_no} 明细导出成功")
            return True
            
        except Exception as e:
            print(f"✗ 导出计划 {plan_no} 明细失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def refresh_plan_list(self, export_zhuanglu=False):
        """刷新计划号列表
        
        直接使用之前新建的 refresh_plan_list_from_file 方法，采用副本读取方案，避免文件占用问题
        
        Args:
            export_zhuanglu: 是否先导出装炉顺序（默认False）
        """
        if export_zhuanglu:
            success, _ = self.export_zhuanglu_shunxu()
            if not success:
                return
        
        # 扫描并重命名计划号文件
        self.scan_and_rename_plan_files()
        
        return self.refresh_plan_list_from_file()
    
    def scan_and_rename_plan_files(self):
        """扫描并重命名计划号文件
        
        只扫描计划号文件夹，不扫描子目录
        对所有xls文件进行更名（装炉顺序.xls、总计划号列表.xls除外）
        """
        try:
            import os
            import xlrd
            
            # 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            # 如果计划号文件夹不存在，创建它
            if not os.path.exists(plan_dir):
                print(f"计划号文件夹不存在，创建: {plan_dir}")
                os.makedirs(plan_dir)
                return
            
            print("\n=== 扫描并重命名计划号文件 ===")
            print(f"扫描目录: {plan_dir}")
            
            # 获取计划号文件夹中的所有文件
            files = os.listdir(plan_dir)
            renamed_count = 0
            skipped_count = 0
            
            for file in files:
                file_path = os.path.join(plan_dir, file)
                
                # 跳过目录
                if os.path.isdir(file_path):
                    continue
                
                # 跳过系统文件
                if file in ["装炉顺序.xls", "总计划号列表.xls", "装炉顺序_显示.xls", "合并文件.xls"]:
                    print(f"跳过系统文件: {file}")
                    skipped_count += 1
                    continue
                
                # 只处理xls和xlsx文件
                if not (file.endswith(".xls") or file.endswith(".xlsx")):
                    continue
                
                # 尝试读取文件获取计划号
                try:
                    success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
                    if not success:
                        print(f"读取文件失败 {file}: {result}")
                        skipped_count += 1
                        continue
                    
                    workbook = result
                    sheet = workbook.sheet_by_index(0)
                    
                    if sheet.nrows < 1:
                        print(f"文件 {file} 没有数据，跳过")
                        skipped_count += 1
                        continue
                    
                    # 查找计划号列
                    plan_col = -1
                    header_row = -1
                    
                    # 在前10行中查找表头
                    for row in range(min(10, sheet.nrows)):
                        for col in range(sheet.ncols):
                            cell_value = str(sheet.cell_value(row, col)).strip()
                            if cell_value == "计划号":
                                plan_col = col
                                header_row = row
                                break
                        if plan_col != -1:
                            break
                    
                    # 如果没有找到计划号列，跳过此文件
                    if plan_col == -1:
                        print(f"文件 {file} 中没有计划号列，跳过")
                        skipped_count += 1
                        continue
                    
                    # 读取计划号
                    plan_no = ""
                    for check_row in range(header_row + 1, min(header_row + 5, sheet.nrows)):
                        cell_value = sheet.cell_value(check_row, plan_col)
                        if isinstance(cell_value, float):
                            if cell_value == int(cell_value):
                                plan_no = str(int(cell_value)).strip()
                            else:
                                plan_no = str(cell_value).strip()
                        else:
                            plan_no = str(cell_value).strip()
                        
                        if plan_no and plan_no != "":
                            break
                    
                    # 如果没有找到计划号，跳过
                    if not plan_no or plan_no == "":
                        print(f"文件 {file} 中没有找到计划号，跳过")
                        skipped_count += 1
                        continue
                    
                    # 检查文件名是否已经是计划号
                    file_name_without_ext = os.path.splitext(file)[0]
                    if file_name_without_ext == plan_no:
                        print(f"文件 {file} 已经是计划号格式，无需重命名")
                        continue
                    
                    # 重命名文件
                    file_ext = os.path.splitext(file)[1]
                    new_file_name = plan_no + file_ext
                    new_file_path = os.path.join(plan_dir, new_file_name)
                    
                    # 检查目标文件是否已存在
                    if os.path.exists(new_file_path):
                        print(f"文件 {file} 需要重命名为 {new_file_name}，但目标文件已存在，跳过")
                        skipped_count += 1
                        continue
                    
                    # 重命名文件
                    os.rename(file_path, new_file_path)
                    print(f"✓ 文件 {file} 已重命名为 {new_file_name}")
                    renamed_count += 1
                    
                    # 释放workbook资源
                    try:
                        workbook.release_resources()
                    except:
                        pass
                    
                except Exception as e:
                    print(f"处理文件 {file} 失败: {str(e)}")
                    skipped_count += 1
                    # 确保释放资源
                    try:
                        if 'workbook' in locals():
                            workbook.release_resources()
                    except:
                        pass
            
            print(f"\n文件扫描完成: 重命名 {renamed_count} 个文件，跳过 {skipped_count} 个文件")
            
        except Exception as e:
            print(f"扫描并重命名文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mark_plan_as_exported(self, plan_no):
        """标记计划号已导出（更新装炉顺序文件中的状态）
        
        参数:
            plan_no: 计划号
        """
        try:
            print(f"标记计划号 {plan_no} 为已导出...")
            
            # 这里可以实现更新Excel文件中的状态列
            # 暂时先添加到已处理集合中
            self.processed_plans.add(plan_no)
            self.save_processed_plans()
            
            print(f"✓ 计划号 {plan_no} 已标记为已导出")
            
        except Exception as e:
            print(f"✗ 标记计划号失败: {str(e)}")
    
    def activate_window(self, window_title):
        """激活指定标题的窗口
        
        Args:
            window_title: 窗口标题
            
        Returns:
            bool: 是否成功激活
        """
        import time
        try:
            import win32gui
            
            def callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    if window_title in win32gui.GetWindowText(hwnd):
                        extra.append(hwnd)
            
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            
            if hwnds:
                win32gui.SetForegroundWindow(hwnds[0])
                return True
            return False
        except Exception as e:
            print(f"激活窗口失败: {str(e)}")
            # 如果win32gui不可用，尝试使用pyautogui
            import pyautogui
            import time
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.typewrite(window_title)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            return True
    
    def select_test_window(self):
        """选择测试窗口
        
        Returns:
            str: 选择的窗口标题，或None如果用户取消
        """
        try:
            import win32gui
            
            # 获取所有可见窗口
            windows = []
            
            def callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        extra.append(title)
            
            win32gui.EnumWindows(callback, windows)
            
            # 过滤掉空标题和系统窗口
            windows = [w for w in windows if w and len(w) > 5]
            
            if not windows:
                print("没有找到可用的窗口")
                return None
            
            # 创建选择窗口
            from tkinter import simpledialog
            
            window = tk.Toplevel(self.root)
            window.title("选择测试窗口")
            window.geometry("400x300")
            window.transient(self.root)
            window.grab_set()
            
            label = tk.Label(window, text="请选择测试窗口:")
            label.pack(pady=10)
            
            listbox = tk.Listbox(window, width=50, height=10)
            for w in windows:
                listbox.insert(tk.END, w)
            listbox.pack(pady=10)
            
            result = [None]
            
            def on_ok():
                selection = listbox.curselection()
                if selection:
                    result[0] = listbox.get(selection[0])
                window.destroy()
            
            def on_cancel():
                result[0] = None
                window.destroy()
            
            btn_frame = tk.Frame(window)
            btn_frame.pack(pady=10)
            
            tk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=10)
            
            window.wait_window()
            
            return result[0]
            
        except Exception as e:
            print(f"选择测试窗口失败: {str(e)}")
            # 默认返回宝钢系统窗口
            return "BGCMS1-宝钢股份多基地制造管理系统运行环境"
    
    def safe_read_excel(self, file_path, max_retries=3, retry_delay=0.5):
        """安全读取Excel文件，支持重试机制
        
        Args:
            file_path: 文件路径
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
            
        Returns:
            tuple: (success, result)
                success: 是否成功
                result: 成功时返回workbook对象，失败时返回错误信息
        """
        import time
        import xlrd
        
        for retry in range(max_retries):
            try:
                print(f"尝试读取Excel文件 (重试 {retry+1}/{max_retries}): {file_path}")
                workbook = xlrd.open_workbook(file_path)
                print(f"成功读取Excel文件: {file_path}")
                return True, workbook
            except Exception as e:
                error_msg = str(e)
                print(f"读取Excel文件失败: {error_msg}")
                if retry < max_retries - 1:
                    print(f"{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                else:
                    return False, error_msg
        
        return False, "达到最大重试次数"
    
    def load_processed_plans(self):
        """加载已处理的计划号"""
        try:
            # 先清空之前的状态
            self.processed_plans.clear()
            processed_file = os.path.join(self.plan_dir, "processed_plans.txt")
            if os.path.exists(processed_file):
                with open(processed_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        plan_no = line.strip()
                        if plan_no:
                            self.processed_plans.add(plan_no)
                print(f"已加载 {len(self.processed_plans)} 个已处理计划号")
            else:
                print("processed_plans.txt 文件不存在")
        except Exception as e:
            print(f"加载已处理计划号失败: {str(e)}")
    
    def save_processed_plans(self):
        """保存已处理的计划号"""
        try:
            processed_file = os.path.join(self.plan_dir, "processed_plans.txt")
            with open(processed_file, 'w', encoding='utf-8') as f:
                for plan_no in self.processed_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.processed_plans)} 个已处理计划号")
        except Exception as e:
            print(f"保存已处理计划号失败: {str(e)}")
    
    def load_printed_plans(self):
        """加载已打印的计划号"""
        try:
            # 先清空之前的状态
            self.printed_plans.clear()
            printed_file = os.path.join(self.plan_dir, "printed_plans.txt")
            if os.path.exists(printed_file):
                with open(printed_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        plan_no = line.strip()
                        if plan_no:
                            self.printed_plans.add(plan_no)
                print(f"已加载 {len(self.printed_plans)} 个已打印计划号")
            else:
                print("printed_plans.txt 文件不存在")
        except Exception as e:
            print(f"加载已打印计划号失败: {str(e)}")
    
    def save_printed_plans(self):
        """保存已打印的计划号"""
        try:
            printed_file = os.path.join(self.plan_dir, "printed_plans.txt")
            with open(printed_file, 'w', encoding='utf-8') as f:
                for plan_no in self.printed_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.printed_plans)} 个已打印计划号")
        except Exception as e:
            print(f"保存已打印计划号失败: {str(e)}")
    
    def load_no_aps_plans(self):
        """加载无APS的计划号"""
        try:
            # 先清空之前的状态
            self.no_aps_plans.clear()
            no_aps_file = os.path.join(self.plan_dir, "no_aps_plans.txt")
            if os.path.exists(no_aps_file):
                with open(no_aps_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        plan_no = line.strip()
                        if plan_no:
                            self.no_aps_plans.add(plan_no)
                print(f"已加载 {len(self.no_aps_plans)} 个无APS计划号")
            else:
                print("no_aps_plans.txt 文件不存在")
        except Exception as e:
            print(f"加载无APS计划号失败: {str(e)}")
    
    def save_no_aps_plans(self):
        """保存无APS的计划号"""
        try:
            no_aps_file = os.path.join(self.plan_dir, "no_aps_plans.txt")
            with open(no_aps_file, 'w', encoding='utf-8') as f:
                for plan_no in self.no_aps_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.no_aps_plans)} 个无APS计划号")
        except Exception as e:
            print(f"保存无APS计划号失败: {str(e)}")
    
    def load_remove_phosphorus_list(self):
        """加载除鳞钢种列表"""
        # 直接在代码中定义除鳞钢种列表
        remove_phosphorus_list = [
            "1E", "-p", "WSS-M1A367-A", "-1B", "SECC", "SECD", "SECE", "SECF", "SECG",
            "CR5", "DP600", "RS600", "HDT580X", "RCL590F", "SPHD", "SPHE", "SS400-MB",
            "RCL380-DF", "CL", "FB60", "SYE-N", "+ZE", "C1", "RST", "JSH270C", "GH420MC",
            "GMW2M-ST-S-HR1", "D4F1", "D4F2", "D4F3", "D4E2", "D4E2-2", "D3E1", "D4E4",
            "H3B2", "H3C4", "H3D1", "H4D1", "H3D1(SY)", "B1B1-2", "DD12", "DX53D+ZF-B",
            "DX53D+ZF-C", "DX54D+ZF-B", "DX54D+ZF-C", "DX56D+ZF-B", "DX56D+ZF-C", "DX54D+Z-B",
            "DX54D+Z-A", "DX54D+Z-C", "DX56D+Z-B", "DX56D+Z-A", "DX56D+Z-C", "DX53D+Z-B",
            "DX53D+Z-A", "DX53D+Z-C", "JAC270D(YL)", "JAC270E(YL)", "JAC270C", "JAC270D",
            "JAC270E", "JAC270F", "JAC340H", "JAC340H(BI)", "JAC390W", "JAC440W", "JAC590R",
            "JAC590R(BI)", "SP781BQ", "SP782BQ", "SP783BQ", "SP783BJQ", "HC260DPD+ZF",
            "HC340DPD+ZF", "HC450DPD+ZF", "HC590DPD+ZF", "HC260LAD+ZF", "HC340LAD+ZF",
            "HC380LAD+ZF", "HC420LAD+ZF", "HC180YD+ZF", "HC220YD+ZF", "HC260YD+ZF",
            "GX260YD+ZF", "H180Y+ZE", "H220Y+ZE", "H180B+ZE", "H260Y+ZE", "GD52D+ZF",
            "GD53D+ZF", "GD54D+ZF", "GD56D+ZF", "AC340H(BT)", "JAC590R(BT)", "HC260/450DPD+ZF",
            "HC340/590DPD+ZF", "GX340/590DPD+ZF", "GX340LAD+ZF", "GX420LAD+ZF", "SP781AQ",
            "SP782AQ", "SP783AQ", "H2B1-2", "B1A1-2Z", "DX56D+Z-SQ", "DX54D+Z-SQ", "WDEL350",
            "YD+ZF", "E+Z", "DX51D+Z(JD1)", "DX54D+Z", "GX180YD+ZF", "HC180YD+ZF", "HC420LAD",
            "HX180YD+ZF", "JAC340H(BT)", "SP781-390BQ", "SP781-440BQ", "SP781-590BQ",
            "SP782-390BQ", "SP782-440BQ", "SP783-590BQ", "VP781AQ", "VP782AQ", "VP783AQ",
            "WDEL350KMS", "SPHC-P", "SPHD-P", "SPHE-P", "SAPH310-P", "SAPH370-P", "SAPH400-P",
            "SAPH440-P", "QStE340TM-P", "QStE380TM-P", "QStE420TM-P", "QStE460TM-P", "QStE500TM-P",
            "GH420MC-P", "RCL380-P", "RCL450-P", "RCL540-P", "RS600-P", "DP600-P", "SPFH590-P",
            "RST330-P", "W550NBH", "H4D2", "H4C2", "H2C1-1B", "BJDC-EB", "DC51D+ZF", "DC52D+ZF",
            "DC53D+ZF", "JAC780Y", "HC420/780DPD+ZF", "GX420/780DPD+ZF", "A-IF-1", "A-IF-A",
            "B1A2-2", "D4F1(SY)", "H3B4", "DX53D+ZF", "BYSE-N5", "D4F5", "WHF1300R", "P3A2(GA)",
            "M1A2-3B", "M1A1-3B", "B510L", "B530CL-P", "S3A3", "Y3E1"
        ]
        print(f"已加载 {len(remove_phosphorus_list)} 个除鳞钢种")
        return remove_phosphorus_list
    
    def load_aps_grades(self):
        """加载APS钢种列表"""
        aps_grades = []
        file_path = "APS.txt"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            aps_grades.append(line)
                print(f"已加载 {len(aps_grades)} 个APS钢种")
            except Exception as e:
                print(f"加载APS钢种列表失败: {str(e)}")
        else:
            print(f"APS钢种文件不存在: {file_path}")
        return aps_grades
    
    def 匹配除鳞钢种(self, 牌号, removePhosphorusList):
        """检查牌号是否匹配除鳞钢种列表"""
        if not 牌号:
            return False
        
        牌号字符串 = str(牌号).strip()
        
        # 检查是否匹配任何除鳞钢种
        for 钢种 in removePhosphorusList:
            钢种字符串 = 钢种.strip()
            
            # 精确匹配
            if 牌号字符串 == 钢种字符串:
                return True
            
            # 通配符匹配：以"1E"开头
            if 钢种字符串 == "1E" and 牌号字符串.startswith("1E"):
                return True
            
            # 通配符匹配：以"-p"结尾
            if 钢种字符串 == "-p" and 牌号字符串.endswith("-p"):
                return True
            
            # 通配符匹配：以"-P"结尾
            if 钢种字符串 == "-P" and 牌号字符串.endswith("-P"):
                return True
            
            # 通配符匹配：包含"-1B"
            if 钢种字符串 == "-1B" and "-1B" in 牌号字符串:
                return True
            
            # 通配符匹配：包含"-3B"
            if 钢种字符串 == "-3B" and "-3B" in 牌号字符串:
                return True
            
            # 通配符匹配：以"SECC"开头
            if 钢种字符串 == "SECC" and 牌号字符串.startswith("SECC"):
                return True
            
            # 通配符匹配：以"SECD"开头
            if 钢种字符串 == "SECD" and 牌号字符串.startswith("SECD"):
                return True
            
            # 通配符匹配：以"SECE"开头
            if 钢种字符串 == "SECE" and 牌号字符串.startswith("SECE"):
                return True
            
            # 通配符匹配：以"SECF"开头
            if 钢种字符串 == "SECF" and 牌号字符串.startswith("SECF"):
                return True
            
            # 通配符匹配：以"SECG"开头
            if 钢种字符串 == "SECG" and 牌号字符串.startswith("SECG"):
                return True
            
            # 通配符匹配：以"CR5"开头
            if 钢种字符串 == "CR5" and 牌号字符串.startswith("CR5"):
                return True
            
            # 通配符匹配：以"DP600"开头
            if 钢种字符串 == "DP600" and 牌号字符串.startswith("DP600"):
                return True
            
            # 通配符匹配：包含"CL"
            if 钢种字符串 == "CL" and "CL" in 牌号字符串:
                return True
            
            # 通配符匹配：以"+ZE"结尾
            if 钢种字符串 == "+ZE" and 牌号字符串.endswith("+ZE"):
                return True
            
            # 通配符匹配：以"RST"开头
            if 钢种字符串 == "RST" and 牌号字符串.startswith("RST"):
                return True
            
            # 通配符匹配：以"WDEL350"开头
            if 钢种字符串 == "WDEL350" and 牌号字符串.startswith("WDEL350"):
                return True
            
            # 通配符匹配：包含"E+Z"
            if 钢种字符串 == "E+Z" and "E+Z" in 牌号字符串:
                return True
            
            # 通配符匹配：包含"YD+ZF"
            if 钢种字符串 == "YD+ZF" and "YD+ZF" in 牌号字符串:
                return True
        
        return False
    
    def load_coordinate_config(self):
        """加载坐标配置"""
        import os
        config_file = os.path.join(self.plan_dir, "export_coordinates.json")
        if os.path.exists(config_file):
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载坐标配置失败: {str(e)}")
        return {}

# 全局变量
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class ExportConfigGUI:
    """坐标配置界面 - 配置自动导出所需的所有坐标"""

    # 默认坐标值
    DEFAULT_COORDS = {
        # 装炉顺序导出坐标
        "zhuanglu_tab": (261, 87),           # 装炉顺作成管理标签
        "zhuanglu_export_btn": (990, 831),   # 装炉顺序导出按钮
        
        # 轧制计划管理页面坐标
        "zhizhi_tab": (87, 85),              # 轧制计划管理标签
        "plan_select": (861, 134),           # 选择计划号
        "zhizhi_export_btn": (77, 501),      # 导出总计划号列表按钮
        
        # 计划明细导出坐标
        "first_plan": (239, 208),            # 第一个计划号
        "plan_spacing": 21,                  # 计划号间距（垂直）
        "first_plan_offset": 0,              # 第一个计划号纵坐标偏移量
        "plan_detail_export": (79, 870),     # 计划明细导出按钮
        
        # 测试窗口和速度设置
        "test_window": "BGCMS1-宝钢股份多基地制造管理系统运行环境",  # 默认测试窗口
        "export_speed": "中",               # 默认导出速度
        
        # 操作提示设置
        "show_operation_warning": True,       # 是否显示"不要操作鼠标键盘"提示
        # 导出后处理设置
        "auto_process_after_export": False,    # 导出完成后是否自动处理计划
        "auto_print_after_export": False       # 处理完成后是否自动打印计划
    }

    def __init__(self, root, plan_dir, main_app=None):
        self.root = root
        self.plan_dir = plan_dir
        self.main_app = main_app  # MainApp实例，用于实时更新配置
        
        # 导入os模块
        import os
        
        self.config_file = os.path.join(plan_dir, "export_coordinates.json")
        self.coordinates = self.load_coordinates()
        self.status_labels = {}  # 初始化状态标签字典
        
        # 确保目录存在
        if not os.path.exists(plan_dir):
            os.makedirs(plan_dir)
        
        # 配置pyautogui
        if PYAUTOGUI_AVAILABLE:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.3
        
        # 创建界面
        self.create_widgets()
        self.update_all_status()

    def load_coordinates(self):
        """加载坐标配置"""
        import json
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # 合并默认值和保存值
                    coords = self.DEFAULT_COORDS.copy()
                    coords.update(saved)
                    return coords
            except:
                pass
        return self.DEFAULT_COORDS.copy()

    def save_coordinates(self):
        """保存坐标配置"""
        import json
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.coordinates, f, indent=2, ensure_ascii=False)
            self.log("✓ 所有配置已保存")
        except Exception as e:
            self.log(f"✗ 保存配置失败: {e}")

    def create_widgets(self):
        """创建界面组件"""
        import tkinter as tk
        from tkinter import ttk
        
        # 创建画布和滚动条
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.main_frame = ttk.Frame(canvas, padding="10")
        
        self.main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 添加鼠标滚轮事件绑定
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 标题
        title_label = ttk.Label(
            self.main_frame, 
            text="自动导出设置", 
            font=('微软雅黑', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # === 装炉顺序导出坐标 ===
        zhuanglu_frame = ttk.LabelFrame(self.main_frame, text="装炉顺序导出坐标", padding="10")
        zhuanglu_frame.pack(fill=tk.X, pady=10)
        
        self.zhuanglu_tab_var = tk.StringVar()
        self.create_coord_row(zhuanglu_frame, "装炉顺作成管理标签:", "zhuanglu_tab", self.zhuanglu_tab_var)
        
        self.zhuanglu_export_var = tk.StringVar()
        self.create_coord_row(zhuanglu_frame, "装炉顺序导出按钮:", "zhuanglu_export_btn", self.zhuanglu_export_var)
        
        # === 轧制计划管理页面坐标 ===
        zhizhi_frame = ttk.LabelFrame(self.main_frame, text="轧制计划管理页面坐标", padding="10")
        zhizhi_frame.pack(fill=tk.X, pady=10)
        
        self.zhizhi_tab_var = tk.StringVar()
        self.create_coord_row(zhizhi_frame, "轧制计划管理标签:", "zhizhi_tab", self.zhizhi_tab_var)
        
        self.plan_select_var = tk.StringVar()
        self.create_coord_row(zhizhi_frame, "选择计划号:", "plan_select", self.plan_select_var)
        
        self.zhizhi_export_var = tk.StringVar()
        self.create_coord_row(zhizhi_frame, "导出总计划号列表按钮:", "zhizhi_export_btn", self.zhizhi_export_var)
        
        # === 计划明细导出坐标 ===
        detail_frame = ttk.LabelFrame(self.main_frame, text="计划明细导出坐标", padding="10")
        detail_frame.pack(fill=tk.X, pady=10)
        
        self.first_plan_var = tk.StringVar()
        self.create_coord_row(detail_frame, "第一个计划号:", "first_plan", self.first_plan_var)
        
        # 计划号间距（单独处理，因为是单个数值）
        spacing_frame = ttk.Frame(detail_frame)
        spacing_frame.pack(fill=tk.X, pady=5)
        ttk.Label(spacing_frame, text="计划号间距:", width=20).pack(side=tk.LEFT)
        self.plan_spacing_var = tk.StringVar()
        ttk.Entry(spacing_frame, textvariable=self.plan_spacing_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(spacing_frame, text="像素").pack(side=tk.LEFT)
        
        # 第一个计划号纵坐标偏移量（用于校准中点位置）
        offset_frame = ttk.Frame(detail_frame)
        offset_frame.pack(fill=tk.X, pady=5)
        ttk.Label(offset_frame, text="纵坐标偏移量:", width=20).pack(side=tk.LEFT)
        self.first_plan_offset_var = tk.StringVar()
        ttk.Entry(offset_frame, textvariable=self.first_plan_offset_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(offset_frame, text="像素 (正值向下,负值向上)").pack(side=tk.LEFT)
        
        self.plan_detail_export_var = tk.StringVar()
        self.create_coord_row(detail_frame, "计划明细导出按钮:", "plan_detail_export", self.plan_detail_export_var)
        
        # === 窗口选择设置 ===
        test_settings_frame = ttk.LabelFrame(self.main_frame, text="窗口选择设置", padding="10")
        test_settings_frame.pack(fill=tk.X, pady=10)
        
        # 窗口选择
        window_label = ttk.Label(test_settings_frame, text="窗口选择:", font=('微软雅黑', 10, 'bold'))
        window_label.pack(anchor=tk.W, pady=5)
        
        self.test_window_var = tk.StringVar(value=self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境"))
        
        window_options = [
            ("Doc1.docx - Word", "Doc1.docx - Word"),
            ("BGCMS1-宝钢股份多基地制造管理系统运行环境", "BGCMS1-宝钢股份多基地制造管理系统运行环境"),
            ("装炉顺序.jpg", "装炉顺序.jpg"),
            ("当前窗口", "当前窗口")
        ]
        
        for text, value in window_options:
            ttk.Radiobutton(test_settings_frame, text=text, variable=self.test_window_var, value=value, 
                          command=lambda v=value: self.coordinates.update({"test_window": v})).pack(anchor=tk.W, padx=10, pady=2)
        
        # 速度设置
        speed_label = ttk.Label(test_settings_frame, text="自动导出速度:", font=('微软雅黑', 10, 'bold'))
        speed_label.pack(anchor=tk.W, pady=5)
        
        self.export_speed_var = tk.StringVar(value=self.coordinates.get("export_speed", "中"))
        
        speed_options = ["慢", "中", "快"]
        speed_frame = ttk.Frame(test_settings_frame)
        speed_frame.pack(anchor=tk.W, pady=2)
        
        for speed in speed_options:
            ttk.Radiobutton(speed_frame, text=speed, variable=self.export_speed_var, value=speed, 
                          command=lambda v=speed: self.coordinates.update({"export_speed": v})).pack(side=tk.LEFT, padx=15)
        
        # 操作提示设置
        warning_frame = ttk.Frame(test_settings_frame)
        warning_frame.pack(anchor=tk.W, pady=5)
        
        self.show_warning_var = tk.BooleanVar(value=self.coordinates.get("show_operation_warning", True))
        self.warning_checkbox = ttk.Checkbutton(
            warning_frame, 
            text="显示操作提示（自动导出前提示不要操作鼠标键盘）", 
            variable=self.show_warning_var,
            command=self.on_warning_changed
        )
        self.warning_checkbox.pack(anchor=tk.W)
        
        ttk.Label(warning_frame, text="自动导出开始前显示警告提示，防止误操作影响自动化流程", 
                 foreground="gray", font=('微软雅黑', 9)).pack(anchor=tk.W, padx=20)
        
        # 导出后处理设置
        process_frame = ttk.Frame(test_settings_frame)
        process_frame.pack(anchor=tk.W, pady=5)
        
        self.auto_process_var = tk.BooleanVar(value=self.coordinates.get("auto_process_after_export", False))
        self.process_checkbox = ttk.Checkbutton(
            process_frame, 
            text="导出完成后自动处理计划（不显示导出成功确认弹窗）", 
            variable=self.auto_process_var,
            command=self.on_auto_process_changed
        )
        self.process_checkbox.pack(anchor=tk.W)
        
        ttk.Label(process_frame, text="导出完成后自动处理刚刚导出的计划，不显示确认弹窗", 
                 foreground="gray", font=('微软雅黑', 9)).pack(anchor=tk.W, padx=20)
        
        # 自动打印设置
        self.auto_print_var = tk.BooleanVar(value=self.coordinates.get("auto_print_after_export", False))
        self.print_checkbox = ttk.Checkbutton(
            process_frame, 
            text="处理完成后自动打印计划（直接打印，不显示确认弹窗）", 
            variable=self.auto_print_var,
            command=self.on_auto_print_changed
        )
        self.print_checkbox.pack(anchor=tk.W, pady=5)
        
        ttk.Label(process_frame, text="处理完成后自动打印刚刚处理的计划，不显示确认弹窗", 
                 foreground="gray", font=('微软雅黑', 9)).pack(anchor=tk.W, padx=20)
        
        # === 操作按钮 ===
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="💾 保存配置", 
                  command=self.save_all_coordinates).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 恢复默认", 
                  command=self.restore_defaults).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📋 查看当前配置",
                  command=self.show_current_config).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="❌ 关闭窗口", 
                  command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.main_frame, text="操作日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=('Consolas', 10), height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 初始化显示
        self.load_values_to_ui()

    def create_coord_row(self, parent, label_text, coord_key, string_var):
        """创建坐标输入行"""
        import tkinter as tk
        from tkinter import ttk
        
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=5)
        
        ttk.Label(row, text=label_text, width=22).pack(side=tk.LEFT)
        
        # 坐标输入框
        ttk.Entry(row, textvariable=string_var, width=12).pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        status_label = ttk.Label(row, text="未设置", foreground="red")
        status_label.pack(side=tk.LEFT, padx=5)
        self.status_labels[coord_key] = status_label
        
        # 按钮组
        btn_frame = ttk.Frame(row)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="获取", 
                  command=lambda: self.capture_coordinate(coord_key, label_text)).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame, text="测试", 
                  command=lambda: self.test_coordinate(coord_key, label_text)).pack(side=tk.LEFT, padx=2)

    def load_values_to_ui(self):
        """加载值到UI"""
        # 装炉顺序导出坐标
        self.zhuanglu_tab_var.set(self.format_coord(self.coordinates.get("zhuanglu_tab")))
        self.zhuanglu_export_var.set(self.format_coord(self.coordinates.get("zhuanglu_export_btn")))
        
        # 轧制计划管理页面坐标
        self.zhizhi_tab_var.set(self.format_coord(self.coordinates.get("zhizhi_tab")))
        self.plan_select_var.set(self.format_coord(self.coordinates.get("plan_select")))
        self.zhizhi_export_var.set(self.format_coord(self.coordinates.get("zhizhi_export_btn")))
        
        # 计划明细导出坐标
        self.first_plan_var.set(self.format_coord(self.coordinates.get("first_plan")))
        self.plan_spacing_var.set(str(self.coordinates.get("plan_spacing", 21)))
        self.first_plan_offset_var.set(str(self.coordinates.get("first_plan_offset", 0)))
        self.plan_detail_export_var.set(self.format_coord(self.coordinates.get("plan_detail_export")))
        
        # 测试设置
        self.test_window_var.set(self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境"))
        self.export_speed_var.set(self.coordinates.get("export_speed", "中"))
        self.show_warning_var.set(self.coordinates.get("show_operation_warning", True))
        self.auto_process_var.set(self.coordinates.get("auto_process_after_export", False))
        
        # 更新状态显示
        self.update_all_status()

    def on_warning_changed(self):
        """操作提示开关状态改变时的回调"""
        self.coordinates["show_operation_warning"] = self.show_warning_var.get()
        status = "启用" if self.show_warning_var.get() else "禁用"
        self.log(f"操作提示已{status}")
    
    def on_auto_process_changed(self):
        """自动处理开关状态改变时的回调"""
        self.coordinates["auto_process_after_export"] = self.auto_process_var.get()
        status = "启用" if self.auto_process_var.get() else "禁用"
        self.log(f"导出后自动处理已{status}")
    
    def on_auto_print_changed(self):
        """自动打印开关状态改变时的回调"""
        self.coordinates["auto_print_after_export"] = self.auto_print_var.get()
        status = "启用" if self.auto_print_var.get() else "禁用"
        self.log(f"处理后自动打印已{status}")

    def format_coord(self, coord):
        """格式化坐标为元组字符串"""
        if coord is None:
            return ""
        if isinstance(coord, (list, tuple)) and len(coord) == 2:
            return f"{coord[0]}, {coord[1]}"
        return str(coord)

    def parse_coord(self, text):
        """解析坐标字符串为元组"""
        try:
            parts = text.replace("，", ",").split(",")
            if len(parts) == 2:
                return (int(parts[0].strip()), int(parts[1].strip()))
        except:
            pass
        return None

    def capture_coordinate(self, key, name):
        """捕获坐标 - 点点精灵模式：实时显示坐标，点击确认"""
        if not PYAUTOGUI_AVAILABLE:
            import tkinter.messagebox as messagebox
            self.custom_messagebox("错误", "pyautogui未安装")
            return
        
        try:
            from pynput import mouse
            PYNPUT_AVAILABLE = True
        except ImportError:
            PYNPUT_AVAILABLE = False
        
        if not PYNPUT_AVAILABLE:
            # 备用方案：使用原来的倒计时方式
            self._capture_coordinate_fallback(key, name)
            return
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 创建全屏透明覆盖窗口（用于捕获鼠标点击）
        import tkinter as tk
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-alpha', 0.01)  # 几乎完全透明
        overlay.attributes('-topmost', True)  # 始终置顶
        overlay.overrideredirect(True)  # 无边框
        overlay.geometry(f"{screen_width}x{screen_height}+0+0")  # 全屏
        
        # 创建悬浮坐标显示窗口（显示在右上角）
        float_window = tk.Toplevel(self.root)
        float_window.title("坐标捕获")
        float_window.attributes('-topmost', True)  # 始终置顶
        float_window.overrideredirect(True)  # 无边框
        float_window.geometry(f"+{screen_width - 220}+50")
        
        # 创建内容
        from tkinter import ttk
        frame = ttk.Frame(float_window, padding="10")
        frame.pack()
        
        ttk.Label(frame, text=f"正在获取: {name}", font=('微软雅黑', 10, 'bold')).pack()
        
        coord_label = ttk.Label(frame, text="X: 0  Y: 0", font=('Consolas', 14), foreground='blue')
        coord_label.pack(pady=5)
        
        ttk.Label(frame, text="移动鼠标查看坐标", font=('微软雅黑', 9)).pack()
        ttk.Label(frame, text="点击鼠标左键确认", font=('微软雅黑', 9), foreground='green').pack()
        ttk.Label(frame, text="按 ESC 键取消", font=('微软雅黑', 9), foreground='red').pack()
        
        # 最小化主窗口
        self.root.iconify()
        
        # 存储捕获结果
        captured = [False]
        final_coord = [None]
        cleaned = [False]  # 清理标志，避免重复调用cleanup
        
        def update_coord():
            """实时更新坐标显示"""
            if captured[0]:
                return
            try:
                import pyautogui
                pos = pyautogui.position()
                coord_label.config(text=f"X: {pos.x}  Y: {pos.y}")
                float_window.after(50, update_coord)  # 每50ms更新一次
            except:
                pass
        
        def on_click(x, y, button, pressed):
            """鼠标点击事件"""
            if pressed and button == mouse.Button.left:
                if not captured[0]:  # 避免重复调用
                    final_coord[0] = (int(x), int(y))
                    captured[0] = True
                    # 先更新UI，再清理
                    coord = final_coord[0]
                    self.coordinates[key] = coord
                    coord_str = self.format_coord(coord)
                    
                    # 更新UI
                    if key == "zhuanglu_tab":
                        self.zhuanglu_tab_var.set(coord_str)
                    elif key == "zhuanglu_export_btn":
                        self.zhuanglu_export_var.set(coord_str)
                    elif key == "zhizhi_tab":
                        self.zhizhi_tab_var.set(coord_str)
                    elif key == "plan_select":
                        self.plan_select_var.set(coord_str)
                    elif key == "zhizhi_export_btn":
                        self.zhizhi_export_var.set(coord_str)
                    elif key == "first_plan":
                        self.first_plan_var.set(coord_str)
                    elif key == "plan_detail_export":
                        self.plan_detail_export_var.set(coord_str)
                    
                    self.log(f"✓ 已捕获 {name}: {coord_str}")
                    self.update_status(key, coord)
                    
                    # 使用after延迟调用cleanup
                    float_window.after(10, cleanup)
                return False  # 停止监听
        
        def on_esc(event):
            """ESC键取消"""
            print("ESC键被按下，取消捕获")
            if not captured[0]:  # 避免重复调用
                captured[0] = True
                final_coord[0] = None
                self.log(f"✗ 已取消捕获 {name}")
                # 使用after延迟调用cleanup
                float_window.after(10, cleanup)
            return 'break'  # 阻止事件继续传播
        
        def cleanup():
            """清理资源"""
            if cleaned[0]:  # 避免重复清理
                return
            cleaned[0] = True
            print("执行cleanup...")
            try:
                listener.stop()
            except Exception as e:
                print(f"停止监听器失败: {e}")
            try:
                overlay.destroy()  # 销毁透明覆盖窗口
            except Exception as e:
                print(f"销毁透明覆盖窗口失败: {e}")
            try:
                float_window.destroy()
            except Exception as e:
                print(f"销毁浮动窗口失败: {e}")
            try:
                self.root.deiconify()
                self.root.lift()
                print("主窗口已恢复")
            except Exception as e:
                print(f"恢复主窗口失败: {e}")
        
        def check_captured():
            """检查是否已捕获"""
            if cleaned[0]:  # 如果已经清理过，不再执行
                return
            if captured[0]:
                # 已经被捕获，调用cleanup
                cleanup()
            else:
                # 继续检查
                float_window.after(100, check_captured)
        
        # 启动鼠标监听（必须在cleanup之前定义）
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        
        # 绑定ESC键（在两个窗口上都绑定）
        float_window.bind('<Escape>', on_esc)
        overlay.bind('<Escape>', on_esc)
        
        # 在透明覆盖窗口上绑定鼠标点击事件
        def on_overlay_click(event):
            """透明覆盖窗口上的鼠标点击"""
            if not captured[0]:
                final_coord[0] = (event.x, event.y)
                captured[0] = True
                # 先更新UI，再清理
                coord = final_coord[0]
                self.coordinates[key] = coord
                coord_str = self.format_coord(coord)
                
                # 更新UI
                if key == "zhuanglu_tab":
                    self.zhuanglu_tab_var.set(coord_str)
                elif key == "zhuanglu_export_btn":
                    self.zhuanglu_export_var.set(coord_str)
                elif key == "zhizhi_tab":
                    self.zhizhi_tab_var.set(coord_str)
                elif key == "plan_select":
                    self.plan_select_var.set(coord_str)
                elif key == "zhizhi_export_btn":
                    self.zhizhi_export_var.set(coord_str)
                elif key == "first_plan":
                    self.first_plan_var.set(coord_str)
                elif key == "plan_detail_export":
                    self.plan_detail_export_var.set(coord_str)
                
                self.log(f"✓ 已捕获 {name}: {coord_str}")
                self.update_status(key, coord)
                
                # 使用after延迟调用cleanup
                float_window.after(10, cleanup)
        
        overlay.bind('<Button-1>', on_overlay_click)
        
        # 强制获取焦点（多种方式尝试）
        overlay.focus_force()
        overlay.lift()
        float_window.focus_force()
        float_window.lift()
        
        # 开始更新坐标
        float_window.after(50, update_coord)
        float_window.after(100, check_captured)

    def _capture_coordinate_fallback(self, key, name):
        """备用捕获方法（无pynput时使用）"""
        import time
        # 最小化窗口
        self.root.iconify()
        time.sleep(0.5)
        
        # 倒计时
        for i in range(5, 0, -1):
            self.log(f"请在{i}秒内将鼠标移动到: {name}")
            time.sleep(1)
        
        # 获取位置
        import pyautogui
        pos = pyautogui.position()
        coord = (pos.x, pos.y)
        self.coordinates[key] = coord
        
        # 更新UI
        coord_str = self.format_coord(coord)
        if key == "zhuanglu_tab":
            self.zhuanglu_tab_var.set(coord_str)
        elif key == "zhuanglu_export_btn":
            self.zhuanglu_export_var.set(coord_str)
        elif key == "zhizhi_tab":
            self.zhizhi_tab_var.set(coord_str)
        elif key == "plan_select":
            self.plan_select_var.set(coord_str)
        elif key == "zhizhi_export_btn":
            self.zhizhi_export_var.set(coord_str)
        elif key == "first_plan":
            self.first_plan_var.set(coord_str)
        elif key == "plan_detail_export":
            self.plan_detail_export_var.set(coord_str)
        
        self.log(f"✓ 已捕获 {name}: {coord_str}")
        
        # 恢复窗口
        self.root.deiconify()
        self.root.lift()
        
        self.update_status(key, coord)

    def get_single_value(self, key, name):
        """获取单个数值（如间距）"""
        if not PYAUTOGUI_AVAILABLE:
            import tkinter.messagebox as messagebox
            self.custom_messagebox("错误", "pyautogui未安装")
            return
        
        # 最小化窗口
        import time
        self.root.iconify()
        time.sleep(0.5)
        
        # 倒计时
        for i in range(3, 0, -1):
            self.log(f"请在{i}秒内记录当前值")
            time.sleep(1)
        
        # 这里只是提示用户，实际值需要手动输入
        self.log(f"请手动输入{name}")
        
        # 恢复窗口
        self.root.deiconify()
        self.root.lift()

    def test_coordinate(self, key, name):
        """测试坐标点击"""
        import time
        coord = self.coordinates.get(key)
        if not coord:
            import tkinter.messagebox as messagebox
            self.custom_messagebox("警告", f"{name} 未设置坐标，请先获取坐标")
            return
        
        if not PYAUTOGUI_AVAILABLE:
            import tkinter.messagebox as messagebox
            self.custom_messagebox("错误", "pyautogui未安装")
            return
        
        # 选择测试窗口
        test_window_result = self.select_test_window()
        if not test_window_result or not test_window_result[0]:
            return
        
        # select_test_window返回元组 (window_name, speed)
        test_window = test_window_result[0]
        
        # 确认测试
        import tkinter.messagebox as messagebox
        if not self.custom_messagebox("确认测试", f"即将测试点击 {name}\n坐标: {coord}\n测试窗口: {test_window}\n\n是否继续？"):
            return
        
        try:
            # 激活测试窗口
            self.activate_window(test_window)
            time.sleep(0.5)
            
            # 移动鼠标到目标位置
            import pyautogui
            pyautogui.moveTo(coord[0], coord[1], duration=0.5)
            time.sleep(0.3)
            
            # 点击
            pyautogui.click()
            
            self.log(f"✓ 已测试点击 {name}: {coord}")
            self.custom_messagebox("测试完成", f"已点击 {name}\n坐标: {coord}\n测试窗口: {test_window}")
        except Exception as e:
            self.log(f"✗ 测试 {name} 失败: {str(e)}")
            self.custom_messagebox("测试失败", f"测试 {name} 时出错:\n{str(e)}")

    def update_status(self, key, coord):
        """更新状态显示"""
        if key in self.status_labels:
            if coord:
                self.status_labels[key].config(text="已设置", foreground="green")
            else:
                self.status_labels[key].config(text="未设置", foreground="red")

    def update_all_status(self):
        """更新所有状态"""
        for key, coord in self.coordinates.items():
            self.update_status(key, coord)

    def save_all_coordinates(self):
        """保存所有坐标"""
        # 从UI读取值
        self.coordinates["zhuanglu_tab"] = self.parse_coord(self.zhuanglu_tab_var.get()) or self.DEFAULT_COORDS["zhuanglu_tab"]
        self.coordinates["zhuanglu_export_btn"] = self.parse_coord(self.zhuanglu_export_var.get()) or self.DEFAULT_COORDS["zhuanglu_export_btn"]
        self.coordinates["zhizhi_tab"] = self.parse_coord(self.zhizhi_tab_var.get()) or self.DEFAULT_COORDS["zhizhi_tab"]
        self.coordinates["plan_select"] = self.parse_coord(self.plan_select_var.get()) or self.DEFAULT_COORDS["plan_select"]
        self.coordinates["zhizhi_export_btn"] = self.parse_coord(self.zhizhi_export_var.get()) or self.DEFAULT_COORDS["zhizhi_export_btn"]
        self.coordinates["first_plan"] = self.parse_coord(self.first_plan_var.get()) or self.DEFAULT_COORDS["first_plan"]
        self.coordinates["plan_detail_export"] = self.parse_coord(self.plan_detail_export_var.get()) or self.DEFAULT_COORDS["plan_detail_export"]
        
        try:
            self.coordinates["plan_spacing"] = int(self.plan_spacing_var.get())
        except:
            self.coordinates["plan_spacing"] = self.DEFAULT_COORDS["plan_spacing"]
        
        try:
            self.coordinates["first_plan_offset"] = int(self.first_plan_offset_var.get())
        except:
            self.coordinates["first_plan_offset"] = 0
        
        # 保存操作提示设置
        self.coordinates["show_operation_warning"] = self.show_warning_var.get()
        # 保存自动处理设置
        self.coordinates["auto_process_after_export"] = self.auto_process_var.get()
        
        self.save_coordinates()
        self.update_all_status()
        
        # 立即更新到MainApp的coordinates中
        if self.main_app:
            self.main_app.coordinates.update(self.coordinates)
            print(f"配置已实时更新到主程序: {self.coordinates}")
        
        import tkinter.messagebox as messagebox
        messagebox.showinfo("成功", "所有配置已保存！")
        
        # 关闭设置窗口
        self.root.destroy()

    def restore_defaults(self):
        """恢复默认坐标"""
        import tkinter.messagebox as messagebox
        if self.custom_messagebox("确认", "确定要恢复默认坐标吗？"):
            self.coordinates = self.DEFAULT_COORDS.copy()
            self.load_values_to_ui()
            self.update_all_status()
            self.log("✓ 已恢复默认坐标")

    def show_current_config(self):
        """显示当前配置"""
        config_text = "当前坐标配置:\n\n"
        config_text += "【装炉顺序导出】\n"
        config_text += f"  装炉顺作成管理标签: {self.format_coord(self.coordinates.get('zhuanglu_tab'))}\n"
        config_text += f"  装炉顺序导出按钮: {self.format_coord(self.coordinates.get('zhuanglu_export_btn'))}\n\n"
        config_text += "【轧制计划管理页面】\n"
        config_text += f"  轧制计划管理标签: {self.format_coord(self.coordinates.get('zhizhi_tab'))}\n"
        config_text += f"  选择计划号: {self.format_coord(self.coordinates.get('plan_select'))}\n"
        config_text += f"  导出总计划号列表按钮: {self.format_coord(self.coordinates.get('zhizhi_export_btn'))}\n\n"
        config_text += "【计划明细导出】\n"
        config_text += f"  第一个计划号: {self.format_coord(self.coordinates.get('first_plan'))}\n"
        config_text += f"  计划号间距: {self.coordinates.get('plan_spacing', 21)} 像素\n"
        config_text += f"  计划明细导出按钮: {self.format_coord(self.coordinates.get('plan_detail_export'))}\n"
        
        import tkinter.messagebox as messagebox
        self.custom_messagebox("当前配置", config_text)

    def select_test_window(self):
        """选择测试窗口和速度设置"""
        print("=== 显示窗口选择对话框 ===")
        import tkinter as tk
        from tkinter import ttk
        
        # 创建选择窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("选择测试窗口")
        dialog.geometry("500x600")  # 增大窗口尺寸
        dialog.resizable(True, True)
        dialog.attributes('-topmost', True)  # 始终置顶
        
        # 计算屏幕中心位置
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog_width = 500
        dialog_height = 600
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 窗口标题
        title_label = ttk.Label(dialog, text="请选择用于测试的窗口", font=('微软雅黑', 14, 'bold'))
        title_label.pack(pady=20)
        
        # 窗口选项
        window_var = tk.StringVar(value="Doc1.docx - Word")
        
        options = [
            ("Doc1.docx - Word - 用于测试所有操作", "Doc1.docx - Word"),
            ("BGCMS1-宝钢股份多基地制造管理系统运行环境", "BGCMS系统"),
            ("装炉顺序.jpg - 装炉顺序图片窗口", "装炉顺序.jpg"),
            ("当前窗口 - 不切换窗口", "当前窗口")
        ]
        
        # 创建选项框架
        options_frame = ttk.Frame(dialog)
        options_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        for text, value in options:
            ttk.Radiobutton(options_frame, text=text, variable=window_var, value=value).pack(anchor=tk.W, padx=10, pady=8)
        
        # 速度设置
        speed_label = ttk.Label(dialog, text="自动导出速度设置", font=('微软雅黑', 12, 'bold'))
        speed_label.pack(pady=10)
        
        speed_var = tk.StringVar(value="中")
        speed_frame = ttk.Frame(dialog)
        speed_frame.pack(padx=20, pady=5)
        
        speeds = ["慢", "中", "快"]
        for speed in speeds:
            ttk.Radiobutton(speed_frame, text=speed, variable=speed_var, value=speed).pack(side=tk.LEFT, padx=20)
        
        # 确认按钮
        def on_confirm():
            selected = window_var.get()
            speed = speed_var.get()
            print(f"用户选择了: {selected}, 速度: {speed}")
            dialog.result = (selected, speed)
            dialog.destroy()
        
        def on_cancel():
            print("用户取消选择")
            dialog.result = (None, None)
            dialog.destroy()
        
        # 按钮框架
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        # 增大按钮尺寸
        confirm_btn = ttk.Button(btn_frame, text="确定", command=on_confirm, width=15)
        confirm_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="取消", command=on_cancel, width=15)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 模态对话框
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.result = (None, None)
        
        print("等待用户选择测试窗口和速度设置...")
        self.root.wait_window(dialog)
        
        print(f"窗口选择完成，结果: {dialog.result}")
        return dialog.result

    def activate_window(self, window_name):
        """激活指定窗口"""
        import time
        print(f"=== 激活窗口: {window_name} ===")
        
        if window_name == "当前窗口":
            print("使用当前窗口")
            return True
        
        try:
            import win32gui
            import win32con
            print("win32gui导入成功")
        except ImportError:
            print("win32gui未安装")
            import tkinter.messagebox as messagebox
            self.custom_messagebox("错误", "win32gui未安装，无法激活窗口")
            return False
        
        # 使用原始窗口标题
        window_title = window_name
        print(f"查找窗口: {window_title}")
        
        # 查找窗口
        def callback(hwnd, handles):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_title in window_text:
                    print(f"找到窗口: {window_text}")
                    handles.append(hwnd)
        
        handles = []
        win32gui.EnumWindows(callback, handles)
        
        if handles:
            hwnd = handles[0]
            print(f"激活窗口句柄: {hwnd}")
            
            # 恢复窗口（如果最小化）
            if win32gui.IsIconic(hwnd):
                print("窗口被最小化，正在恢复...")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                import time
                time.sleep(0.5)
            
            # 激活窗口
            try:
                print("设置窗口为前台...")
                win32gui.SetForegroundWindow(hwnd)
                win32gui.SetActiveWindow(hwnd)
                win32gui.SetFocus(hwnd)
                import time
                time.sleep(1)
                print("窗口激活成功")
                return True
            except Exception as e:
                print(f"激活窗口失败: {str(e)}")
                # 备用方案：不使用鼠标点击，只返回成功
                if PYAUTOGUI_AVAILABLE:
                    print("使用pyautogui备用方案...")
                    # 不执行鼠标点击，避免干扰导出步骤
                    import time
                    time.sleep(0.5)
                    print("pyautogui备用方案执行成功")
                    return True
                return False
        else:
            print(f"未找到窗口: {window_title}")
            import tkinter.messagebox as messagebox
            self.custom_messagebox("警告", f"未找到窗口: {window_title}")
            return False

    def log(self, message):
        """添加日志"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()


def main():
    root = tk.Tk()
    app = FurnaceOrderManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
