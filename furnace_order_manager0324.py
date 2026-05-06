import tkinter as tk
from tkinter import ttk, messagebox
from collections import OrderedDict
import os
import sys
import warnings
import pandas as pd
import xlrd

# 导入PyQt5模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QScrollArea, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QBrush

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
        self.is_selecting_all = False
        
        # 自动导出相关配置
        # 获取exe文件所在目录或脚本所在目录
        if getattr(sys, 'frozen', False):
            # 打包成exe后的路径
            self.plan_dir = os.path.dirname(sys.executable)
        else:
            # 脚本运行时的路径
            self.plan_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 自动创建计划号文件夹
        self.create_required_folders()
        
        self.coordinates = self.load_coordinate_config()  # 加载坐标配置
        self.processed_plans = set()  # 已处理的计划号集合
        self.printed_plans = set()  # 已打印的计划号集合
        self.no_aps_plans = set()  # 包含无APS钢种的计划号集合
        self.newly_exported_plans = set()  # 新导出的计划号集合
        
        # 防退出登录相关变量
        self.anti_logout_timer = None
        self.is_anti_logout_running = False
        
        # 尝试导入必要的模块
        try:
            import win32gui
            import win32api
            import win32con
            import pyautogui
            self.PYAUTOGUI_AVAILABLE = True
        except ImportError:
            self.PYAUTOGUI_AVAILABLE = False
        
        # 总计划号列表缓存
        self.zhizhi_plan_list = []  # 存储序号和计划号信息：[(序号, 计划号), ...]
        self.zhizhi_plan_coord_map = {}  # 存储计划号到坐标的映射
        
        # 调试窗口（在auto_export中创建）
        self.debug_window = None
        self.debug_text = None
        
        # 数据库相关
        self.db_path = os.path.join(self.plan_dir, "furnace_order.db")
        self.init_database()
        
        self.create_ui()
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_data()
    
    def create_required_folders(self):
        """自动创建所需的文件夹和文件"""
        # 创建计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        if not os.path.exists(plan_dir):
            os.makedirs(plan_dir)
            print(f"✓ 创建计划号文件夹: {plan_dir}")
        
        # 创建备份文件夹
        backup_dir = os.path.join(plan_dir, "backup")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            print(f"✓ 创建备份文件夹: {backup_dir}")
        
        # 创建必要的模板文件
        required_files = {
            "export_coordinates.json": "{}",
            "processed_plans.txt": "",
            "printed_plans.txt": "",
            "no_aps_plans.txt": ""
        }
        
        for filename, default_content in required_files.items():
            file_path = os.path.join(self.plan_dir, filename)
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    print(f"✓ 创建文件: {filename}")
                except Exception as e:
                    print(f"✗ 创建文件失败 {filename}: {e}")
        
        # 特殊处理APS.txt文件 - 如果不存在，从项目目录读取
        aps_file_path = os.path.join(self.plan_dir, "APS.txt")
        if not os.path.exists(aps_file_path):
            try:
                # 从项目目录读取现有的APS.txt文件
                project_aps_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "APS.txt")
                
                if os.path.exists(project_aps_file):
                    # 读取项目中的APS.txt文件内容
                    with open(project_aps_file, 'r', encoding='utf-8') as f:
                        aps_content = f.read()
                    # 创建新的APS.txt文件
                    with open(aps_file_path, 'w', encoding='utf-8') as f:
                        f.write(aps_content)
                    print(f"✓ 从项目目录复制APS.txt文件")
                else:
                    print(f"✗ 项目目录中不存在APS.txt文件")
            except Exception as e:
                print(f"✗ 创建APS.txt文件失败: {e}")
        
        # 不创建装炉顺序和总计划号列表文件，由用户自行管理
    
    def init_database(self):
        """初始化SQLite数据库"""
        import sqlite3
        import os
        
        try:
            # 确保数据库文件所在目录存在
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建装炉顺序表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_order (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_no TEXT NOT NULL,
                    coil_no TEXT,
                    steel_grade TEXT,
                    specification TEXT,
                    weight REAL,
                    order_no INTEGER,
                    rough_rolling_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建总计划号列表表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS total_plan_list (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_no TEXT NOT NULL,
                    seq_no INTEGER,
                    steel_grade TEXT,
                    specification TEXT,
                    quantity INTEGER,
                    x_coord INTEGER,
                    y_coord INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建计划号文件状态表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_file_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_no TEXT NOT NULL UNIQUE,
                    has_file INTEGER DEFAULT 0,
                    status TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 提交并关闭
            conn.commit()
            conn.close()
            print(f"✓ 数据库初始化成功: {self.db_path}")
        except Exception as e:
            print(f"✗ 数据库初始化失败: {str(e)}")
    
    def import_zhuanglu_shunxu_to_db(self, file_path):
        """从装炉顺序.xls导入数据到数据库"""
        import time
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                import xlrd
                import sqlite3
                import os
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"文件不存在: {file_path}")
                    return False
                
                # 检查文件是否可以读取
                if not os.access(file_path, os.R_OK):
                    print(f"文件无法读取: {file_path}")
                    return False
                
                # 等待文件操作完成
                time.sleep(0.5)
                
                # 读取Excel文件
                print(f"尝试读取Excel文件: {file_path}")
                workbook = xlrd.open_workbook(file_path)
                sheet = workbook.sheet_by_index(0)
                
                # 查找列索引
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                plan_col = -1
                coil_col = -1
                steel_col = -1
                spec_col = -1
                weight_col = -1
                order_col = -1
                rough_col = -1
                
                for idx, header in enumerate(headers):
                    if '计划号' in str(header):
                        plan_col = idx
                    elif '钢卷号' in str(header):
                        coil_col = idx
                    elif '钢种' in str(header) or '钢级' in str(header):
                        steel_col = idx
                    elif '规格' in str(header):
                        spec_col = idx
                    elif '重量' in str(header):
                        weight_col = idx
                    elif '装炉顺序' in str(header):
                        order_col = idx
                    elif '粗轧报信' in str(header):
                        rough_col = idx
                
                if plan_col == -1:
                    print("未找到计划号列")
                    return False
                
                # 连接数据库
                print(f"尝试连接数据库: {self.db_path}")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 清空现有数据
                cursor.execute("DELETE FROM plan_order")
                
                # 导入数据
                count = 0
                for row in range(1, sheet.nrows):
                    try:
                        plan_no = str(sheet.cell_value(row, plan_col)).strip()
                        if not plan_no or plan_no == 'nan':
                            continue
                        
                        coil_no = str(sheet.cell_value(row, coil_col)).strip() if coil_col != -1 else ''
                        steel_grade = str(sheet.cell_value(row, steel_col)).strip() if steel_col != -1 else ''
                        specification = str(sheet.cell_value(row, spec_col)).strip() if spec_col != -1 else ''
                        weight = float(sheet.cell_value(row, weight_col)) if weight_col != -1 else 0.0
                        order_no = int(sheet.cell_value(row, order_col)) if order_col != -1 else row
                        rough_info = str(sheet.cell_value(row, rough_col)).strip() if rough_col != -1 else ''
                        
                        cursor.execute('''
                            INSERT INTO plan_order (plan_no, coil_no, steel_grade, specification, weight, order_no, rough_rolling_info)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (plan_no, coil_no, steel_grade, specification, weight, order_no, rough_info))
                        count += 1
                    except Exception as e:
                        print(f"导入行 {row} 失败: {str(e)}")
                        continue
                
                # 提交并关闭
                conn.commit()
                conn.close()
                print(f"✓ 成功导入 {count} 条装炉顺序数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入装炉顺序数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"✗ 导入装炉顺序数据失败: {str(e)}")
                    return False
    
    def import_zhizhi_plan_list_to_db(self, file_path):
        """从总计划号列表.xls导入数据到数据库"""
        import time
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                import xlrd
                import sqlite3
                import os
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    print(f"文件不存在: {file_path}")
                    return False
                
                # 检查文件是否可以读取
                if not os.access(file_path, os.R_OK):
                    print(f"文件无法读取: {file_path}")
                    return False
                
                # 等待文件操作完成
                time.sleep(0.5)
                
                # 读取Excel文件
                print(f"尝试读取Excel文件: {file_path}")
                workbook = xlrd.open_workbook(file_path)
                sheet = workbook.sheet_by_index(0)
                
                # 查找列索引
                headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
                seq_col = -1
                plan_col = -1
                steel_col = -1
                spec_col = -1
                quantity_col = -1
                
                for idx, header in enumerate(headers):
                    if '序号' in str(header):
                        seq_col = idx
                    elif '计划号' in str(header):
                        plan_col = idx
                    elif '钢种' in str(header) or '钢级' in str(header):
                        steel_col = idx
                    elif '规格' in str(header):
                        spec_col = idx
                    elif '数量' in str(header):
                        quantity_col = idx
                
                if plan_col == -1:
                    print("未找到计划号列")
                    return False
                
                # 连接数据库
                print(f"尝试连接数据库: {self.db_path}")
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 清空现有数据
                cursor.execute("DELETE FROM total_plan_list")
                
                # 导入数据
                count = 0
                for row in range(1, sheet.nrows):
                    try:
                        plan_no = str(sheet.cell_value(row, plan_col)).strip()
                        if not plan_no or plan_no == 'nan':
                            continue
                        
                        seq_no = int(sheet.cell_value(row, seq_col)) if seq_col != -1 else row
                        steel_grade = str(sheet.cell_value(row, steel_col)).strip() if steel_col != -1 else ''
                        specification = str(sheet.cell_value(row, spec_col)).strip() if spec_col != -1 else ''
                        quantity = int(sheet.cell_value(row, quantity_col)) if quantity_col != -1 else 1
                        
                        cursor.execute('''
                            INSERT INTO total_plan_list (plan_no, seq_no, steel_grade, specification, quantity)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (plan_no, seq_no, steel_grade, specification, quantity))
                        count += 1
                    except Exception as e:
                        print(f"导入行 {row} 失败: {str(e)}")
                        continue
                
                # 提交并关闭
                conn.commit()
                conn.close()
                print(f"✓ 成功导入 {count} 条总计划号列表数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入总计划号列表数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"✗ 导入总计划号列表数据失败: {str(e)}")
                    return False
    
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
        
        # 创建Treeview和滚动条
        list_frame = tk.Frame(main_frame, bg='#f0f0f0')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 垂直滚动条
        yscrollbar = tk.Scrollbar(list_frame)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 水平滚动条
        xscrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 导入ttk模块
        from tkinter import ttk
        
        # 创建Treeview组件，设置为扩展选择模式以支持多选
        self.listbox = ttk.Treeview(
            list_frame,
            columns=('plan_no', 'count', 'status', 'coil_range'),
            show='headings',
            yscrollcommand=yscrollbar.set,
            xscrollcommand=xscrollbar.set,
            height=6,  # 减少显示的行数，增加每行的高度感
            selectmode='extended'  # 启用扩展选择模式，支持鼠标点击多选
        )
        
        # 设置列标题和宽度
        self.listbox.heading('plan_no', text='计划号')
        self.listbox.heading('count', text='块数')
        self.listbox.heading('status', text='状态')
        self.listbox.heading('coil_range', text='起止钢卷号')
        
        self.listbox.column('plan_no', width=26, anchor='center')    # 计划号列宽26，水平居中
        self.listbox.column('count', width=10, anchor='w')           # 块数列宽10
        self.listbox.column('status', width=380, anchor='w')         # 状态列宽380
        self.listbox.column('coil_range', width=180, anchor='w')      # 钢卷号列宽180
        
        # 设置字体和行高
        style = ttk.Style()
        # 设置行高和字体
        style.configure('Treeview', font=('宋体', 28, 'bold'), rowheight=50)  # 设置行高为50
        style.configure('Treeview.Heading', font=('宋体', 28, 'bold'), padding=(5, 10))  # 标题增加内边距
        # 创建绿色字体标签
        style.configure('Green.Treeview', font=('宋体', 28, 'bold'), foreground='green')
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscrollbar.config(command=self.listbox.yview)
        xscrollbar.config(command=self.listbox.xview)
        
        # 绑定选择事件
        self.listbox.bind('<<TreeviewSelect>>', self.on_select)
        # 绑定右键菜单
        self.listbox.bind('<Button-3>', self.show_context_menu)
        # 绑定鼠标左键点击事件，实现直接点击多选
        self.listbox.bind('<Button-1>', self.on_item_click)
        
        # 统计信息和防退出登录选项
        stats_frame = tk.Frame(main_frame, bg='#f0f0f0')
        stats_frame.pack(fill=tk.X, pady=10)
        
        # 统计信息标签
        self.stats_label = tk.Label(
            stats_frame,
            text="总块数: 0",
            font=("宋体", 20),
            bg='#f0f0f0',
            fg='blue',
            anchor='w'
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # 防退出登录选项
        self.anti_logout_var = tk.BooleanVar()
        self.anti_logout_checkbox = tk.Checkbutton(
            stats_frame,
            text="防止退出登录",
            variable=self.anti_logout_var,
            font=("宋体", 20),
            bg='#f0f0f0',
            command=self.on_anti_logout_toggle
        )
        self.anti_logout_checkbox.pack(side=tk.RIGHT)
        
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
            user_choice = [False]  # 使用列表存储，以便在内部函数中修改
            
            def on_yes():
                user_choice[0] = True
                msg_window.destroy()
            
            def on_no():
                user_choice[0] = False
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
            except Exception as e:
                print(f"提升主窗口失败: {e}")
            
            # 确保弹窗在最前面
            msg_window.transient(self.root)
            msg_window.grab_set()
            msg_window.lift()
            msg_window.focus_force()
            # 设置"是"按钮为默认焦点
            yes_btn.focus_set()
            # 绑定回车键到"是"按钮
            msg_window.bind('<Return>', lambda event: on_yes())
            msg_window.wait_window()
            
            return user_choice[0]
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
            # 设置"确定"按钮为默认焦点
            ok_btn.focus_set()
            # 绑定回车键到"确定"按钮
            msg_window.bind('<Return>', lambda event: msg_window.destroy())
            msg_window.wait_window()
    
    def load_data(self):
        """加载Excel数据 - 调用刷新计划号列表方法"""
        import os
        # 重新加载已处理和已打印的状态
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_no_aps_plans()
        
        # 获取最新的装炉顺序和总计划号列表文件
        def get_latest_file(plan_dir, base_name, extension):
            import re
            latest_file = None
            max_num = -1
            for file in os.listdir(plan_dir):
                if file.startswith(base_name) and file.endswith(extension):
                    # 处理带序号的文件名
                    if file == f"{base_name}{extension}":
                        # 没有序号的文件，视为0号
                        num = 0
                    else:
                        match = re.search(rf'{base_name}(\d+){extension}', file)
                        if match:
                            num = int(match.group(1))
                        else:
                            continue
                    if num > max_num:
                        max_num = num
                        latest_file = file
            return latest_file
        
        # 检查是否存在装炉顺序文件，如果存在则自动导入到数据库
        plan_dir = os.path.join(self.plan_dir, "计划号")
        # 查找所有以"装炉顺序"开头的文件
        zhuanglu_files = []
        for file in os.listdir(plan_dir):
            if file.startswith("装炉顺序") and file.endswith(".xls"):
                zhuanglu_files.append(file)
        
        # 找到最新的装炉顺序文件
        latest_zhuanglu = None
        if zhuanglu_files:
            # 按文件名排序，优先选择带序号的文件，然后是不带序号的
            zhuanglu_files.sort(reverse=True)
            latest_zhuanglu = zhuanglu_files[0]
        
        if latest_zhuanglu:
            zhuanglu_file = os.path.join(plan_dir, latest_zhuanglu)
            try:
                print(f"发现装炉顺序文件: {latest_zhuanglu}，正在导入到数据库...")
                import_success = self.import_zhuanglu_shunxu_to_db(zhuanglu_file)
                if import_success:
                    print(f"✓ 装炉顺序数据导入数据库成功")
                else:
                    print(f"✗ 装炉顺序数据导入数据库失败")
            except Exception as e:
                print(f"导入装炉顺序数据时出错: {str(e)}")
        
        # 检查是否存在总计划号列表文件，如果存在则自动导入到数据库
        latest_total_plan = get_latest_file(plan_dir, "总计划号列表", ".xls")
        if latest_total_plan:
            total_plan_file = os.path.join(plan_dir, latest_total_plan)
            try:
                print(f"发现总计划号列表文件: {latest_total_plan}，正在导入到数据库...")
                import_success = self.import_zhizhi_plan_list_to_db(total_plan_file)
                if import_success:
                    print(f"✓ 总计划号列表数据导入数据库成功")
                else:
                    print(f"✗ 总计划号列表数据导入数据库失败")
            except Exception as e:
                print(f"导入总计划号列表数据时出错: {str(e)}")
        
        # 刷新计划号列表
        self.refresh_plan_list()
    
    def refresh_plan_list_from_file(self):
        """刷新计划号列表 - 从数据库读取数据
        
        此方法供以下场景使用：
        1. 启动主程序时加载数据
        2. 点击刷新按钮时
        3. 导出装炉顺序文件后更新列表
        
        Returns:
            bool: 是否成功加载数据
        """
        try:
            import sqlite3
            import os
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 从数据库获取装炉顺序数据，包括每个计划号的最小和最大钢卷号
            cursor.execute('''
                SELECT plan_no, COUNT(*) as count, MIN(coil_no) as min_coil, MAX(coil_no) as max_coil
                FROM plan_order 
                GROUP BY plan_no 
                ORDER BY MIN(order_no)
            ''')
            plan_counts = cursor.fetchall()
            
            # 获取计划号文件夹中的所有xls文件
            plan_dir = os.path.join(self.plan_dir, "计划号")
            plan_files = set()
            if os.path.exists(plan_dir):
                for f in os.listdir(plan_dir):
                    if f.endswith('.xls') or f.endswith('.xlsx'):
                        # 去掉扩展名获取计划号
                        plan_no_from_file = os.path.splitext(f)[0]
                        plan_files.add(plan_no_from_file)
            
            # 获取backup文件夹中的所有xls文件
            backup_dir = os.path.join(plan_dir, "backup")
            if os.path.exists(backup_dir):
                for f in os.listdir(backup_dir):
                    if f.endswith('.xls') or f.endswith('.xlsx'):
                        # 去掉扩展名获取计划号
                        plan_no_from_file = os.path.splitext(f)[0]
                        plan_files.add(plan_no_from_file)
            
            print(f"计划号文件夹和backup文件夹中找到 {len(plan_files)} 个文件")
            
            self.plan_data = []
            total_count = 0
            no_file_count = 0
            
            for plan_no, count, min_coil, max_coil in plan_counts:
                # 检查是否有对应的文件
                status = ''
                has_low_roll_width = False
                
                if plan_no not in plan_files:
                    status = '无文件'
                    no_file_count += 1
                    print(f"计划号 {plan_no} 无对应文件")
                else:
                    # 检查计划号文件中的轧宽数据
                    file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                    if not os.path.exists(file_path):
                        # 检查backup目录
                        backup_path = os.path.join(backup_dir, f"{plan_no}.xls")
                        if os.path.exists(backup_path):
                            file_path = backup_path
                    
                    if os.path.exists(file_path):
                        try:
                            import xlrd
                            # 读取Excel文件
                            workbook = xlrd.open_workbook(file_path)
                            sheet = workbook.sheet_by_index(0)
                            
                            # 查找字段列名行
                            字段列名行号 = -1
                            for row_idx in range(min(10, sheet.nrows)):
                                row_has_field_names = False
                                for col_idx in range(sheet.ncols):
                                    cell_value = str(sheet.cell_value(row_idx, col_idx))
                                    if any(field in cell_value for field in ["序号", "钢卷号", "牌号", "坯厚", "轧厚", "轧宽", "装炉顺"]):
                                        row_has_field_names = True
                                        break
                                if row_has_field_names:
                                    字段列名行号 = row_idx
                                    break
                            
                            if 字段列名行号 != -1:
                                # 获取列名
                                current_columns = []
                                for i in range(sheet.ncols):
                                    current_columns.append(sheet.cell_value(字段列名行号, i))
                                
                                # 查找轧宽列
                                轧宽列索引 = -1
                                for col_idx, col_name in enumerate(current_columns):
                                    if "轧宽" in col_name:
                                        轧宽列索引 = col_idx
                                        break
                                
                                if 轧宽列索引 != -1:
                                    # 检查数据行中的轧宽值
                                    for row_idx in range(字段列名行号 + 1, sheet.nrows):
                                        轧宽值 = sheet.cell_value(row_idx, 轧宽列索引)
                                        try:
                                            # 去除可能的标记（如Δ）
                                            轧宽值_clean = str(轧宽值).strip().replace('Δ', '')
                                            轧宽数值 = float(轧宽值_clean)
                                            if 轧宽数值 <= 930:
                                                has_low_roll_width = True
                                                break
                                        except (ValueError, TypeError):
                                            pass
                        except Exception as e:
                            print(f"检查轧宽时出错 {plan_no}: {str(e)}")
                
                # 清理钢卷号，只保留数字
                def clean_coil_no(coil_no):
                    if coil_no:
                        return ''.join(c for c in str(coil_no) if c.isdigit())
                    return ''
                
                min_coil_clean = clean_coil_no(min_coil)
                max_coil_clean = clean_coil_no(max_coil)
                
                self.plan_data.append({
                    'plan_no': plan_no,
                    'count': count,
                    'status': status,
                    'min_coil': min_coil_clean,
                    'max_coil': max_coil_clean,
                    'has_low_roll_width': has_low_roll_width
                })
                total_count += count
            
            # 关闭数据库连接
            conn.close()
            
            self.update_listbox()
            self.stats_label.config(text=f"总块数: {total_count} | 无文件: {no_file_count}")
            
            print(f"成功加载 {len(self.plan_data)} 个计划号，总计 {total_count} 块，无文件 {no_file_count} 个")
            return True
            
        except Exception as e:
            self.custom_messagebox("错误", f"加载数据失败: {str(e)}")
            return False
    
    def update_listbox(self):
        """更新列表框显示"""
        # 清空Treeview
        for item in self.listbox.get_children():
            self.listbox.delete(item)
        
        for item in self.plan_data:
            plan_no = item['plan_no']
            count = item['count']
            status = item['status']
            min_coil = item.get('min_coil', '')
            max_coil = item.get('max_coil', '')
            
            # 构建状态文本
            status_text = ""
            if status:
                status_text += f"[{status}] "
            if plan_no in self.processed_plans:
                status_text += f"[已处理] "
            if plan_no in self.printed_plans:
                status_text += f"[已打印] "
            if plan_no in self.no_aps_plans:
                status_text += f"[无APS] "
            if item.get('has_low_roll_width', False):
                status_text += f"[轧宽<930] "
            
            # 构建钢卷号范围文本
            coil_text = ""
            if min_coil and max_coil:
                coil_text = f"[{min_coil}-{max_coil}]"  # 使用连字符替代波浪号
            
            # 确定使用的标签
            tags = []
            if plan_no in self.newly_exported_plans:
                tags.append('green')
            # 轧宽预警或无APS时使用红色字体
            if item.get('has_low_roll_width', False) or plan_no in self.no_aps_plans:
                tags.append('red')
            
            # 插入到Treeview
            if tags:
                self.listbox.insert('', tk.END, values=(plan_no, count, status_text.strip(), coil_text), tags=tags)
            else:
                # 普通计划号使用默认字体
                self.listbox.insert('', tk.END, values=(plan_no, count, status_text.strip(), coil_text))
        
        # 配置标签
        self.listbox.tag_configure('green', foreground='green')
        self.listbox.tag_configure('red', foreground='red')
    
    def on_item_click(self, event):
        """鼠标左键点击事件处理，实现直接点击多选"""
        # 获取点击的项目
        item = self.listbox.identify_row(event.y)
        if not item:
            return
        
        # 检查是否已经被选中
        if item in self.listbox.selection():
            # 如果已经选中，则取消选择
            self.listbox.selection_remove(item)
        else:
            # 如果未选中，则添加选择
            self.listbox.selection_add(item)
        
        # 触发选择事件
        self.on_select(event)
        
        # 阻止默认的选择行为
        return "break"
    
    def on_select(self, event):
        """选择事件处理"""
        # 检查是否正在执行全选或取消全选操作
        if getattr(self, 'is_selecting_all', False):
            return
        
        selection = self.listbox.selection()
        # 转换为索引集合
        self.selected_items = set()
        for item in selection:
            # 获取项的索引
            index = self.listbox.index(item)
            self.selected_items.add(index)
    
    def select_all(self):
        """全选"""
        # 设置标志，避免触发on_select方法
        self.is_selecting_all = True
        # 先清除所有选择
        self.listbox.selection_set(())
        # 添加所有项到选择中
        for item in self.listbox.get_children():
            self.listbox.selection_add(item)
        # 更新选中项集合
        self.selected_items = set(range(len(self.plan_data)))
        # 清除标志
        self.is_selecting_all = False
    
    def deselect_all(self):
        """取消全选"""
        # 设置标志，避免触发on_select方法
        self.is_selecting_all = True
        # 直接清除Treeview的所有选择
        self.listbox.selection_set(())
        # 直接清空selected_items集合
        self.selected_items = set()
        # 清除标志
        self.is_selecting_all = False
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 检查是否有选中的计划号
        selection = self.listbox.selection()
        if not selection:
            return
        
        # 创建右键菜单，设置字体大小与列表框一致
        context_menu = tk.Menu(self.root, tearoff=0, font=('宋体', 30))
        
        # 添加显示选项
        context_menu.add_command(label="显示", command=self.show_selected)
        
        # 添加处理选项
        context_menu.add_command(label="处理", command=lambda: self.process_plans(auto_print=False))
        
        # 添加打印选项
        context_menu.add_command(label="打印", command=self.print_selected)
        
        # 显示菜单
        context_menu.post(event.x_root, event.y_root)
    
    def mark_selected_as_processed(self):
        """标注选中的计划号为已处理"""
        selection = self.listbox.selection()
        if not selection:
            return
        
        # 转换为索引集合
        selected_indices = []
        for item in selection:
            index = self.listbox.index(item)
            selected_indices.append(index)
        
        for i in selected_indices:
            plan_no = self.plan_data[i]['plan_no']
            self.processed_plans.add(plan_no)
        
        # 保存状态
        self.save_processed_plans()
        # 更新列表显示
        self.update_listbox()
        
        print(f"已将 {len(selected_indices)} 个计划号标注为已处理")
    
    def mark_selected_as_printed(self):
        """标注选中的计划号为已打印"""
        selection = self.listbox.selection()
        if not selection:
            return
        
        # 转换为索引集合
        selected_indices = []
        for item in selection:
            index = self.listbox.index(item)
            selected_indices.append(index)
        
        for i in selected_indices:
            plan_no = self.plan_data[i]['plan_no']
            self.printed_plans.add(plan_no)
        
        # 保存状态
        self.save_printed_plans()
        # 更新列表显示
        self.update_listbox()
        
        print(f"已将 {len(selected_indices)} 个计划号标注为已打印")
    
    def remove_no_file_mark(self):
        """去除选中计划号的无文件标注"""
        selection = self.listbox.selection()
        if not selection:
            return
        
        # 重新加载计划号文件状态，去除无文件标注
        self.refresh_plan_list_from_file()
        
        print(f"已去除 {len(selection)} 个计划号的无文件标注")
    
    def refresh_data(self):
        """刷新数据"""
        # 扫描并重命名计划号文件
        self.scan_and_rename_plan_files()
        # 刷新计划号列表（load_data会自动加载状态）
        self.load_data()
    
    def on_anti_logout_toggle(self):
        """防退出登录选项状态变化处理"""
        if self.anti_logout_var.get():
            self.start_anti_logout()
        else:
            self.stop_anti_logout()
    
    def anti_logout_action(self):
        """防退出登录动作：激活选择窗口，按下F2键，返回当前画面"""
        try:
            # 保存当前窗口句柄
            import win32gui
            current_hwnd = win32gui.GetForegroundWindow()
            
            # 从设置中获取选择的窗口标题（优先使用自定义窗口名称）
            custom_title = self.coordinates.get("custom_window_title", "").strip()
            if custom_title:
                window_title = custom_title
            else:
                window_title = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            
            # 激活目标窗口
            if self.activate_window(window_title):
                # 等待窗口激活
                import time
                time.sleep(0.5)
                
                # 按下F2键
                import pyautogui
                pyautogui.press('f2')
                
                # 等待按键操作完成
                time.sleep(0.5)
                
                # 激活回之前的窗口
                if current_hwnd:
                    win32gui.SetForegroundWindow(current_hwnd)
        except Exception as e:
            print(f"防退出登录动作失败: {e}")
    
    def start_anti_logout(self):
        """开始防退出登录"""
        if not self.PYAUTOGUI_AVAILABLE:
            self.custom_messagebox("错误", "pyautogui未安装，请先安装: pip install pyautogui")
            self.anti_logout_var.set(False)
            return
        
        # 启动定时器，每隔5秒执行一次
        import threading
        def timer_function():
            while self.is_anti_logout_running:
                self.anti_logout_action()
                import time
                time.sleep(5)
        
        self.is_anti_logout_running = True
        self.anti_logout_timer = threading.Thread(target=timer_function, daemon=True)
        self.anti_logout_timer.start()
        print("防退出登录已启动，每隔5秒激活窗口并按下F2键")
    
    def stop_anti_logout(self):
        """停止防退出登录"""
        self.is_anti_logout_running = False
        print("防退出登录已停止")
    

    
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
        
        # 检查是否启用调试模式
        debug_mode = self.coordinates.get("debug_mode", False)
        
        # 如果启用调试模式，创建或复用调试信息窗口
        if debug_mode:
            # 检查是否已存在调试窗口
            if hasattr(self, 'debug_window') and self.debug_window is not None:
                try:
                    # 检查窗口是否还存在
                    self.debug_window.winfo_exists()
                    # 清空现有内容
                    self.debug_text.delete(1.0, tk.END)
                    self.debug_text.insert(tk.END, "=== 新的自动导出开始 ===\n\n")
                    self.debug_text.see(tk.END)
                    self.debug_window.update()
                except:
                    # 窗口可能已关闭，重新创建
                    self.debug_window = None
                    self.debug_text = None
            
            # 如果窗口不存在，创建新窗口
            if not hasattr(self, 'debug_window') or self.debug_window is None:
                self.debug_window = tk.Toplevel(self.root)
                self.debug_window.title("调试信息 - 自动导出")
                self.debug_window.geometry("400x300")
                # 不设置topmost，让激活窗口在最前面
                
                tk.Label(self.debug_window, text="自动导出调试信息", font=('微软雅黑', 12, 'bold')).pack(pady=3)
                
                self.debug_text = tk.Text(self.debug_window, wrap=tk.WORD, font=('Consolas', 9))
                self.debug_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
                
                scrollbar = tk.Scrollbar(self.debug_text)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                self.debug_text.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=self.debug_text.yview)
                
                # 添加关闭事件处理 - 窗口可以单独关闭
                def on_debug_window_close():
                    if self.debug_window is not None:
                        self.debug_window.destroy()
                    self.debug_window = None
                    self.debug_text = None
                
                self.debug_window.protocol("WM_DELETE_WINDOW", on_debug_window_close)
            
            def add_debug_log(msg):
                if self.debug_text is not None and self.debug_window is not None:
                    try:
                        # 检查窗口是否还存在
                        if self.debug_window.winfo_exists():
                            self.debug_text.insert(tk.END, msg + "\n")
                            self.debug_text.see(tk.END)
                            self.debug_window.update()
                    except:
                        # 窗口已关闭，忽略错误
                        pass
        else:
            def add_debug_log(msg):
                pass  # 非调试模式下不输出
        
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
            # 步骤0：系统健康检查和自动修复
            update_progress("【步骤0/4】系统健康检查和自动修复...")
            print("\n=== 步骤0：系统健康检查和自动修复 ===")
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("【步骤0/4】系统健康检查和自动修复")
            add_debug_log("="*60)
            
            # 检查系统状态
            add_debug_log("检查系统状态...")
            warnings = self.check_and_warn()
            if warnings:
                add_debug_log(f"发现 {len(warnings)} 个潜在问题")
                
                # 执行自动修复
                add_debug_log("执行自动修复...")
                repair_results = self.auto_repair()
                add_debug_log(f"修复结果: 清理Excel进程 {repair_results['excel_processes_killed']} 个, 创建目录 {repair_results['directories_created']} 个")
                update_progress("【步骤0/4】系统健康检查和自动修复...", f"已修复 {repair_results['excel_processes_killed']} 个Excel进程")
            else:
                add_debug_log("系统状态正常，无预警信息")
                update_progress("【步骤0/4】系统健康检查和自动修复...", "系统状态正常")
            
            add_debug_log("系统健康检查和自动修复完成")
            update_progress("✓ 系统健康检查和自动修复完成")
            time.sleep(1)
            
            # 步骤1：导出装炉顺序
            update_progress("【步骤1/4】正在导出装炉顺序...")
            print("\n=== 步骤1：导出装炉顺序 ===")
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("【步骤1/4】导出装炉顺序")
            add_debug_log("="*60)
            
            success1, log1 = self.export_zhuanglu_shunxu(add_debug_log=add_debug_log)
            print(log1)
            
            if not success1:
                progress_window.destroy()
                self.custom_messagebox("错误", log1)
                return
            
            update_progress("✓ 装炉顺序导出完成", "等待文件保存...")
            # 步骤2：导出总计划号列表
            update_progress("【步骤2/4】正在导出总计划号列表...")
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("【步骤2/4】导出总计划号列表")
            add_debug_log("="*60)
            print("\n=== 步骤2：导出总计划号列表 ===")
            
            test_window_zhizhi = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
            success3 = self.export_zhizhi_plan_list(test_window=test_window_zhizhi, add_debug_log=add_debug_log)
            
            if not success3:
                add_debug_log(f"✗ 总计划号列表导出失败")
                progress_window.destroy()
                return
            
            update_progress("✓ 总计划号列表导出完成", "等待文件保存...")
            add_debug_log(f"✓ 总计划号列表导出完成")
            time.sleep(1)
            
            # 步骤3：重新计算坐标
            update_progress("【步骤3/4】正在重新计算坐标...")
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("【步骤3/4】重新计算坐标")
            add_debug_log("="*60)
            print("\n=== 步骤3：重新计算坐标 ===")
            
            # 定义计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            # 读取总计划号列表并计算坐标（会自动更新缓存）
            add_debug_log(f"")
            add_debug_log(f"[读取文件] 总计划号列表.xls")
            plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
            add_debug_log(f"  路径: {plan_list_file}")
            add_debug_log(f"  存在: {'是' if os.path.exists(plan_list_file) else '否'}")
            
            coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=add_debug_log)
            
            if not coord_map:
                add_debug_log(f"✗ 坐标计算失败")
                progress_window.destroy()
                # 检查文件是否存在
                plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
                if not os.path.exists(plan_list_file):
                    self.custom_messagebox("错误", f"无法计算计划号坐标\n\n原因：总计划号列表文件不存在\n路径：{plan_list_file}\n\n请先执行步骤3导出总计划号列表")
                else:
                    self.custom_messagebox("错误", "无法计算计划号坐标\n\n原因：读取总计划号列表文件失败\n\n可能原因：\n1. 文件被占用\n2. 文件格式错误\n3. 未找到计划号列")
                return
            
            add_debug_log(f"  计算到 {len(coord_map)} 个计划号坐标")
            for plan_no, coord in list(coord_map.items())[:5]:  # 只显示前5个
                add_debug_log(f"    {plan_no}: {coord}")
            if len(coord_map) > 5:
                add_debug_log(f"    ... 还有 {len(coord_map) - 5} 个")
            
            update_progress("✓ 坐标计算完成", f"共 {len(coord_map)} 个计划号坐标")
            add_debug_log(f"✓ 坐标计算完成")
            time.sleep(0.5)
            
            # 步骤4：导出无文件计划号的明细
            update_progress("【步骤4/4】正在导出无文件计划号明细...")
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("【步骤4/4】导出无文件计划号明细")
            add_debug_log("="*60)
            print("\n=== 步骤4：导出无文件计划号明细 ===")
            
            # 获取标识为"无文件"的计划号
            no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
            add_debug_log(f"")
            add_debug_log(f"[筛选计划号] 状态='无文件'")
            add_debug_log(f"  找到 {len(no_file_plans)} 个无文件的计划号")
            add_debug_log(f"  计划号列表: {no_file_plans}")
            print(f"找到 {len(no_file_plans)} 个无文件的计划号: {no_file_plans}")
            
            if not no_file_plans:
                add_debug_log(f"✗ 没有需要导出的计划号")
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
                add_debug_log(f"✗ 未设置计划明细导出按钮坐标")
                progress_window.destroy()
                self.custom_messagebox("错误", "未设置计划明细导出按钮坐标")
                return
            
            add_debug_log(f"")
            add_debug_log(f"[配置信息]")
            add_debug_log(f"  计划明细导出按钮坐标: {plan_detail_export_btn}")
            add_debug_log(f"  导出速度: {test_speed} (延迟: {delay_time}s)")
            
            exported_plans = []
            failed_plans = []
            
            add_debug_log(f"")
            add_debug_log(f"="*60)
            add_debug_log(f"开始导出计划号明细")
            add_debug_log(f"="*60)
            
            for i, plan_no in enumerate(no_file_plans):
                update_progress(f"【{i+1}/{len(no_file_plans)}】正在导出 {plan_no}...", f"剩余 {len(no_file_plans)-i-1} 个")
                print(f"\n[{i+1}/{len(no_file_plans)}] 导出计划: {plan_no}")
                
                add_debug_log(f"")
                add_debug_log(f"[{i+1}/{len(no_file_plans)}] 导出计划: {plan_no}")
                
                coord = coord_map.get(plan_no)
                if not coord:
                    add_debug_log(f"  ✗ 找不到计划号 {plan_no} 的坐标")
                    print(f"✗ 找不到计划号 {plan_no} 的坐标")
                    failed_plans.append(plan_no)
                    continue
                
                add_debug_log(f"  坐标: {coord}")
                add_debug_log(f"  开始执行导出操作...")
                
                success = self.export_single_plan_detail(plan_no, coord, plan_detail_export_btn, test_window, add_debug_log)
                
                if success:
                    exported_plans.append(plan_no)
                    add_debug_log(f"  ✓ 导出成功")
                    # 不标记为已处理，保持"无文件"状态，等待下次刷新
                    # self.mark_plan_as_exported(plan_no)
                else:
                    failed_plans.append(plan_no)
                    add_debug_log(f"  ✗ 导出失败")
                
                if i < len(no_file_plans) - 1:
                    add_debug_log(f"  延迟: {delay_time}s (准备导出下一个)")
                    time.sleep(delay_time)
            
            progress_window.destroy()
            
            add_debug_log(f"")
            add_debug_log(f"="*60)
            add_debug_log(f"自动导出全部完成")
            add_debug_log(f"="*60)
            add_debug_log(f"装炉顺序: ✓")
            add_debug_log(f"总计划号列表: ✓")
            add_debug_log(f"坐标重新计算: ✓")
            add_debug_log(f"计划号明细导出: {len(exported_plans)} 个成功, {len(failed_plans)} 个失败")
            if exported_plans:
                add_debug_log(f"  成功: {exported_plans}")
            if failed_plans:
                add_debug_log(f"  失败: {failed_plans}")
            
            print("\n=== 自动导出全部完成 ===")
            print(f"装炉顺序: ✓")
            print(f"总计划号列表: ✓")
            print(f"坐标重新计算: ✓")
            print(f"计划号明细导出: {len(exported_plans)} 个成功, {len(failed_plans)} 个失败")
            
            # 刷新计划号列表，更新状态
            add_debug_log(f"")
            add_debug_log(f"[刷新计划号列表]")
            print("\n刷新计划号列表...")
            self.refresh_plan_list_from_file()
            add_debug_log(f"✓ 计划号列表刷新完成")
            print("✓ 计划号列表刷新完成")
            
            # 标记新导出的计划号
            self.newly_exported_plans.clear()
            for plan_no in exported_plans:
                self.newly_exported_plans.add(plan_no)
            
            # 检查是否需要自动处理和自动打印
            auto_process = self.coordinates.get("auto_process_after_export", False)
            auto_print = self.coordinates.get("auto_print_after_export", False)
            
            if exported_plans:
                # 选中刚刚导出的计划号
                if not isinstance(self.selected_items, set):
                    self.selected_items = set()
                else:
                    self.selected_items.clear()
                for i, plan_data in enumerate(self.plan_data):
                    if plan_data['plan_no'] in exported_plans:
                        self.selected_items.add(i)
                
                # 根据选项决定执行逻辑
                if auto_print:
                    # 第二个选项选中，直接处理并打印
                    print("\n=== 自动执行计划处理并打印 ===")
                    self.process_plans(auto_print=True)
                elif auto_process:
                    # 第一个选项选中，直接处理但不打印
                    print("\n=== 自动执行计划处理 ===")
                    self.process_plans(auto_print=False)
                else:
                    # 两个选项都未选中，显示确认弹窗
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
                        # 自动处理选中的计划号（默认不自动打印）
                        self.process_plans(auto_print=False)
            
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
        import sys
        import time
        
        # 确保QApplication实例存在
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 导入需要的PyQt5组件
        from PyQt5.QtWidgets import QLineEdit, QMessageBox
        from PyQt5.QtCore import QTimer, QEvent, Qt
        from PyQt5.QtGui import QColor, QBrush
        
        # 定义主题配色方案
        主题配色 = {
            "默认": {
                "窗口背景": "#f0f0f0",
                "表格背景": "#FFFFFF",
                "表格文字": "#000000",
                "表头背景": "#E8E8E8",
                "表头文字": "#000000",
                "选中行": "#0078D7",
                "选中行文字": "#FFFFFF",
                "悬停行": "#E3F2FD",
                "悬停行文字": "#000000",
                "高亮标记": "#FFFF00",
                "提示框背景": "#ffffcc",
                "提示框文字": "#000000",
                "边框": "#CCCCCC"
            },
            "护眼模式": {
                "窗口背景": "#E8F5E9",
                "表格背景": "#F1F8E9",
                "表格文字": "#2E7D32",
                "表头背景": "#C8E6C9",
                "表头文字": "#2E7D32",
                "选中行": "#4CAF50",
                "选中行文字": "#FFFFFF",
                "悬停行": "#DCEDC8",
                "悬停行文字": "#2E7D32",
                "高亮标记": "#FFF9C4",
                "提示框背景": "#E8F5E9",
                "提示框文字": "#2E7D32",
                "边框": "#A5D6A7"
            },
            "鲜明模式": {
                "窗口背景": "#E3F2FD",
                "表格背景": "#FFFFFF",
                "表格文字": "#1976D2",
                "表头背景": "#2196F3",
                "表头文字": "#FFFFFF",
                "选中行": "#64B5F6",
                "选中行文字": "#000000",
                "悬停行": "#BBDEFB",
                "悬停行文字": "#1976D2",
                "高亮标记": "#FFD54F",
                "提示框背景": "#E3F2FD",
                "提示框文字": "#1976D2",
                "边框": "#90CAF9"
            },
            "暗黑模式": {
                "窗口背景": "#2E2E2E",
                "表格背景": "#3E3E3E",
                "表格文字": "#E0E0E0",
                "表头背景": "#4E4E4E",
                "表头文字": "#E0E0E0",
                "选中行": "#5A5A5A",
                "选中行文字": "#FFFFFF",
                "悬停行": "#4A4A4A",
                "悬停行文字": "#E0E0E0",
                "高亮标记": "#FFD700",
                "提示框背景": "#3E3E3E",
                "提示框文字": "#E0E0E0",
                "边框": "#5E5E5E"
            },
            "柔和模式": {
                "窗口背景": "#F5F5F5",
                "表格背景": "#FFFFFF",
                "表格文字": "#666666",
                "表头背景": "#E0E0E0",
                "表头文字": "#666666",
                "选中行": "#B0BEC5",
                "选中行文字": "#000000",
                "悬停行": "#ECEFF1",
                "悬停行文字": "#666666",
                "高亮标记": "#FFF3E0",
                "提示框背景": "#F5F5F5",
                "提示框文字": "#666666",
                "边框": "#E0E0E0"
            },
            "自定义": {
                "窗口背景": "#f0f0f0",
                "表格背景": "#FFFFFF",
                "表格文字": "#000000",
                "表头背景": "#E8E8E8",
                "表头文字": "#000000",
                "选中行": "#0078D7",
                "选中行文字": "#FFFFFF",
                "悬停行": "#E3F2FD",
                "悬停行文字": "#000000",
                "高亮标记": "#FFFF00",
                "提示框背景": "#ffffcc",
                "提示框文字": "#000000",
                "边框": "#CCCCCC"
            }
        }
        
        # 当前主题
        当前主题 = "默认"
        
        # 列名（按照用户要求的顺序：计划号 钢卷号 牌号（钢级）坯宽 减宽 调宽 轧宽 公差带 粗轧报信 除鳞 坯厚 坯长 轧厚 中厚  RT2 强度  切边 去向  订宽 坯头部宽 坯尾部宽 热轧产品分类 炼钢钢种 负公差 正公差 回炉坯 原轧宽）
        columns = [
            "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
            "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
            "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
        ]
        
        # 列宽配置
        # 固定列宽配置（像素）
        列宽配置 = {
            "计划号": 110,
            "钢卷号": 190,
            "牌号（钢级）": 210,
            "除鳞": 110,
            "去向": 65,
            "坯厚": 80,
            "坯宽": 90,
            "坯长": 95,
            "中厚": 65,
            "轧厚": 70,
            "轧宽": 90,
            "订宽": 90,
            "切边": 70,
            "调宽": 75,
            "减宽": 85,
            "公差带": 120,
            "RT2": 75,
            "强度": 60,
            "粗轧报信":360,
            "坯头部宽": 120,
            "坯尾部宽": 120,
            "热轧产品分类": 110,
            "炼钢钢种": 210,
            "负公差": 90,
            "正公差": 90,
            "回炉坯": 90,
            "原轧宽": 90
        }
        
        # 创建主窗口
        detail_window = QMainWindow()
        detail_window.setWindowTitle("装炉明细")
        detail_window.resize(1000, 600)
        detail_window.showMaximized()
        
        # 创建中心部件
        central_widget = QWidget()
        detail_window.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建自定义表格类，确保标注单元格始终保持红色背景
        from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QPainter, QColor, QBrush
        
        class CustomTableWidget(QTableWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
            
            def paintEvent(self, event):
                # 调用父类的paintEvent
                super().paintEvent(event)
                
                # 重新绘制标注单元格，确保它们保持红色背景
                painter = QPainter(self.viewport())
                for row in range(self.rowCount()):
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        if item and item.background().color().name() == '#ff0000':
                            # 获取单元格的矩形
                            rect = self.visualRect(self.model().index(row, col))
                            # 绘制红色背景
                            painter.fillRect(rect, QBrush(QColor('#FF0000')))
                            # 绘制文字
                            painter.setPen(QColor('white'))
                            painter.setFont(item.font())
                            painter.drawText(rect, item.textAlignment(), item.text())
        
        # 表格
        table = CustomTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        for i, col in enumerate(columns):
            width = 列宽配置.get(col, 70)
            table.setColumnWidth(i, width)
        
        # 设置行高
        table.verticalHeader().setDefaultSectionSize(80)
        
        # 隐藏垂直表头（序号列）
        table.verticalHeader().setVisible(False)
        
        # 设置字体
        font = QFont("微软雅黑", 20, QFont.Bold)
        table.setFont(font)
        
        # 设置表头字体
        header_font = QFont("微软雅黑", 20, QFont.Bold)
        table.horizontalHeader().setFont(header_font)
        
        # 设置表格不可编辑
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置点击单元格时选中整行
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        # 添加表格到布局
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(table)
        main_layout.addWidget(scroll_area)
        
        # 底部布局
        bottom_layout = QVBoxLayout()
        main_layout.addLayout(bottom_layout)
        
        # 状态标签行
        status_layout = QHBoxLayout()
        status_layout.setAlignment(Qt.AlignCenter)
        bottom_layout.addLayout(status_layout)
        
        # 块数显示
        block_count_label = QLabel("正在加载...")
        block_count_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        status_layout.addWidget(block_count_label)
        
        # 右侧滚动状态和输入
        scroll_container = QWidget()
        scroll_layout = QHBoxLayout(scroll_container)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)
        # 设置垂直居中
        scroll_layout.setAlignment(Qt.AlignVCenter)
        
        # 自动滚动状态
        scroll_status_label = QLabel("")
        scroll_status_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        scroll_status_label.setAlignment(Qt.AlignRight)
        scroll_layout.addWidget(scroll_status_label)
        
        # 滚动时间输入框（直接显示，无标签）
        scroll_time_edit = QLineEdit("110")
        scroll_time_edit.setFont(QFont("微软雅黑", 14))
        scroll_time_edit.setFixedWidth(80)
        # 设置占位符提示
        scroll_time_edit.setPlaceholderText("滚动间隔(秒)")
        scroll_layout.addWidget(scroll_time_edit)
        

        
        # 将滚动容器添加到状态布局的右侧
        status_layout.addStretch()
        status_layout.addWidget(scroll_container)
        
        # 按钮容器
        button_container = QHBoxLayout()
        button_container.setAlignment(Qt.AlignCenter)
        # 设置按钮容器的间距
        button_container.setSpacing(5)
        bottom_layout.addLayout(button_container)
        
        # 中间按钮组（居中）
        center_buttons = QHBoxLayout()
        button_container.addLayout(center_buttons)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.setFont(QFont("微软雅黑", 14))
        refresh_btn.setFixedWidth(100)
        refresh_btn.setFixedHeight(40)
        center_buttons.addWidget(refresh_btn)
        
        # 显示按钮
        show_btn = QPushButton("显示")
        show_btn.setFont(QFont("微软雅黑", 14))
        show_btn.setFixedWidth(100)
        show_btn.setFixedHeight(40)
        center_buttons.addWidget(show_btn)
        
        # 打印按钮
        print_btn = QPushButton("打印")
        print_btn.setFont(QFont("微软雅黑", 14))
        print_btn.setFixedWidth(100)
        print_btn.setFixedHeight(40)
        center_buttons.addWidget(print_btn)
        
        # 返回按钮
        return_btn = QPushButton("返回")
        return_btn.setFont(QFont("微软雅黑", 14))
        return_btn.setFixedWidth(100)
        return_btn.setFixedHeight(40)
        center_buttons.addWidget(return_btn)
        
        # 主题按钮
        theme_btn = QPushButton("主题")
        theme_btn.setFont(QFont("微软雅黑", 14))
        theme_btn.setFixedWidth(100)
        theme_btn.setFixedHeight(40)
        center_buttons.addWidget(theme_btn)
        
        # 右侧伸缩空间
        button_container.addStretch()
        
        # 最右侧滚动按钮组（靠右）
        right_controls = QHBoxLayout()
        button_container.addLayout(right_controls)
        # 设置垂直居中
        right_controls.setAlignment(Qt.AlignVCenter)
        
        # 开始滚动按钮
        start_scroll_btn = QPushButton("开始")
        start_scroll_btn.setFont(QFont("微软雅黑", 14))
        start_scroll_btn.setFixedWidth(80)
        start_scroll_btn.setFixedHeight(40)
        right_controls.addWidget(start_scroll_btn)
        
        # 增加按钮之间的间距
        right_controls.addSpacing(15)
        
        # 停止滚动按钮
        stop_scroll_btn = QPushButton("停止")
        stop_scroll_btn.setFont(QFont("微软雅黑", 14))
        stop_scroll_btn.setFixedWidth(80)
        stop_scroll_btn.setFixedHeight(40)
        right_controls.addWidget(stop_scroll_btn)
        
        def apply_theme(theme_name):
            """应用主题"""
            nonlocal 当前主题
            当前主题 = theme_name
            colors = 主题配色[theme_name]
            
            # 设置窗口背景
            central_widget.setStyleSheet(f"background-color: {colors['窗口背景']};")
            
            # 设置表格背景和文字
            table.setStyleSheet(f"""
                QTableWidget {{ background-color: {colors['表格背景']}; color: {colors['表格文字']}; }}
                QHeaderView::section {{ background-color: {colors['表头背景']}; color: {colors['表头文字']}; }}
                QTableWidget::item:selected {{ background-color: {colors['选中行']}; color: {colors['选中行文字']}; }}
                QTableWidget::item:hover {{ background-color: {colors['悬停行']}; color: {colors['悬停行文字']}; }}
            """)
            
            # 更新按钮样式
            button_style = f"""
                QPushButton {{ 
                    background-color: {colors['表头背景']}; 
                    color: {colors['表头文字']}; 
                    border: 1px solid {colors['边框']}; 
                    border-radius: 4px;
                }}
                QPushButton:hover {{ 
                    background-color: {colors['悬停行']}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {colors['选中行']}; 
                }}
            """
            refresh_btn.setStyleSheet(button_style)
            show_btn.setStyleSheet(button_style)
            print_btn.setStyleSheet(button_style)
            return_btn.setStyleSheet(button_style)
            theme_btn.setStyleSheet(button_style)
            start_scroll_btn.setStyleSheet(button_style)
            stop_scroll_btn.setStyleSheet(button_style)
            
            # 更新状态标签
            block_count_label.setStyleSheet(f"color: {colors['表格文字']};")
            scroll_status_label.setStyleSheet(f"color: {colors['表格文字']};")
        
        # 自动滚动相关变量
        scroll_timer = QTimer()
        is_scrolling = False
        current_row = 0
        
        def start_scroll():
            """开始自动滚动"""
            nonlocal is_scrolling, current_row
            
            # 获取滚动时间
            try:
                scroll_time = int(scroll_time_edit.text())
                if scroll_time < 1:
                    scroll_time = 1
            except:
                scroll_time = 5
            
            # 检查是否有选中的行
            selected_items = table.selectedItems()
            if selected_items:
                current_row = selected_items[0].row()
                # 将选中的钢卷号显示在屏幕中间，光标移到这一行
                table.selectRow(current_row)
                table.scrollToItem(selected_items[0], QTableWidget.PositionAtCenter)
            
            # 启动定时器
            scroll_timer.setInterval(scroll_time * 1000)
            # 先断开之前的连接，避免重复连接
            try:
                scroll_timer.timeout.disconnect()
            except:
                pass
            scroll_timer.timeout.connect(auto_scroll)
            scroll_timer.start()
            is_scrolling = True
            start_scroll_btn.setEnabled(False)
            stop_scroll_btn.setEnabled(True)
            scroll_status_label.setText("自动滚动中")
        
        def stop_scroll():
            """停止自动滚动"""
            nonlocal is_scrolling
            scroll_timer.stop()
            is_scrolling = False
            start_scroll_btn.setEnabled(True)
            stop_scroll_btn.setEnabled(False)
            scroll_status_label.setText("自动滚动已停止")
        
        def auto_scroll():
            """自动向上滚动 - 光标在窗口中间不动，数据往上滚动"""
            nonlocal current_row
            
            if table.rowCount() == 0:
                return
            
            # 每次向上滚动一个钢卷号（一行）
            # 为了实现数据往上滚动，我们需要让选中行向下移动
            if current_row < table.rowCount() - 1:
                # 向下移动一行，这样数据会向上滚动
                current_row += 1
            else:
                # 到达底部，回到顶部
                current_row = 0
            
            # 确保选中行在屏幕中间
            table.selectRow(current_row)
            table.scrollToItem(table.item(current_row, 0), QTableWidget.PositionAtCenter)
        
        # 添加右键菜单
        from PyQt5.QtWidgets import QMenu
        
        def show_context_menu(event):
            """显示右键菜单"""
            # 获取点击位置对应的行
            row = table.rowAt(event.y())
            if row >= 0:
                # 选中该行
                table.selectRow(row)
                
                # 创建右键菜单
                context_menu = QMenu()
                start_scroll_action = context_menu.addAction("开始滚动")
                
                # 连接菜单项到槽函数
                start_scroll_action.triggered.connect(start_scroll)
                
                # 显示菜单
                context_menu.exec_(table.mapToGlobal(event))
        
        # 绑定右键菜单事件
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(show_context_menu)
        
        # 绑定单元格点击事件，用于校准当前显示行
        def on_cell_clicked(row, column):
            """当用户点击单元格时，将光标条移到该行"""
            nonlocal current_row
            # 选中点击的行
            table.selectRow(row)
            # 只有在自动滚动时才滚动数据
            if is_scrolling:
                # 将该行滚动到屏幕中间
                table.scrollToItem(table.item(row, 0), QTableWidget.PositionAtCenter)
            # 更新当前行变量
            current_row = row
            # 确保标注的单元格保持红色背景
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and item.background().color().name() == '#ff0000':
                    item.setBackground(QBrush(QColor('#FF0000')))
        
        table.cellClicked.connect(on_cell_clicked)
        
        # 绑定选择变化事件，确保标注的单元格保持红色背景
        def on_item_selection_changed():
            """当选择变化时，确保标注的单元格保持红色背景"""
            selected_rows = set()
            for item in table.selectedItems():
                selected_rows.add(item.row())
            
            for row in selected_rows:
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and item.background().color().name() == '#ff0000':
                        item.setBackground(QBrush(QColor('#FF0000')))
        
        table.itemSelectionChanged.connect(on_item_selection_changed)
        
        # 绑定鼠标移动事件，当光标移到标注的单元格时，保持单元格背景色置顶层
        def on_mouse_move(event):
            """当鼠标移动时，处理标注单元格的显示"""
            # 获取鼠标位置对应的单元格
            index = table.indexAt(event.pos())
            if index.isValid():
                row = index.row()
                col = index.column()
                item = table.item(row, col)
                if item:
                    # 检查单元格是否有红色标注背景
                    if item.background().color().name() == '#ff0000':
                        # 将标注单元格置为顶层显示
                        item.setBackground(QBrush(QColor('#FF0000')))
                        # 强制更新单元格显示
                        table.update(index)
        
        table.viewport().installEventFilter(table)
        
        # 重写eventFilter方法处理鼠标移动事件
        def eventFilter(obj, event):
            if event.type() == QEvent.MouseMove:
                on_mouse_move(event)
            return False
        
        table.eventFilter = eventFilter
        
        # 绑定按钮事件
        start_scroll_btn.clicked.connect(start_scroll)
        stop_scroll_btn.clicked.connect(stop_scroll)
        
        def show_theme_window():
            """显示主题设置窗口"""
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QColorDialog, QGridLayout, QLineEdit
            
            # 创建主题设置窗口
            theme_dialog = QDialog(detail_window)
            theme_dialog.setWindowTitle("主题设置")
            theme_dialog.resize(600, 400)
            
            # 主布局
            main_layout = QVBoxLayout(theme_dialog)
            
            # 主题选择和自定义设置的水平布局
            content_layout = QHBoxLayout()
            main_layout.addLayout(content_layout)
            
            # 左侧主题列表
            theme_list = QListWidget()
            theme_list.setFixedWidth(150)
            content_layout.addWidget(theme_list)
            
            # 填充主题列表
            for theme_name in 主题配色:
                item = QListWidgetItem(theme_name)
                if theme_name == 当前主题:
                    item.setSelected(True)
                theme_list.addItem(item)
            
            # 右侧自定义设置
            custom_layout = QVBoxLayout()
            content_layout.addLayout(custom_layout)
            
            # 颜色设置网格
            color_grid = QGridLayout()
            custom_layout.addLayout(color_grid)
            
            # 颜色项
            color_items = [
                ("窗口背景", "窗口背景"),
                ("表格背景", "表格背景"),
                ("表格文字", "表格文字"),
                ("表头背景", "表头背景"),
                ("表头文字", "表头文字"),
                ("选中行", "选中行"),
                ("选中行文字", "选中行文字"),
                ("悬停行", "悬停行"),
                ("悬停行文字", "悬停行文字"),
                ("高亮标记", "高亮标记"),
                ("提示框背景", "提示框背景"),
                ("提示框文字", "提示框文字"),
                ("边框", "边框")
            ]
            
            # 存储颜色输入框
            color_inputs = {}
            
            for i, (label_text, color_key) in enumerate(color_items):
                row = i // 2
                col = i % 2
                
                # 标签
                label = QLabel(label_text)
                color_grid.addWidget(label, row, col * 3)
                
                # 颜色输入框
                color_input = QLineEdit()
                color_input.setText(主题配色["自定义"][color_key])
                color_inputs[color_key] = color_input
                color_grid.addWidget(color_input, row, col * 3 + 1)
                
                # 颜色选择按钮
                def create_color_picker(color_key):
                    def pick_color():
                        color = QColorDialog.getColor()
                        if color.isValid():
                            color_inputs[color_key].setText(color.name())
                    return pick_color
                
                color_btn = QPushButton("选择")
                color_btn.clicked.connect(create_color_picker(color_key))
                color_grid.addWidget(color_btn, row, col * 3 + 2)
            
            # 底部按钮
            button_layout = QHBoxLayout()
            main_layout.addLayout(button_layout)
            
            # 应用按钮
            apply_btn = QPushButton("应用")
            apply_btn.clicked.connect(lambda: apply_theme(theme_list.currentItem().text()))
            button_layout.addWidget(apply_btn)
            
            # 保存自定义按钮
            save_custom_btn = QPushButton("保存自定义")
            def save_custom():
                for color_key, input_field in color_inputs.items():
                    主题配色["自定义"][color_key] = input_field.text()
                apply_theme("自定义")
            save_custom_btn.clicked.connect(save_custom)
            button_layout.addWidget(save_custom_btn)
            
            # 取消按钮
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(theme_dialog.close)
            button_layout.addWidget(cancel_btn)
            
            # 显示窗口
            theme_dialog.exec_()
        
        # 绑定主题按钮点击事件
        theme_btn.clicked.connect(show_theme_window)
        
        # 应用默认主题
        apply_theme(当前主题)
        
        # 添加按钮间距，但不影响右侧控件的间距
        for i in range(center_buttons.count()):
            if i > 0:
                center_buttons.insertSpacing(i, 10)
        
        def wrap_text(text, max_chars=18):
            """自动换行函数，英文和数字算0.5个字符，每行最多max_chars个字符"""
            if not text or len(text.strip()) == 0:
                return text
                
            # 计算字符长度（英文和数字算0.5，中文算1）
            def char_length(char):
                if char.isascii() and (char.isalnum() or char in ' .,;:!?()[]{}'):
                    return 0.5
                return 1
            
            lines = []
            current_line = ""
            current_length = 0
            
            for char in text:
                char_len = char_length(char)
                
                # 如果当前行加上这个字符会超过限制，就换行
                if current_length + char_len > max_chars:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
                    current_length = char_len
                else:
                    current_line += char
                    current_length += char_len
            
            if current_line:
                lines.append(current_line)
            
            return '\n'.join(lines)
        
        def load_furnace_data():
            """加载装炉数据"""
            try:
                import os
                import tempfile
                import shutil
                import xlrd
                import time
                
                # 读取装炉顺序.xls
                plan_dir = os.path.join(self.plan_dir, "计划号")
                excel_file = os.path.join(plan_dir, "装炉顺序.xls")
                
                print(f"查找装炉顺序文件: {excel_file}")
                
                if not os.path.exists(excel_file):
                    print(f"文件不存在: {excel_file}")
                    # 显示错误信息，但继续执行
                    # 不使用模态对话框，而是直接返回空列表
                    return []
                
                # 创建临时副本（存储在计划号文件夹中）
                plan_dir = os.path.join(self.plan_dir, "计划号")
                temp_file_name = f"temp_装炉顺序_{int(time.time())}.xls"
                temp_file_path = os.path.join(plan_dir, temp_file_name)
                shutil.copy2(excel_file, temp_file_path)
                print(f"创建临时副本: {temp_file_path}")
                
                # 读取数据
                workbook = xlrd.open_workbook(temp_file_path)
                sheet = workbook.sheet_by_index(0)
                
                headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
                print(f"列名: {headers}")
                
                # 查找列索引
                order_col = None  # 装炉顺序号
                plan_col = None   # 计划号
                coil_col = None   # 钢卷号
                
                for idx, header in enumerate(headers):
                    if '装炉顺序号' in header or '装炉顺序' in header:
                        order_col = idx
                        print(f"找到装炉顺序列: {idx}")
                    elif '计划号' in header:
                        plan_col = idx
                        print(f"找到计划号列: {idx}")
                    elif '钢卷号' in header:
                        coil_col = idx
                        print(f"找到钢卷号列: {idx}")
                
                if None in [order_col, plan_col, coil_col]:
                    print(f"缺少必要列: order_col={order_col}, plan_col={plan_col}, coil_col={coil_col}")
                    # 删除临时文件
                    if os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                            print(f"删除临时文件: {temp_file_path}")
                        except Exception as e:
                            print(f"删除临时文件失败: {e}")
                    print("装炉顺序.xls文件缺少必要的列（装炉顺序、计划号、钢卷号）")
                    return []
                
                # 读取数据
                data = []
                for row in range(1, sheet.nrows):
                    try:
                        order = sheet.cell_value(row, order_col)
                        # 转换装炉顺序为整数
                        if isinstance(order, float) and order.is_integer():
                            order = int(order)
                        plan_no = str(sheet.cell_value(row, plan_col)).strip()
                        coil_no = str(sheet.cell_value(row, coil_col)).strip()
                        
                        # 清理钢卷号，只保留ASCII数字
                        coil_no = ''.join(c for c in coil_no if c.isdigit())
                        
                        if plan_no and coil_no:
                            data.append({
                                'order': order,
                                'plan_no': plan_no,
                                'coil_no': coil_no
                            })
                            print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no}")
                        else:
                            print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}'")
                    except Exception as e:
                        print(f"读取行 {row} 失败: {e}")
                        # 继续处理下一行，不中断整个加载过程
                        continue
                
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"删除临时文件: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件失败: {e}")
                
                print(f"加载到 {len(data)} 条装炉数据")
                if len(data) == 0:
                    print("装炉顺序.xls文件中没有数据")
                return data
            except Exception as e:
                print(f"加载装炉数据失败: {str(e)}")
                import traceback
                traceback.print_exc()
                # 删除临时文件
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"删除临时文件: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件失败: {e}")
                print(f"加载装炉数据失败: {str(e)}")
                return []
        
        def get_plan_file(plan_no):
            """获取计划号文件路径（从计划号目录或backup目录）"""
            import os
            # 首先在计划号目录查找
            plan_dir = os.path.join(self.plan_dir, "计划号")
            file_path = os.path.join(plan_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件: {file_path}")
                return file_path
            # 然后在backup目录查找
            backup_dir = os.path.join(plan_dir, "backup")
            if os.path.exists(backup_dir):
                file_path = os.path.join(backup_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    print(f"找到计划号文件(backup): {file_path}")
                    return file_path
            # 尝试其他可能的路径
            # 直接在计划号目录的上级目录查找
            parent_dir = os.path.dirname(plan_dir)
            file_path = os.path.join(parent_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(上级目录): {file_path}")
                return file_path
            # 尝试在当前工作目录查找
            current_dir = os.getcwd()
            file_path = os.path.join(current_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(当前目录): {file_path}")
                return file_path
            print(f"未找到计划号文件: {plan_no}.xls")
            return None
        
        def extract_coil_data(plan_file, coil_no):
            """从计划号文件中提取钢卷数据"""
            try:
                import xlrd
                print(f"提取钢卷数据: {plan_file}, 钢卷号: {coil_no}")
                workbook = xlrd.open_workbook(plan_file)
                sheet = workbook.sheet_by_index(0)
                
                # 查找列名行（跳过标题行）
                header_row = 0
                # 首先尝试找到包含"钢卷号"或"序号"的行（这是列名行的关键特征）
                for i in range(min(10, sheet.nrows)):
                    row_values = []
                    for col in range(sheet.ncols):
                        try:
                            value = str(sheet.cell_value(i, col)).strip()
                            row_values.append(value)
                        except:
                            row_values.append('')
                    # 检查是否包含"钢卷号"或"序号"列
                    has_coil_col = any('钢卷号' in v for v in row_values)
                    has_seq_col = any('序号' in v for v in row_values)
                    if has_coil_col or has_seq_col:
                        header_row = i
                        print(f"自动检测到列名行: {i+1} (包含钢卷号或序号列)")
                        break
                
                # 如果没有找到，再尝试其他方法
                if header_row == 0:
                    for i in range(min(5, sheet.nrows)):
                        row_values = []
                        for col in range(sheet.ncols):
                            try:
                                value = str(sheet.cell_value(i, col)).strip()
                                row_values.append(value)
                            except:
                                row_values.append('')
                        # 检查是否包含多个非空值（可能是列名）
                        non_empty = [v for v in row_values if v]
                        if len(non_empty) >= 5:
                            header_row = i
                            print(f"自动检测到列名行: {i+1} (包含{len(non_empty)}个非空值)")
                            break
                
                # 如果还是没有找到，尝试从第二行开始
                if header_row == 0 and sheet.nrows > 1:
                    header_row = 1
                    print("使用第二行作为列名行")
                
                # 查找列
                headers = []
                for col in range(sheet.ncols):
                    try:
                        header = str(sheet.cell_value(header_row, col)).strip()
                        headers.append(header)
                    except:
                        headers.append('')
                print(f"计划号文件列名（从第{header_row+1}行开始）: {headers}")
                
                # 直接按照字段名获取数据，因为字段名已经完全一致
                col_map = {}
                for idx, header in enumerate(headers):
                    # 直接使用表头作为键，这样可以直接对应到表格列名
                    col_map[header] = idx
                    print(f"找到列: {idx} (表头: {header})")
                
                # 如果没有找到钢卷号列，尝试自动检测
                if 'coil_no' not in col_map:
                    print("未找到钢卷号列，尝试自动检测...")
                    # 尝试从数据行中检测钢卷号列
                    if sheet.nrows > header_row + 1:
                        for col in range(sheet.ncols):
                            try:
                                # 检查前10行数据，看是否有类似钢卷号的格式
                                has_coil_like = 0
                                for row in range(header_row + 1, min(header_row + 11, sheet.nrows)):
                                    value = str(sheet.cell_value(row, col)).strip()
                                    # 清理值，只保留ASCII数字
                                    clean_value = ''.join(c for c in value if c.isdigit())
                                    # 钢卷号通常是数字，长度在8-12位
                                    if 8 <= len(clean_value) <= 12:
                                        has_coil_like += 1
                                if has_coil_like >= 3:
                                    col_map['coil_no'] = col
                                    print(f"自动检测到钢卷号列: {col}")
                                    break
                            except:
                                pass
                
                # 查找钢卷号对应的行（从列名行的下一行开始）
                found = False
                for row in range(header_row + 1, sheet.nrows):
                    try:
                        # 首先尝试使用自动检测的钢卷号列
                        coil_no_col = -1
                        if 'coil_no' in col_map:
                            coil_no_col = col_map['coil_no']
                        else:
                            # 尝试从表头中找到钢卷号列
                            for header, idx in col_map.items():
                                if '钢卷号' in header:
                                    coil_no_col = idx
                                    break
                            
                            if coil_no_col == -1:
                                # 尝试从表头中找到序号列
                                for header, idx in col_map.items():
                                    if '序号' in header:
                                        coil_no_col = idx
                                        break
                        
                        if coil_no_col != -1:
                            cell_value = str(sheet.cell_value(row, coil_no_col)).strip()
                            # 清理单元格值，只保留ASCII数字
                            clean_cell_value = ''.join(c for c in cell_value if c.isdigit())
                            # 尝试多种匹配方式
                            print(f"尝试匹配钢卷号: 目标={coil_no}, 单元格值={cell_value}, 清理后={clean_cell_value}")
                            if clean_cell_value == coil_no or cell_value == coil_no:
                                found = True
                                # 提取数据
                                data = {}
                                for header, col_idx in col_map.items():
                                    if col_idx < sheet.ncols:
                                        try:
                                            data[header] = str(sheet.cell_value(row, col_idx)).strip()
                                        except:
                                            data[header] = ''
                                print(f"找到钢卷数据: {data}")
                                return data
                            else:
                                print(f"钢卷号不匹配: 目标={coil_no}, 单元格值={cell_value}, 清理后={clean_cell_value}")
                        else:
                            print("未找到钢卷号列")
                    except Exception as e:
                        print(f"读取单元格失败: {e}")
                if not found:
                    print(f"未找到钢卷号: {coil_no} 在文件: {plan_file}")
                    # 尝试打印所有钢卷号，帮助调试
                    print("文件中的钢卷号:")
                    for row in range(header_row + 1, min(header_row + 11, sheet.nrows)):
                        if 'coil_no' in col_map:
                            try:
                                cell_value = str(sheet.cell_value(row, col_map['coil_no'])).strip()
                                print(f"  行 {row}: {cell_value}")
                            except:
                                pass
                    # 即使没有找到钢卷号，也返回一个基本的数据结构
                    # 至少包含装炉顺序、计划号和钢卷号
                    print("返回基本数据结构")
                    return {
                        'coil_no': coil_no,
                        'grade': '',
                        'scaling': '',
                        'destination': '',
                        'blank_thick': '',
                        'blank_width': '',
                        'blank_length': '',
                        'middle_thick': '',
                        'roll_thick': '',
                        'roll_width': '',
                        'order_width': '',
                        'edge_cut': '',
                        'width_adjust': '',
                        'width_reduce': '',
                        'tolerance': '',
                        'rt2': '',
                        'strength': '',
                        'rough_rolling': '',
                        'blank_head_width': '',
                        'blank_tail_width': '',
                        'hot_rolled_product': '',
                        'steel_grade': '',
                        'width_neg_tolerance': '',
                        'width_pos_tolerance': '',
                        'reject_count': '',
                        'original_roll_width': ''
                    }
                return data
            except Exception as e:
                print(f"提取钢卷数据失败: {str(e)}")
                import traceback
                traceback.print_exc()
                return None
        
        def refresh_data():
            """刷新数据"""
            try:
                print("开始刷新数据...")
                # 清空表格
                table.setRowCount(0)
                
                # 整数字段和文本字段处理
                整数字段显示列表 = ["坯厚", "坯宽", "坯长", "中厚", "轧宽", "订宽", "调宽", "减宽", "RT2", "强度", "坯头部宽", "坯尾部宽", "原轧宽", "负公差", "正公差", "回炉坯"]
                文本字段显示列表 = ["去向"]
                
                # 加载装炉数据
                furnace_data = load_furnace_data()
                print(f"处理 {len(furnace_data)} 条装炉数据")
                
                if not furnace_data:
                    print("没有装炉数据可处理")
                    block_count_label.setText("没有装炉数据可处理")
                    return
                
                # 处理每条数据
                processed_count = 0
                for item in furnace_data:
                    order = item['order']
                    plan_no = item['plan_no']
                    coil_no = item['coil_no']
                    
                    print(f"处理: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no}")
                    
                    # 获取计划号文件
                    plan_file = get_plan_file(plan_no)
                    if plan_file:
                        # 提取钢卷数据
                        coil_data = extract_coil_data(plan_file, coil_no)
                        if coil_data:
                            # 构建表格数据（按照用户要求的列顺序：计划号 钢卷号 牌号（钢级）坯宽 减宽 调宽 轧宽 公差带 粗轧报信 除鳞 坯厚 坯长 轧厚 中厚  RT2 强度  切边 去向  订宽 坯头部宽 坯尾部宽 热轧产品分类 炼钢钢种 负公差 正公差 回炉坯 原轧宽）
                            brand = coil_data.get('牌号（钢级）', coil_data.get('牌号', coil_data.get('钢级', '')))
                            scaling = coil_data.get('除鳞', '')
                            
                            row_data = [
                                plan_no,
                                coil_no,
                                brand,  # 牌号（钢级）
                                coil_data.get('坯宽', ''),      # 坯宽
                                coil_data.get('减宽', ''),     # 减宽
                                coil_data.get('调宽', ''),     # 调宽
                                coil_data.get('轧宽', coil_data.get('轧宽（+余量）', '')),       # 轧宽
                                coil_data.get('公差带', ''),        # 公差带
                                coil_data.get('粗轧报信', ''),    # 粗轧报信
                                scaling,          # 除鳞
                                coil_data.get('坯厚', ''),      # 坯厚
                                coil_data.get('坯长', ''),     # 坯长
                                coil_data.get('轧厚', ''),       # 轧厚
                                coil_data.get('中厚', ''),     # 中厚
                                coil_data.get('RT2', ''),              # RT2
                                coil_data.get('强度', ''),         # 强度
                                coil_data.get('切边', ''),         # 切边
                                coil_data.get('去向', ''),      # 去向
                                coil_data.get('订宽', ''),      # 订宽
                                coil_data.get('坯头部宽', ''),  # 坯头部宽
                                coil_data.get('坯尾部宽', ''),  # 坯尾部宽
                                coil_data.get('热轧产品分类', coil_data.get('产品分类', '')), # 热轧产品分类
                                coil_data.get('炼钢钢种', coil_data.get('炼钢', '')),      # 炼钢钢种
                                coil_data.get('负公差', coil_data.get('width_neg_tolerance', '')), # 负公差
                                coil_data.get('正公差', coil_data.get('width_pos_tolerance', '')), # 正公差
                                coil_data.get('回炉坯', coil_data.get('回炉', coil_data.get('reject_count', ''))),     # 回炉坯
                                coil_data.get('原轧宽', coil_data.get('original_roll_width', '')) # 原轧宽
                            ]
                        else:
                            # 如果没有找到钢卷数据，创建一个空数据行
                            row_data = [
                                plan_no,
                                coil_no,
                                '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                            ]
                    else:
                        # 如果没有找到计划号文件，创建一个空数据行
                        row_data = [
                            plan_no,
                            coil_no,
                            '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                        ]
                    
                    # 数据类型转换
                    for i, col_name in enumerate(columns):
                        if col_name in 整数字段显示列表:
                            # 整数字段：自动转换为整数显示
                            try:
                                value = row_data[i]
                                if isinstance(value, float) and value.is_integer():
                                    row_data[i] = int(value)
                                elif isinstance(value, str):
                                    # 尝试将字符串转换为数字
                                    try:
                                        num_value = float(value)
                                        if num_value.is_integer():
                                            row_data[i] = int(num_value)
                                        else:
                                            row_data[i] = num_value
                                    except:
                                        pass
                            except:
                                pass
                        elif col_name in 文本字段显示列表:
                            # 文本字段：确保显示为文本，去除小数点
                            try:
                                value = row_data[i]
                                if isinstance(value, float):
                                    row_data[i] = str(int(value)) if value.is_integer() else str(value)
                            except:
                                pass
                    
                    # 对粗轧报信字段应用自动换行（索引9）
                    if len(row_data) > 9:
                        rough_rolling_text = str(row_data[9])
                        if rough_rolling_text:
                            row_data[9] = wrap_text(rough_rolling_text, 18)
                    
                    # 插入数据
                    row_position = table.rowCount()
                    table.insertRow(row_position)
                    
                    for i, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        
                        # 检查是否有标识（三角符号Δ或星号*）
                        if isinstance(value, str) and ('Δ' in value or '*' in value):
                            # 设置红色背景
                            item.setBackground(QBrush(QColor('#FF0000')))
                            # 添加annotation属性，用于样式表识别
                            item.setData(Qt.UserRole, True)
                        # 除鳞字段中包含"回"和"无APS"的单元格也改背景色为红色
                        elif i == 9 and isinstance(value, str) and ('回' in value or '无APS' in value):
                            # 设置红色背景
                            item.setBackground(QBrush(QColor('#FF0000')))
                            # 添加annotation属性，用于样式表识别
                            item.setData(Qt.UserRole, True)
                        
                        # 设置对齐方式
                        if i == 8:  # 粗轧报信在第9列（索引8）
                            item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                        else:
                            item.setTextAlignment(Qt.AlignCenter)  # 水平和垂直居中
                        
                        table.setItem(row_position, i, item)
                    
                    # 自动调整行高
                    table.resizeRowToContents(row_position)
                    # 增加行高10
                    current_height = table.rowHeight(row_position)
                    table.setRowHeight(row_position, current_height + 10)
                    
                    print(f"已插入表格数据: {row_data}")
                    processed_count += 1
                
                print(f"刷新数据完成，成功处理 {processed_count} 条数据")
                
                # 更新状态显示
                block_count_label.setText(f"一共 {processed_count} 块")
            except Exception as e:
                print(f"刷新数据失败: {str(e)}")
                import traceback
                traceback.print_exc()
                block_count_label.setText(f"加载失败: {str(e)}")
            
        def show_selected_plan():
            """显示选中的计划号文件"""
            selected_items = table.selectedItems()
            if not selected_items:
                self.custom_messagebox("提示", "请先在表格中选择一行数据")
                return
            
            # 获取选中行的数据
            row = selected_items[0].row()
            plan_no = table.item(row, 1).text()  # 计划号在第二列
            
            # 获取计划号文件
            plan_file = get_plan_file(plan_no)
            if plan_file:
                try:
                    import os
                    os.startfile(plan_file)
                    print(f"已打开文件: {plan_file}")
                except Exception as e:
                    print(f"打开文件失败: {str(e)}")
                    self.custom_messagebox("错误", f"打开文件失败: {str(e)}")
            else:
                self.custom_messagebox("错误", f"找不到计划号文件: {plan_no}.xls")
        
        def print_furnace_details():
            """打印装炉明细"""
            try:
                import tempfile
                import os
                import xlwt
                
                # 获取所有数据
                rows = []
                for row_idx in range(table.rowCount()):
                    row_data = []
                    for col_idx in range(table.columnCount()):
                        item = table.item(row_idx, col_idx)
                        if item:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    rows.append(row_data)
                
                if not rows:
                    self.custom_messagebox("提示", "没有数据可打印")
                    return
                
                # 创建临时Excel文件（存储在计划号文件夹中）
                plan_dir = os.path.join(self.plan_dir, "计划号")
                temp_file_name = f"temp_装炉明细_{int(time.time())}.xls"
                temp_file_path = os.path.join(plan_dir, temp_file_name)
                
                # 创建工作簿和工作表
                workbook = xlwt.Workbook(encoding='utf-8')
                sheet = workbook.add_sheet('装炉明细')
                
                # 设置列名（按照用户要求的顺序）
                headers = [
                    "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                    "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
                    "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
                ]
                
                # 写入列名
                for col, header in enumerate(headers):
                    sheet.write(0, col, header)
                
                # 写入数据
                for row_idx, row_data in enumerate(rows, 1):
                    for col_idx, value in enumerate(row_data):
                        if col_idx < len(headers):
                            sheet.write(row_idx, col_idx, value)
                
                # 保存文件
                workbook.save(temp_file_path)
                
                # 打印文件
                os.startfile(temp_file_path, 'print')
                print(f"已打印装炉明细: {temp_file_path}")
                
            except Exception as e:
                print(f"打印失败: {str(e)}")
                self.custom_messagebox("错误", f"打印失败: {str(e)}")
        
        # 绑定按钮事件
        refresh_btn.clicked.connect(refresh_data)
        show_btn.clicked.connect(show_selected_plan)
        print_btn.clicked.connect(print_furnace_details)
        return_btn.clicked.connect(detail_window.close)
        
        # 显示窗口
        detail_window.show()
        
        # 初始加载数据
        refresh_data()
        
        # 运行事件循环
        app.exec_()
    
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
                    has_low_roll_width = self.run_excel_macro_with_pandas(file_path)
                    processed_count += 1
                    success_files.append(plan_no)
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    
                    # 更新plan_data中的has_low_roll_width字段
                    for i, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[i]['has_low_roll_width'] = has_low_roll_width
                            break
                    
                    # 实时刷新列表显示
                    self.update_listbox()
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_count > 0:
                self.save_processed_plans()
                # 列表框已经在处理每个计划时实时刷新，不需要再次刷新
                # self.update_listbox()
            
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
                # print_selected方法内部会调用load_data，load_data会刷新列表状态
                self.print_selected()
                # 打印完成后，print_selected已经刷新了列表状态，不需要重复刷新
            else:
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
                
                # 自动关闭提示
                auto_close_label = tk.Label(
                    main_frame,
                    text="此窗口将在5秒后自动关闭...",
                    font=('宋体', 12),
                    bg='#f0f0f0',
                    fg='gray'
                )
                auto_close_label.pack(pady=5)
                
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
                # 设置"确定"按钮为默认焦点
                ok_btn.focus_set()
                # 绑定回车键到"确定"按钮
                result_window.bind('<Return>', lambda event: result_window.destroy())
                
                # 5秒后自动关闭窗口
                result_window.after(5000, result_window.destroy)
            
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
                    # 只有xlrd的Workbook对象才有release_resources方法
                    if hasattr(workbook3, 'release_resources'):
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
        
        # 3. 定义目标列（按照用户要求的新顺序，把装炉顺调整到原轧宽后面）
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
            "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
            "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式",
            # 保留其他字段但不显示
            "板坯头部宽度", "板坯尾部宽度", "计划号", "热轧产品分类",
            "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽", "装炉顺序号"
        ]
        
        # 定义字段名映射（按照用户要求的新顺序显示名称）
        字段名映射 = {
            "顺序号": "序号",
            "钢卷号": "钢卷号",
            "牌号（钢级）": "牌号（钢级）",
            "坯宽": "坯宽",
            "侧压量": "减宽",
            "板坯宽度调宽标记": "调宽",
            "轧宽+（余量）": "轧宽",
            "碳": "公差带",
            "粗轧报信": "粗轧报信",
            "层号": "除鳞",
            "坯厚": "坯厚",
            "坯长": "坯长",
            "轧厚": "轧厚",
            "中间坯厚度设定值": "中厚",
            "RT2目标值": "RT2",
            "硬度组": "强度",
            "轧宽": "原轧宽",
            "装炉顺序号": "装炉顺",
            "板坯头部宽度": "坯头部宽",
            "板坯尾部宽度": "坯尾部宽",
            "计划号": "计划号",
            "热轧产品分类": "热轧产品分类",
            "炼钢钢种": "炼钢钢种",
            "宽度负公差": "负公差",
            "宽度正公差": "正公差",
            "板坯炉后拒收次数": "回炉坯"
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
        alignment_header_info.wrap = True  # 启用自动换行
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
        font_time.height = 200  # 10pt
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
        
        # 12pt 长间隔虚线边框样式（用于除鳞、公差带）
    
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
                    has_low_roll_width = self.run_excel_macro_with_pandas(file_path)
                    processed_count += 1
                    success_files.append(plan_no)
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    
                    # 更新plan_data中的has_low_roll_width字段
                    for i, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[i]['has_low_roll_width'] = has_low_roll_width
                            break
                    
                    # 实时刷新列表显示
                    self.update_listbox()
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_count > 0:
                self.save_processed_plans()
                # 列表框已经在处理每个计划时实时刷新，不需要再次刷新
                # self.update_listbox()
            
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
                # print_selected方法内部会调用load_data，load_data会刷新列表状态
                self.print_selected()
                # 打印完成后，print_selected已经刷新了列表状态，不需要重复刷新
            else:
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
                
                # 自动关闭提示
                auto_close_label = tk.Label(
                    main_frame,
                    text="此窗口将在5秒后自动关闭...",
                    font=('宋体', 12),
                    bg='#f0f0f0',
                    fg='gray'
                )
                auto_close_label.pack(pady=5)
                
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
                # 设置"确定"按钮为默认焦点
                ok_btn.focus_set()
                # 绑定回车键到"确定"按钮
                result_window.bind('<Return>', lambda event: result_window.destroy())
                
                # 5秒后自动关闭窗口
                result_window.after(5000, result_window.destroy)
            
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
                    # 只有xlrd的Workbook对象才有release_resources方法
                    if hasattr(workbook3, 'release_resources'):
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
        
        # 3. 定义目标列（按照用户要求的新顺序，把装炉顺调整到原轧宽后面）
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
            "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
            "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式",
            # 保留其他字段但不显示
            "板坯头部宽度", "板坯尾部宽度", "计划号", "热轧产品分类",
            "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽", "装炉顺序号"
        ]
        
        # 定义字段名映射（按照用户要求的新顺序显示名称）
        字段名映射 = {
            "顺序号": "序号",
            "钢卷号": "钢卷号",
            "牌号（钢级）": "牌号（钢级）",
            "坯宽": "坯宽",
            "侧压量": "减宽",
            "板坯宽度调宽标记": "调宽",
            "轧宽+（余量）": "轧宽",
            "碳": "公差带",
            "粗轧报信": "粗轧报信",
            "层号": "除鳞",
            "坯厚": "坯厚",
            "坯长": "坯长",
            "轧厚": "轧厚",
            "中间坯厚度设定值": "中厚",
            "RT2目标值": "RT2",
            "硬度组": "强度",
            "轧宽": "原轧宽",
            "装炉顺序号": "装炉顺",
            "板坯头部宽度": "坯头部宽",
            "板坯尾部宽度": "坯尾部宽",
            "计划号": "计划号",
            "热轧产品分类": "热轧产品分类",
            "炼钢钢种": "炼钢钢种",
            "宽度负公差": "负公差",
            "宽度正公差": "正公差",
            "板坯炉后拒收次数": "回炉坯"
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
        alignment_header_info.wrap = True  # 启用自动换行
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
        font_time.height = 200  # 10pt
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
        
        # 12pt 长间隔虚线边框样式（用于除鳞、公差带）
        style_data_12pt_dashed = xlwt.XFStyle()
        font_data_12pt_dashed = xlwt.Font()
        font_data_12pt_dashed.name = '仿宋'
        font_data_12pt_dashed.height = 240  # 12pt
        font_data_12pt_dashed.bold = True
        style_data_12pt_dashed.font = font_data_12pt_dashed
        style_data_12pt_dashed.alignment = alignment_data_12pt
        borders_data_12pt_dashed = xlwt.Borders()
        borders_data_12pt_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashed.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashed.top = xlwt.Borders.THIN
        borders_data_12pt_dashed.bottom = xlwt.Borders.THIN
        style_data_12pt_dashed.borders = borders_data_12pt_dashed
        
        # 12pt 长间隔虚线边框样式（用于轧厚）
        style_data_12pt_dashdot = xlwt.XFStyle()
        font_data_12pt_dashdot = xlwt.Font()
        font_data_12pt_dashdot.name = '仿宋'
        font_data_12pt_dashdot.height = 240  # 12pt
        font_data_12pt_dashdot.bold = True
        style_data_12pt_dashdot.font = font_data_12pt_dashdot
        style_data_12pt_dashdot.alignment = alignment_data_12pt
        borders_data_12pt_dashdot = xlwt.Borders()
        borders_data_12pt_dashdot.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashdot.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_dashdot.top = xlwt.Borders.THIN
        borders_data_12pt_dashdot.bottom = xlwt.Borders.THIN
        style_data_12pt_dashdot.borders = borders_data_12pt_dashdot
        
        # 12pt 左侧长间隔虚线边框样式（用于坯宽）
        style_data_12pt_left_dashdot = xlwt.XFStyle()
        font_data_12pt_left_dashdot = xlwt.Font()
        font_data_12pt_left_dashdot.name = '仿宋'
        font_data_12pt_left_dashdot.height = 240  # 12pt
        font_data_12pt_left_dashdot.bold = True
        style_data_12pt_left_dashdot.font = font_data_12pt_left_dashdot
        style_data_12pt_left_dashdot.alignment = alignment_data_12pt
        borders_data_12pt_left_dashdot = xlwt.Borders()
        borders_data_12pt_left_dashdot.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_left_dashdot.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left_dashdot.top = xlwt.Borders.THIN
        borders_data_12pt_left_dashdot.bottom = xlwt.Borders.THIN
        style_data_12pt_left_dashdot.borders = borders_data_12pt_left_dashdot
        
        # 14pt 实线边框样式（用于轧宽）- 去掉左边线
        style_data_14pt_dashed = xlwt.XFStyle()
        font_data_14pt_dashed = xlwt.Font()
        font_data_14pt_dashed.name = '仿宋'
        font_data_14pt_dashed.height = 280  # 14pt
        font_data_14pt_dashed.bold = True
        style_data_14pt_dashed.font = font_data_14pt_dashed
        style_data_14pt_dashed.alignment = alignment_data_14pt
        borders_data_14pt_dashed = xlwt.Borders()
        borders_data_14pt_dashed.left = xlwt.Borders.NO_LINE  # 去掉左边线
        borders_data_14pt_dashed.right = xlwt.Borders.THIN
        borders_data_14pt_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_dashed.borders = borders_data_14pt_dashed
        
        # 14pt 长间隔虚线边框样式（用于减宽）
        style_data_14pt_long_dashed = xlwt.XFStyle()
        font_data_14pt_long_dashed = xlwt.Font()
        font_data_14pt_long_dashed.name = '仿宋'
        font_data_14pt_long_dashed.height = 280  # 14pt
        font_data_14pt_long_dashed.bold = True
        style_data_14pt_long_dashed.font = font_data_14pt_long_dashed
        style_data_14pt_long_dashed.alignment = alignment_data_14pt
        borders_data_14pt_long_dashed = xlwt.Borders()
        borders_data_14pt_long_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_long_dashed.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_long_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_long_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_long_dashed.borders = borders_data_14pt_long_dashed
        
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
        
        # 14pt 双横线+长间隔虚线样式（用于减宽超标）
        style_data_14pt_double = xlwt.XFStyle()
        font_data_14pt_double = xlwt.Font()
        font_data_14pt_double.name = '仿宋'
        font_data_14pt_double.height = 280  # 14pt
        font_data_14pt_double.bold = True
        style_data_14pt_double.font = font_data_14pt_double
        style_data_14pt_double.alignment = alignment_data_14pt
        borders_data_14pt_double = xlwt.Borders()
        borders_data_14pt_double.left = xlwt.Borders.MEDIUM_DASHED  # 长间隔虚线
        borders_data_14pt_double.right = xlwt.Borders.MEDIUM_DASHED  # 长间隔虚线
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
        
        for row_idx in range(1, sheet.nrows):
            if "计划号" in current_columns:
                计划号值 = sheet.cell_value(row_idx, current_columns.index("计划号"))
                if 计划号值:
                    计划号 = str(计划号值)
                    break
        
        # 获取当前时间
        from datetime import datetime
        当前时间 = datetime.now().strftime("%Y/%m/%d %H:%M")
        
        # 找到"强度"列的索引
        强度列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "强度":
                强度列索引 = col_idx
                break
        
        # 找到"装炉顺"列的索引
        装炉顺列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
                break
        
        # 如果找到强度列，标题只跨列到该列；否则跨所有列
        if 强度列索引 >= 0:
            标题结束列 = 强度列索引
        else:
            标题结束列 = len(target_columns) - 1
        
        # 8. 设置列宽（根据新的字段顺序）
        # 新顺序：序号、钢卷号、牌号（钢级）、坯宽、减宽、调宽、轧宽、公差带、粗轧报信、除鳞、坯厚、坯长、轧厚、中厚、RT2、强度、原轧宽、装炉顺、订宽、去向、切边
        col_widths = [
            int(4.3 * 256 * 1.2),       # 1. 序号
            int(20 * 256 * 1.04),       # 2. 钢卷号
            int(18 * 256 * 1.04),       # 3. 牌号（钢级）
            int(7 * 256 * 1.04),         # 4. 坯宽
            int(7 * 256 * 1.05),         # 5. 减宽（侧压量）
            int(5.6 * 256 * 1.04),       # 6. 调宽（板坯宽度调宽标记）
            int(7 * 256 * 1.13),         # 7. 轧宽（轧宽+（余量））
            int(9 * 256 * 1.03),         # 8. 公差带（碳）
            int(33 * 256 * 1.04),        # 9. 粗轧报信
            int(7 * 256 * 1.08),         # 10. 除鳞（层号）
            int(7 * 256 * 1.04),         # 11. 坯厚
            int(6.2 * 256 * 1.13),       # 12. 坯长
            int(6 * 256 * 1.04),         # 13. 轧厚
            int(5 * 256 * 1.04),         # 14. 中厚（中间坯厚度设定值）
            int(6.57 * 256 * 1.04),      # 15. RT2（RT2目标值）
            int(4.5 * 256 * 1.2),        # 16. 强度（硬度组）
            int(8.0 * 256 * 1.04),       # 17. 原轧宽（轧宽）
            int(7 * 256 * 1.1),        # 18. 装炉顺（装炉顺序号）
            int(5 * 256 * 1.17),         # 19. 订宽（订货宽度）
            int(3.6 * 256 * 1.2),        # 20. 去向
            int(3.6 * 256 * 1.2),        # 21. 切边（切边方式）
            # 保留的其他字段
            int(8.0 * 256 * 1.04),       # 坯头部宽（板坯头部宽度）
            int(8.0 * 256 * 1.04),       # 坯尾部宽（板坯尾部宽度）
            int(8.0 * 256 * 1.04),       # 计划号
            int(8.0 * 256 * 1.04),       # 热轧产品分类
            int(8.0 * 256 * 1.04),       # 炼钢钢种
            int(8.0 * 256 * 1.04),       # 负公差（宽度负公差）
            int(8.0 * 256 * 1.04),       # 正公差（宽度正公差）
            int(8.0 * 256 * 1.04)        # 回炉坯（板坯炉后拒收次数）
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
        调宽问题列表 = []
        
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
            
            # 3. 填充去向字段 - 参考VBA代码中的转换逻辑
            if "去向" in target_columns and "去向" in row_data:
                去向值 = str(row_data.get("去向", "")).strip()
                
                # 根据VBA代码进行转换
                if 去向值 in ["41", "42", "43", "49"]:
                    row_data["去向"] = "B"
                elif 去向值 in ["51", "52", "58", "59"]:
                    row_data["去向"] = "A"
                elif 去向值 in ["1A", "1B", "1C", "2A", "2B", "2C", "3A", "3B", "3C", "4A", "4B"]:
                    row_data["去向"] = "C"
                elif 去向值 == "C1":
                    row_data["去向"] = "E"
                elif 去向值 == "C3":
                    row_data["去向"] = "J"
                elif 去向值 == "C2":
                    row_data["去向"] = "H"
            
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
            是无APS钢种 = False
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无APS块数 += 1
                    row_data["需标注"] = True
                    是无APS钢种 = True
                    包含无APS = True
                    if brand not in 已添加无APS的钢种:
                        已添加无APS的钢种.add(brand)
                        无APS钢种数 += 1
            # 存储无APS钢种标志到row_data中
            row_data["是无APS钢种"] = 是无APS钢种
            
            # 处理调宽字段 - 如果调宽不为"0"，则进行特殊处理
            if "板坯宽度调宽标记" in row_data and str(row_data.get("板坯宽度调宽标记", "")).strip() != "0":
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
                    
                    # 判断头部宽度和尾部宽度中小者<=轧宽，则标注调宽三角符号
                    if "轧宽" in row_data:
                        轧宽值 = row_data.get("轧宽", 0)
                        try:
                            轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                            # 计算头部宽度和尾部宽度的较小值
                            宽度较小值 = min(板坯头部宽度值, 板坯尾部宽度值)
                            if 宽度较小值 <= 轧宽值:
                                # 标注调宽三角符号
                                row_data["板坯宽度调宽标记"] = str(调宽差值) + "Δ"
                                row_data["需标注"] = True
                                # 记录调宽问题信息，用于提示行显示
                                if "钢卷号" in row_data:
                                    钢卷号 = row_data.get("钢卷号", "")
                                    调宽问题信息 = f"{钢卷号}-{宽度较小值}"
                                    调宽问题列表.append(调宽问题信息)
                        except (ValueError, TypeError):
                            pass
            
            # 只有在调宽为"0"时，才检查"侧压量"字段
            if "板坯宽度调宽标记" not in row_data or str(row_data.get("板坯宽度调宽标记", "")).strip() == "0":
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
            
            # 比较轧宽+（余量）和轧宽，如果轧宽+（余量）大于轧宽，修改负公差和正公差
            if "轧宽+（余量）" in row_data and "轧宽" in row_data:
                轧宽余量值 = row_data.get("轧宽+（余量）", 0)
                轧宽值 = row_data.get("轧宽", 0)
                try:
                    轧宽余量值 = float(轧宽余量值) if 轧宽余量值 != "" else 0
                    轧宽值 = float(轧宽值) if 轧宽值 != "" else 0
                    if 轧宽余量值 > 轧宽值:
                        差值 = int(轧宽余量值 - 轧宽值)
                        负公差原始值 = row_data.get("宽度负公差", 0)
                        正公差原始值 = row_data.get("宽度正公差", 0)
                        try:
                            负公差原始值 = float(负公差原始值) if 负公差原始值 != "" else 0
                            正公差原始值 = float(正公差原始值) if 正公差原始值 != "" else 0
                            row_data["宽度负公差"] = int(负公差原始值 - 差值)
                            row_data["宽度正公差"] = int(正公差原始值 - 差值)
                        except (ValueError, TypeError):
                            pass
                except (ValueError, TypeError):
                    pass
            
            # 检查轧宽+（余量）是否<=930，如果是则添加标记
            if "轧宽+（余量）" in row_data:
                轧宽余量值 = row_data.get("轧宽+（余量）", "")
                try:
                    轧宽余量数值 = float(轧宽余量值) if 轧宽余量值 != "" else 0
                    if 轧宽余量数值 <= 930:
                        row_data["轧宽+（余量）"] = str(int(轧宽余量数值)) + "Δ"
                        row_data["低轧宽标记"] = True
                        row_data["需标注"] = True
                        低轧宽板坯数 += 1
                        if 轧宽余量数值 < 720:
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
            
            # 处理切边字段 - 如果为M0则改成"直发"
            if "切边方式" in row_data:
                切边值 = str(row_data.get("切边方式", "")).strip()
                if 切边值 == "M0":
                    row_data["切边方式"] = "直发"
            
            # 将处理后的数据添加到列表
            all_row_data.append(row_data)
        
        # 9. 写入表头
        # 第一行：大标题"轧制计划明细表"
        new_sheet.write_merge(0, 0, 0, 标题结束列, "轧制计划明细表", style_title)
        
        # 准备提示信息列表
        提示信息列表 = []
        序号 = 1
        
        if 无APS钢种数 > 0:
            提示信息列表.append(f"{序号}.无APS钢种{无APS钢种数}个{无APS块数}块")
            序号 += 1
        if 减宽超标块数 > 0:
            提示信息列表.append(f"{序号}.减宽量超标{减宽超标块数}块")
            序号 += 1
        if 逆宽轧制板坯数 > 0:
            提示信息列表.append(f"{序号}.逆宽轧制板坯{逆宽轧制板坯数}块")
            序号 += 1
        if 低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有轧宽低于930板坯{低轧宽板坯数}块")
            序号 += 1
        if 极低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有低于860的板坯{极低轧宽板坯数}块")
            序号 += 1
        if 调宽问题列表:
            调宽问题信息 = ", ".join(调宽问题列表)
            提示信息列表.append(f"{序号}.调宽问题: {调宽问题信息}")
            序号 += 1
        
        # 计算提示信息行数（先左右再上下，每行显示2条）
        if len(提示信息列表) == 0:
            提示信息行数 = 1  # 至少有一行（空行）
        else:
            提示信息行数 = (len(提示信息列表) + 1) // 2  # 向上取整，每行2条
            # 确保至少有2行来显示3个提示信息
            if len(提示信息列表) >= 3 and 提示信息行数 < 2:
                提示信息行数 = 2
        
        # 计算提示信息总行数（用于后续判断）
        提示信息总行数 = 提示信息行数
        
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
        公差带列索引 = -1
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
            elif 映射后的列名 == "公差带":
                公差带列索引 = col_idx
        
        # 第二行及以下：提示信息、计划号、块数、打印时间
        # 提示信息显示在第2行开始
        # 计划号和块数信息写入到提示信息行的最后一行
        plan_info_row = 1 + 提示信息行数 - 1  # 提示信息的最后一行
        new_sheet.write_merge(plan_info_row, plan_info_row, 序号列索引, 钢卷号列索引, f"计划号：{计划号}", style_header_info)
        
        # 牌号（钢级）列填充块数信息
        if 牌号列索引 >= 0:
            new_sheet.write(plan_info_row, 牌号列索引, f"块数：{块数} 块", style_header_info)
        
        # 更新字段列名行号，确保在计划号和块数信息行的下面
        字段列名行号 = plan_info_row + 1
        
        # 根据用户要求重新设计提示信息显示区域
        # 左区域：坯宽到公差带（显示提示信息）
        # 中间区域：粗轧报信到坯长（显示提示信息）
        # 右区域：中厚到装炉顺（显示打印时间）
        
        # 找到需要的列索引
        坯宽列索引 = -1
        轧厚列索引 = -1
        坯长列索引 = -1
        坯厚列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "坯宽":
                坯宽列索引 = col_idx
            elif 映射后的列名 == "轧厚":
                轧厚列索引 = col_idx
            elif 映射后的列名 == "坯长":
                坯长列索引 = col_idx
            elif 映射后的列名 == "坯厚":
                坯厚列索引 = col_idx
        
        # 计算左区域（坯宽到公差带）
        if 坯宽列索引 >= 0 and 公差带列索引 >= 0:
            左区域起始 = 坯宽列索引
            左区域结束 = 公差带列索引
        else:
            左区域起始 = -1
            左区域结束 = -1
        
        # 计算中间区域（粗轧报信到坯厚）
        if 粗轧报信列索引 >= 0 and 坯厚列索引 >= 0:
            中间区域起始 = 粗轧报信列索引
            中间区域结束 = 坯厚列索引
        else:
            中间区域起始 = -1
            中间区域结束 = -1
        
        # 计算右区域（轧厚到装炉顺）
        if 轧厚列索引 >= 0 and 装炉顺列索引 >= 0:
            右区域起始 = 轧厚列索引
            右区域结束 = 装炉顺列索引
        else:
            右区域起始 = -1
            右区域结束 = -1
        
        # 显示提示信息（多行显示）
        if 左区域起始 >= 0 and 左区域结束 >= 0 and 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 多行显示提示信息，每行2条
            for i in range(提示信息行数):
                # 左列（坯宽到公差带）：显示第 i*2 条提示信息
                左列索引 = i * 2
                if 左列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, 提示信息列表[左列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, "", style_header_info)
                
                # 中间列（粗轧报信到坯长）：显示第 i*2+1 条提示信息
                中间列索引 = i * 2 + 1
                if 中间列索引 < len(提示信息列表):
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, 提示信息列表[中间列索引], style_header_info)
                else:
                    new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, "", style_header_info)
        elif 左区域起始 >= 0 and 左区域结束 >= 0:
            # 如果只有左区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 左区域起始, 左区域结束, 提示信息, style_header_info)
        elif 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 如果只有中间区域
            for i, 提示信息 in enumerate(提示信息列表):
                new_sheet.write_merge(1 + i, 1 + i, 中间区域起始, 中间区域结束, 提示信息, style_header_info)
        
        # 右区域（坯长到强度）显示打印时间
        if 坯长列索引 >= 0 and 强度列索引 >= 0:
            # 打印时间应该与计划号和块数信息在同一行
            new_sheet.write_merge(plan_info_row, plan_info_row, 坯长列索引, 强度列索引, f"打印时间：{当前时间}", style_time)
        
        # 设置提示信息行的行高和自动换行
        # 为每个提示行设置行高
        for i in range(1, 字段列名行号):
            # 设置固定行高23pt
            new_sheet.row(i).height = 460  # 23pt
            new_sheet.row(i).height_mismatch = True
        
        # 字段列名（使用内外边框线样式）
        粗轧报信字段名 = ""
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            new_sheet.write(字段列名行号, col_idx, 映射后的列名, style_header_border)
            # 记录粗轧报信字段名用于计算行高
            if 映射后的列名 == "粗轧报信":
                粗轧报信字段名 = 映射后的列名
        
        # 设置字段列名行的行高（25pt = 500 twips）
        new_sheet.row(字段列名行号).height = 500
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
                    # 减宽使用14pt长间隔虚线样式
                    # 检查减宽值是否>=240或<0，如果是，则使用双横线样式
                    减宽超标 = row_data.get("减宽超标", False)
                    是无APS钢种 = row_data.get("是无APS钢种", False)
                    # 减宽字段不要小数点，转为整数
                    try:
                        if value:
                            减宽数值 = float(value)
                            value = str(int(减宽数值))
                    except (ValueError, TypeError):
                        pass
                    # 只有在减宽超标的情况下才标注减宽字段
                    if 减宽超标:
                        value = str(value) + "Δ"
                        new_sheet.write(new_row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(new_row_idx, col_idx, value, style_data_14pt_long_dashed)
                elif 映射后的列名 == "除鳞" or 映射后的列名 == "公差带":
                    # 除鳞和公差带使用12pt虚线边框样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_dashed)
                elif 映射后的列名 == "牌号（钢级）":
                    # 牌号（钢级）使用12pt左对齐样式
                    # 检查是否是无APS钢种，如果是则标注
                    是无APS钢种 = row_data.get("是无APS钢种", False)
                    需标注 = row_data.get("需标注", False)
                    if 需标注 and 是无APS钢种:
                        value = str(value) + "Δ"
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_left)
                elif 映射后的列名 == "轧厚":
                    # 轧厚使用12pt点划线边框样式，并保留小数点后1位（不四舍五入）
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
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_dashdot)
                elif 映射后的列名 == "去向" or 映射后的列名 == "坯长" or 映射后的列名 == "中厚":
                    # 这些字段使用12pt样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt)
                elif 映射后的列名 == "坯厚":
                    # 坯厚使用14pt样式
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
                    new_sheet.write(new_row_idx, col_idx, value, style_data_14pt)
                elif 映射后的列名 == "坯宽":
                    # 坯宽使用14pt样式，左右都添加虚线边框
                    # 创建坯宽专用样式
                    style_坯宽 = xlwt.XFStyle()
                    font_坯宽 = xlwt.Font()
                    font_坯宽.name = '仿宋'
                    font_坯宽.height = 280  # 14pt
                    font_坯宽.bold = True
                    style_坯宽.font = font_坯宽
                    alignment_坯宽 = xlwt.Alignment()
                    alignment_坯宽.horz = xlwt.Alignment.HORZ_CENTER
                    alignment_坯宽.vert = xlwt.Alignment.VERT_CENTER
                    style_坯宽.alignment = alignment_坯宽
                    borders_坯宽 = xlwt.Borders()
                    borders_坯宽.left = xlwt.Borders.MEDIUM_DASHED  # 左边添加长间隔虚线
                    borders_坯宽.right = xlwt.Borders.MEDIUM_DASHED  # 右边保持长间隔虚线
                    borders_坯宽.top = xlwt.Borders.THIN
                    borders_坯宽.bottom = xlwt.Borders.THIN
                    style_坯宽.borders = borders_坯宽
                    new_sheet.write(new_row_idx, col_idx, value, style_坯宽)
                elif 映射后的列名 == "RT2":
                    # RT2使用14pt样式
                    new_sheet.write(new_row_idx, col_idx, value, style_data_14pt)
                elif 映射后的列名 == "轧厚":
                    # 轧厚使用14pt样式，并保留小数点后1位（不四舍五入）
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
                    new_sheet.write(new_row_idx, col_idx, value, style_data_14pt)
                elif 映射后的列名 == "钢卷号":
                    # 钢卷号使用16pt左对齐样式
                    # 检查是否需要标注（添加三角符号）
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    # 第一列左侧需要实线边框
                    if is_first_column:
                        # 创建16pt左对齐带左边框样式
                        style_steel_coil_16pt_left = xlwt.XFStyle()
                        font_steel_coil = xlwt.Font()
                        font_steel_coil.name = '仿宋'
                        font_steel_coil.height = 320  # 16pt
                        font_steel_coil.bold = True
                        style_steel_coil_16pt_left.font = font_steel_coil
                        alignment_steel_coil = xlwt.Alignment()
                        alignment_steel_coil.horz = xlwt.Alignment.HORZ_LEFT
                        alignment_steel_coil.vert = xlwt.Alignment.VERT_CENTER
                        style_steel_coil_16pt_left.alignment = alignment_steel_coil
                        borders_steel_coil = xlwt.Borders()
                        borders_steel_coil.left = xlwt.Borders.THIN
                        borders_steel_coil.right = xlwt.Borders.NO_LINE
                        borders_steel_coil.top = xlwt.Borders.THIN
                        borders_steel_coil.bottom = xlwt.Borders.THIN
                        style_steel_coil_16pt_left.borders = borders_steel_coil
                        new_sheet.write(new_row_idx, col_idx, value, style_steel_coil_16pt_left)
                    else:
                        # 创建16pt左对齐样式
                        style_steel_coil_16pt_left = xlwt.XFStyle()
                        font_steel_coil = xlwt.Font()
                        font_steel_coil.name = '仿宋'
                        font_steel_coil.height = 320  # 16pt
                        font_steel_coil.bold = True
                        style_steel_coil_16pt_left.font = font_steel_coil
                        alignment_steel_coil = xlwt.Alignment()
                        alignment_steel_coil.horz = xlwt.Alignment.HORZ_LEFT
                        alignment_steel_coil.vert = xlwt.Alignment.VERT_CENTER
                        style_steel_coil_16pt_left.alignment = alignment_steel_coil
                        borders_steel_coil = xlwt.Borders()
                        borders_steel_coil.left = xlwt.Borders.NO_LINE
                        borders_steel_coil.right = xlwt.Borders.NO_LINE
                        borders_steel_coil.top = xlwt.Borders.THIN
                        borders_steel_coil.bottom = xlwt.Borders.THIN
                        style_steel_coil_16pt_left.borders = borders_steel_coil
                        new_sheet.write(new_row_idx, col_idx, value, style_steel_coil_16pt_left)
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
                    # 强度列右侧需要实线边框
                    new_sheet.write(new_row_idx, col_idx, value, style_data_12pt_right_border)
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
            
            # 设置数据行行高（最低25pt = 500 twips，根据内容自动计算）
            # 检查粗轧报信字段内容长度，如果内容较长需要增加行高
            粗轧报信列索引 = -1
            for col_idx, col_name in enumerate(target_columns):
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "粗轧报信":
                    粗轧报信列索引 = col_idx
                    break
            
            # 根据内容长度计算行高（至少25pt = 500 twips）
            if 粗轧报信列索引 >= 0:
                粗轧报信值 = row_data.get("粗轧报信", "")
                if 粗轧报信值:
                    内容 = str(粗轧报信值)
                    # 按实际显示规则计算行数：每行约13个字符（考虑中英文混合）
                    # 英文和数字占宽度较少，中文占宽度较多
                    def 计算显示宽度(文本):
                        宽度 = 0
                        for 字符 in 文本:
                            if 字符.isascii():
                                宽度 += 0.6  # 英文字符和数字占0.6个中文宽度
                            else:
                                宽度 += 1  # 中文字符占1个宽度
                        return 宽度
                    
                    总宽度 = 计算显示宽度(内容)
                    每行宽度 = 13  # 每行约13个中文宽度（根据实际Excel显示调整）
                    # 计算需要的行数
                    需要行数 = max(1, int((总宽度 + 每行宽度 - 1) // 每行宽度))
                    # 增加安全系数：只有内容较长时才增加1行，短内容不增加
                    # 判断标准：如果最后一行接近满行（超过80%宽度），则增加1行
                    最后一行宽度 = 总宽度 % 每行宽度
                    if 最后一行宽度 == 0:
                        最后一行宽度 = 每行宽度
                    if 最后一行宽度 > 每行宽度 * 0.8:
                        需要行数 = 需要行数 + 1
                    # 行高计算：基础行高25pt(500 twips)，多行时每行增加18pt(360 twips)
                    # 1行=25pt, 2行=25+18=43pt, 3行=25+18+18=61pt, 以此类推
                    基础行高 = 500  # 25pt
                    每增加行高 = 360  # 18pt
                    # 计算总行高（至少25pt）
                    计算行高 = 基础行高 + (需要行数 - 1) * 每增加行高
                    # 设置行高（根据内容动态调整，最低25pt）
                    new_sheet.row(new_row_idx).height = 计算行高
                    new_sheet.row(new_row_idx).height_mismatch = True
                else:
                    # 无内容时使用默认行高（25pt = 500 twips）
                    new_sheet.row(new_row_idx).height = 500
                    new_sheet.row(new_row_idx).height_mismatch = True
            else:
                # 其他行使用默认行高（25pt = 500 twips）
                new_sheet.row(new_row_idx).height = 500
                new_sheet.row(new_row_idx).height_mismatch = True
        
        # 11. 保存文件
        # 设置页边距为0（使用inches为单位）
        try:
            new_sheet.left_margin = 0.0
            new_sheet.right_margin = 0.0
            new_sheet.top_margin = 0.0
            new_sheet.bottom_margin = 0.0
            print("[纸张设置] ✓ 页边距设置为0")
        except Exception as e:
            print(f"[纸张设置] ✗ 页边距设置失败: {str(e)}")
        
        # 设置页眉页脚为空（使用bytes类型）
        new_sheet.header_str = b''
        new_sheet.footer_str = b''
        # 设置文档缩放比例为140%
        new_sheet.normal_magn = 140
        
        # 设置列宽
        try:
            # 查找列标题并设置对应列宽
            header_row = 1  # 假设表头在第一行
            column_widths = {
                "订宽": 4.8,
                "坯厚": 4.8,
                "中厚": 4,
                "减宽": 7,
                "粗轧报信": 33
            }
            
            # 获取已用区域
            max_col = sheet.ncols
            
            # 遍历表头查找对应列
            for col in range(sheet.ncols):
                try:
                    cell_value = str(sheet.cell_value(0, col)).strip()
                    if cell_value in column_widths:
                        new_sheet.col(col).width = column_widths[cell_value] * 256  # xlwt的列宽单位是1/256字符宽度
                        print(f"[纸张设置] ✓ 列 '{cell_value}' 宽度设置为 {column_widths[cell_value]}")
                except:
                    continue
            
            print("[纸张设置] ✓ 列宽设置完成")
        except Exception as e:
            print(f"[纸张设置] ✗ 列宽设置失败: {str(e)}")
        
        # 保存文件
        new_workbook.save(file_path)
        print(f"[纸张设置] ✓ 保存文件到: {file_path}")
        
        # 尝试使用pywin32设置纸张大小（如果可用）
        try:
            import win32com.client
            print("[纸张设置] 尝试使用pywin32设置纸张大小...")
            
            # 创建Excel应用程序实例
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False  # 禁用警告
            
            # 打开文件
            workbook = excel.Workbooks.Open(file_path)
            ws = workbook.ActiveSheet
            
            # 强制使用 xlPaperFanfoldUS (137) - 美国连续折叠纸
            preferred_size = 137  # xlPaperFanfoldUS
            
            # 尝试设置首选纸张
            try:
                ws.PageSetup.PaperSize = preferred_size
                print(f"[纸张设置] ✓ 成功设置纸张: FanfoldUS (14.875 x 11 inch)")
            except Exception as e:
                print(f"[纸张设置] ✗ 首选纸张设置失败: {str(e)}")
                # 尝试备选纸张
                fallback_papers = [39, 118, 119, 1, 9]
                for paper_code in fallback_papers:
                    if paper_code == preferred_size:
                        continue
                    try:
                        ws.PageSetup.PaperSize = paper_code
                        print(f"[纸张设置] ✓ 成功设置备选纸张: {paper_code}")
                        break
                    except Exception as e:
                        print(f"[纸张设置] ✗ 备选纸张 {paper_code} 设置失败: {str(e)}")
                        continue
            
            # 保存并关闭
            workbook.Save()
            workbook.Close()
            excel.Quit()
            print("[纸张设置] ✓ pywin32设置完成")
        except ImportError:
            print("[纸张设置] pywin32未安装，跳过纸张大小设置")
        except Exception as e:
            print(f"[纸张设置] pywin32设置失败: {str(e)}")
        
        # 释放资源
        # 只有xlrd的Workbook对象才有release_resources方法
        if hasattr(workbook, 'release_resources'):
            workbook.release_resources()
        
        # 处理无APS标记
        # 将无APS钢种添加到APS.txt文件中
        if 已添加无APS的钢种:
            aps_file_path = os.path.join(self.plan_dir, "APS.txt")
            try:
                # 先读取现有APS钢种列表
                existing_aps_grades = set()
                if os.path.exists(aps_file_path):
                    with open(aps_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                existing_aps_grades.add(line)
                
                # 找出新的无APS钢种
                new_aps_grades = 已添加无APS的钢种 - existing_aps_grades
                
                # 如果有新的钢种，追加到APS.txt文件
                if new_aps_grades:
                    with open(aps_file_path, 'a', encoding='utf-8') as f:
                        for grade in sorted(new_aps_grades):
                            f.write(f"{grade}\n")
                    print(f"已将 {len(new_aps_grades)} 个无APS钢种添加到APS.txt文件")
            except Exception as e:
                print(f"添加无APS钢种到APS.txt文件失败: {str(e)}")
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
        
        # 返回是否检测到轧宽预警
        return 低轧宽板坯数 > 0
    
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
                    has_low_roll_width = self.run_excel_macro_with_pandas(file_path)
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    
                    # 更新plan_data中的has_low_roll_width字段
                    for i, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[i]['has_low_roll_width'] = has_low_roll_width
                            break
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    print(f"✗ 处理失败 {plan_no}.xls: {str(e)}")
                    print(f"详细错误:\n{error_detail}")
                    # 显示详细错误弹窗
                    self.custom_messagebox("错误", f"处理计划 {plan_no} 失败:\n\n{str(e)}\n\n详细错误:\n{error_detail[:500]}...")
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
                    has_low_roll_width = self.run_excel_macro_with_pandas(file_path)
                    update_progress("正在处理计划...", f"已处理: {plan_no}")
                    print(f"✓ 已处理: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    processed_plans.append(plan_no)
                    
                    # 更新plan_data中的has_low_roll_width字段
                    for j, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[j]['has_low_roll_width'] = has_low_roll_width
                            break
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
        
        # 自动关闭提示
        auto_close_label = tk.Label(
            main_frame,
            text="此窗口将在5秒后自动关闭...",
            font=('宋体', 12),
            bg='#f0f0f0',
            fg='gray'
        )
        auto_close_label.pack(pady=5)
        
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
        # 设置"确定"按钮为默认焦点
        ok_btn.focus_set()
        # 绑定回车键到"确定"按钮
        result_window.bind('<Return>', lambda event: result_window.destroy())
        
        # 5秒后自动关闭窗口
        result_window.after(5000, result_window.destroy)
    
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
            
            # 找到强度列的索引
            强度列索引 = -1
            for col_idx, col_name in enumerate(target_columns):
                映射后的列名 = 字段名映射.get(col_name, col_name)
                if 映射后的列名 == "强度":
                    强度列索引 = col_idx
                    break
            
            # 即使找不到强度列，也强制设置打印范围为前16列（根据标准列顺序）
            if 强度列索引 == -1:
                print("未找到强度列，使用默认打印范围：前16列")
                强度列索引 = 15  # 默认第16列（索引15）为强度列
            else:
                print(f"找到强度列，索引: {强度列索引}")
            
            # 计算打印范围：第一列(0)到强度列
            print_col_start = 0
            print_col_end = 强度列索引
            
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
                
                # 设置每页打印表头：首页表头为$1:$n，后续页面表头为$2:$n
                # 计算字段名行号对应的Excel行号（Excel行号从1开始）
                field_name_row = 字段列名行号 + 1  # 转换为Excel行号
                # 设置打印标题行为从第二行到字段名行
                worksheet.PageSetup.PrintTitleRows = f"$2:${field_name_row}"
                
                # 设置打印时间字体大小为10号
                # 查找打印时间所在的单元格
                for row_idx in range(sheet.nrows):
                    for col_idx in range(sheet.ncols):
                        cell_value = str(sheet.cell_value(row_idx, col_idx))
                        if "打印时间" in cell_value:
                            # 找到打印时间单元格，设置字体大小为10号
                            excel_range = worksheet.Cells(row_idx + 1, col_idx + 1)
                            excel_range.Font.Size = 10
                            break
                    else:
                        continue
                    break
                
                print(f"打印区域: {print_area} (共{sheet.nrows}行)")
                
                # 打印
                worksheet.PrintOut()
                
                # 关闭工作簿
                workbook_obj.Close(False)
                excel.Quit()
                
                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
                    workbook.release_resources()
                
                return True
                
            except ImportError:
                print("win32com未安装，使用默认打印方式")
                # 释放资源
                # 只有xlrd的Workbook对象才有release_resources方法
                if hasattr(workbook, 'release_resources'):
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
    
    def kill_excel_processes(self, max_retries=3, retry_delay=1.0):
        """彻底清理Excel进程
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        
        Returns:
            bool: 是否成功终止所有Excel进程
        """
        try:
            import os
            import psutil
            import time
            
            retry_count = 0
            while retry_count < max_retries:
                # 查找并终止所有Excel进程
                excel_processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] in ['EXCEL.EXE', 'excel.exe']:
                            excel_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if not excel_processes:
                    print("没有发现Excel进程")
                    return True
                
                print(f"[Excel进程管理] 发现 {len(excel_processes)} 个Excel进程，正在终止...")
                
                # 先尝试正常终止
                for proc in excel_processes:
                    try:
                        proc.terminate()
                        print(f"[Excel进程管理] 已终止Excel进程 PID: {proc.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # 等待进程完全终止
                time.sleep(retry_delay)
                
                # 检查是否还有Excel进程
                remaining_processes = []
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] in ['EXCEL.EXE', 'excel.exe']:
                            remaining_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if not remaining_processes:
                    print("[Excel进程管理] 所有Excel进程已成功终止")
                    return True
                
                # 如果还有进程，尝试强制终止
                print(f"[Excel进程管理] 仍有 {len(remaining_processes)} 个Excel进程，尝试强制终止...")
                for proc in remaining_processes:
                    try:
                        proc.kill()
                        print(f"[Excel进程管理] 已强制终止Excel进程 PID: {proc.pid}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # 等待进程完全终止
                time.sleep(retry_delay)
                
                retry_count += 1
            
            # 最终检查
            final_check = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] in ['EXCEL.EXE', 'excel.exe']:
                        final_check.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if final_check:
                print(f"[Excel进程管理] 最终仍有 {len(final_check)} 个Excel进程未终止")
                return False
            else:
                print("[Excel进程管理] 所有Excel进程已成功终止")
                return True
                
        except ImportError:
            # 如果psutil不可用，尝试使用taskkill命令
            try:
                import subprocess
                print("[Excel进程管理] 使用taskkill命令终止Excel进程...")
                for i in range(max_retries):
                    result = subprocess.run(['taskkill', '/F', '/IM', 'EXCEL.EXE'], capture_output=True)
                    print(f"[Excel进程管理] Excel进程终止命令已执行 (尝试 {i+1}/{max_retries})")
                    time.sleep(retry_delay)
                return True
            except Exception as e:
                print(f"[Excel进程管理] 终止Excel进程失败: {str(e)}")
                return False
        except Exception as e:
            print(f"[Excel进程管理] 终止Excel进程失败: {str(e)}")
            return False
    
    def check_excel_processes(self):
        """检查是否有Excel进程在运行
        
        Returns:
            list: 运行中的Excel进程列表
        """
        try:
            import psutil
            excel_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] in ['EXCEL.EXE', 'excel.exe']:
                        excel_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return excel_processes
        except ImportError:
            return []
    
    def is_file_locked(self, file_path):
        """检查文件是否被锁定
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 文件是否被锁定
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # 尝试以独占模式打开文件
            with open(file_path, 'a') as f:
                pass
            return False
        except IOError:
            return True
        except Exception:
            return True
    
    def atomic_file_replace(self, source_path, target_path, max_retries=3, retry_delay=1.0):
        """原子性文件替换
        
        将源文件原子性地替换目标文件，确保操作要么完全成功，要么完全失败
        
        Args:
            source_path: 源文件路径（临时文件）
            target_path: 目标文件路径
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        
        Returns:
            bool: 操作是否成功
        """
        import os
        import shutil
        import tempfile
        import time
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                # 确保目标文件所在目录存在
                target_dir = os.path.dirname(target_path)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                
                # 生成临时文件路径（在同一目录下）
                temp_name = f"{os.path.basename(target_path)}.tmp{os.getpid()}_{int(time.time())}"
                temp_path = os.path.join(target_dir, temp_name)
                
                # 检查源文件是否存在
                if not os.path.exists(source_path):
                    print(f"[文件操作] 源文件不存在: {source_path}")
                    return False
                
                # 检查文件是否被锁定
                if self.is_file_locked(source_path):
                    print(f"[文件操作] 源文件被锁定: {source_path}")
                    time.sleep(retry_delay)
                    retry_count += 1
                    continue
                
                if os.path.exists(target_path) and self.is_file_locked(target_path):
                    print(f"[文件操作] 目标文件被锁定: {target_path}")
                    # 尝试清理Excel进程
                    self.kill_excel_processes()
                    time.sleep(retry_delay)
                    retry_count += 1
                    continue
                
                # 先复制到临时文件
                print(f"[文件操作] 复制文件: {source_path} -> {temp_path}")
                shutil.copy2(source_path, temp_path)
                
                # 确保文件完全写入
                with open(temp_path, 'rb') as f:
                    f.read()
                
                # 验证文件大小
                if os.path.getsize(temp_path) == 0:
                    print(f"[文件操作] 临时文件为空: {temp_path}")
                    os.remove(temp_path)
                    retry_count += 1
                    continue
                
                # 使用os.replace进行原子性替换
                print(f"[文件操作] 原子性替换: {temp_path} -> {target_path}")
                os.replace(temp_path, target_path)
                
                # 验证替换是否成功
                if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                    print(f"[文件操作] 原子性替换成功: {target_path}")
                    return True
                else:
                    print(f"[文件操作] 替换后文件不存在或为空: {target_path}")
                    retry_count += 1
                    continue
                    
            except Exception as e:
                print(f"[文件操作] 原子性文件替换失败: {str(e)}")
                # 清理临时文件
                try:
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                retry_count += 1
                time.sleep(retry_delay)
        
        print(f"[文件操作] 原子性文件替换失败，已达到最大重试次数")
        return False
    
    def clear_file_cache(self, file_path):
        """清理文件缓存，确保读取到最新数据
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 操作是否成功
        """
        try:
            import os
            if os.path.exists(file_path):
                # 使用os.stat获取文件信息，强制刷新缓存
                os.stat(file_path)
                print(f"[文件操作] 已清理文件缓存: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"[文件操作] 清理文件缓存失败: {str(e)}")
            return False
    
    def safe_file_operation(self, file_path, operation, max_retries=5, initial_delay=0.5, backoff_factor=2):
        """安全的文件操作，带有重试机制
        
        Args:
            file_path: 文件路径
            operation: 操作函数，接收文件路径作为参数
            max_retries: 最大重试次数
            initial_delay: 初始延迟时间（秒）
            backoff_factor: 退避因子
        
        Returns:
            操作结果
        """
        import time
        
        for attempt in range(max_retries):
            try:
                # 检查文件是否被锁定
                if os.path.exists(file_path) and self.is_file_locked(file_path):
                    print(f"[文件操作] 文件被锁定，等待... ({attempt+1}/{max_retries})")
                    # 尝试清理Excel进程
                    self.kill_excel_processes()
                    # 计算退避延迟
                    delay = initial_delay * (backoff_factor ** attempt)
                    time.sleep(delay)
                    continue
                
                # 执行操作
                result = operation(file_path)
                print(f"[文件操作] 操作成功: {file_path}")
                return result
                
            except Exception as e:
                print(f"[文件操作] 操作失败 ({attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # 计算退避延迟
                    delay = initial_delay * (backoff_factor ** attempt)
                    time.sleep(delay)
                    # 尝试清理Excel进程
                    self.kill_excel_processes()
                else:
                    print(f"[文件操作] 已达到最大重试次数，操作失败")
                    raise
    
    def create_file_backup(self, file_path, backup_dir=None):
        """创建文件备份
        
        Args:
            file_path: 文件路径
            backup_dir: 备份目录，默认为原文件所在目录
        
        Returns:
            str: 备份文件路径
        """
        try:
            import os
            import shutil
            import time
            
            if not os.path.exists(file_path):
                print(f"[文件操作] 原文件不存在，跳过备份: {file_path}")
                return None
            
            # 确定备份目录
            if backup_dir is None:
                backup_dir = os.path.dirname(file_path)
            
            # 创建备份目录
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            print(f"[文件操作] 已创建文件备份: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"[文件操作] 创建文件备份失败: {str(e)}")
            return None
    
    def monitor_system_health(self):
        """监控系统健康状态
        
        Returns:
            dict: 系统健康状态信息
        """
        import os
        import psutil
        import time
        
        health_status = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'excel_processes': [],
            'file_locks': [],
            'disk_space': {},
            'memory_usage': {},
            'cpu_usage': 0
        }
        
        try:
            # 检查Excel进程
            excel_processes = self.check_excel_processes()
            health_status['excel_processes'] = [{'pid': proc.pid, 'name': proc.info['name']} for proc in excel_processes]
            
            # 检查关键文件是否被锁定
            critical_files = [
                os.path.join(self.plan_dir, "计划号", "装炉顺序.xls"),
                os.path.join(self.plan_dir, "计划号", "总计划号列表.xls")
            ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    if self.is_file_locked(file_path):
                        health_status['file_locks'].append(file_path)
            
            # 检查磁盘空间
            disk_usage = psutil.disk_usage('.')
            health_status['disk_space'] = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent
            }
            
            # 检查内存使用
            memory_usage = psutil.virtual_memory()
            health_status['memory_usage'] = {
                'total': memory_usage.total,
                'available': memory_usage.available,
                'used': memory_usage.used,
                'percent': memory_usage.percent
            }
            
            # 检查CPU使用率
            health_status['cpu_usage'] = psutil.cpu_percent(interval=1)
            
        except Exception as e:
            print(f"[系统监控] 监控系统健康状态失败: {str(e)}")
        
        return health_status
    
    def check_and_warn(self):
        """检查系统状态并发出预警
        
        Returns:
            list: 预警信息列表
        """
        import os
        warnings = []
        
        # 检查Excel进程
        excel_processes = self.check_excel_processes()
        if len(excel_processes) > 5:
            warnings.append(f"[预警] 发现 {len(excel_processes)} 个Excel进程，可能存在进程泄露")
        
        # 检查关键文件是否被锁定
        critical_files = [
            os.path.join(self.plan_dir, "计划号", "装炉顺序.xls"),
            os.path.join(self.plan_dir, "计划号", "总计划号列表.xls")
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                if self.is_file_locked(file_path):
                    warnings.append(f"[预警] 文件被锁定: {file_path}")
        
        # 检查磁盘空间
        try:
            import psutil
            disk_usage = psutil.disk_usage('.')
            if disk_usage.percent > 90:
                warnings.append(f"[预警] 磁盘空间不足，使用率: {disk_usage.percent}%")
        except Exception:
            pass
        
        # 检查内存使用
        try:
            import psutil
            memory_usage = psutil.virtual_memory()
            if memory_usage.percent > 85:
                warnings.append(f"[预警] 内存使用过高，使用率: {memory_usage.percent}%")
        except Exception:
            pass
        
        # 检查计划号文件夹是否存在
        plan_dir = os.path.join(self.plan_dir, "计划号")
        if not os.path.exists(plan_dir):
            warnings.append(f"[预警] 计划号文件夹不存在: {plan_dir}")
        
        # 检查数据库文件
        if not os.path.exists(self.db_path):
            warnings.append(f"[预警] 数据库文件不存在: {self.db_path}")
        
        # 输出预警信息
        for warning in warnings:
            print(warning)
        
        return warnings
    
    def auto_repair(self):
        """自动修复系统问题
        
        Returns:
            dict: 修复结果
        """
        import os
        repair_results = {
            'excel_processes_killed': 0,
            'file_locks_released': 0,
            'directories_created': 0
        }
        
        try:
            # 清理Excel进程
            excel_processes = self.check_excel_processes()
            if excel_processes:
                success = self.kill_excel_processes()
                if success:
                    repair_results['excel_processes_killed'] = len(excel_processes)
                    print(f"[自动修复] 已清理 {len(excel_processes)} 个Excel进程")
            
            # 创建必要的目录
            plan_dir = os.path.join(self.plan_dir, "计划号")
            if not os.path.exists(plan_dir):
                os.makedirs(plan_dir, exist_ok=True)
                repair_results['directories_created'] = 1
                print(f"[自动修复] 已创建计划号文件夹: {plan_dir}")
            
            # 清理临时文件
            import glob
            temp_files = glob.glob(os.path.join(plan_dir, "*.tmp*"))
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                    print(f"[自动修复] 已清理临时文件: {temp_file}")
                except Exception as e:
                    print(f"[自动修复] 清理临时文件失败: {str(e)}")
            
        except Exception as e:
            print(f"[自动修复] 自动修复失败: {str(e)}")
        
        return repair_results

    # ==================== 自动导出依赖方法 ====================
    
    def export_zhuanglu_shunxu(self, add_debug_log=None):
        """导出装炉顺序 - 严格按照点点精灵脚本步骤执行
        
        参数:
            add_debug_log: 调试日志函数（可选），如果为None则不输出调试信息
        """
        import time
        log_lines = ["开始导出装炉顺序..."]
        
        # 如果没有传入调试日志函数，使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass  # 非调试模式下不输出
        
        # 文件路径 - 使用计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        # 准备临时文件路径
        temp_zhuanglu_file = os.path.join(plan_dir, f"装炉顺序_{int(time.time())}.tmp.xls")
        # 导出前清理可能存在的临时文件
        import glob
        for temp_file in glob.glob(os.path.join(plan_dir, "装炉顺序_*.tmp.xls")):
            try:
                os.remove(temp_file)
                add_debug_log(f"✓ 已清理临时文件: {os.path.basename(temp_file)}")
            except Exception as e:
                add_debug_log(f"✗ 清理临时文件失败: {str(e)}")
        
        # 从配置中读取窗口标题（优先使用自定义窗口名称）
        custom_title = self.coordinates.get("custom_window_title", "").strip()
        if custom_title:
            window_title = custom_title
        else:
            window_title = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")
        
        add_debug_log(f"【配置信息】")
        add_debug_log(f"窗口标题: {window_title}")
        add_debug_log(f"文件路径: {zhuanglu_file}")
        add_debug_log("")
        
        # 从配置中读取坐标
        zhuanglu_tab = self.coordinates.get("zhuanglu_tab", (261, 87))
        zhuanglu_export = self.coordinates.get("zhuanglu_export_btn", (990, 831))
        
        add_debug_log(f"【坐标配置】")
        add_debug_log(f"装炉顺作成管理标签: {zhuanglu_tab}")
        add_debug_log(f"装炉顺序导出按钮: {zhuanglu_export}")
        add_debug_log("")
        
        # 步骤1: 激活目标窗口
        log_lines.append(f"[1/9] 激活目标窗口: {window_title}...")
        add_debug_log(f"【步骤1】激活目标窗口: {window_title}")
        try:
            if not self.activate_window(window_title):
                log_lines.append("✗ 激活窗口失败")
                add_debug_log("✗ 激活窗口失败")
                return False, "\n".join(log_lines)
            log_lines.append(f"✓ 已激活窗口: {window_title}")
            add_debug_log(f"✓ 已激活窗口: {window_title}")
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # 激活窗口后延迟
        except Exception as e:
            log_lines.append(f"✗ 激活窗口失败: {str(e)}")
            add_debug_log(f"✗ 激活窗口失败: {str(e)}")
            return False, "\n".join(log_lines)
        
        # 步骤2: 鼠标点击 - 装炉顺作成管理画面
        log_lines.append(f"[2/9] 鼠标点击: 装炉顺作成管理画面 @ {zhuanglu_tab}...")
        add_debug_log(f"【步骤2】鼠标点击: 装炉顺作成管理画面")
        add_debug_log(f"  坐标: ({zhuanglu_tab[0]}, {zhuanglu_tab[1]})")
        pyautogui.moveTo(zhuanglu_tab[0], zhuanglu_tab[1])
        pyautogui.click()
        add_debug_log(f"  延迟: 500ms")
        time.sleep(0.5)  # 点击后延迟
        log_lines.append("点击完成")
        add_debug_log("✓ 点击完成")
        
        # 步骤3: 键盘按键 - F2
        log_lines.append("[3/9] 键盘按键: F2...")
        add_debug_log(f"【步骤3】键盘按键: F2")
        pyautogui.press('f2')
        add_debug_log(f"  延迟: 500ms")
        time.sleep(0.5)  # F2后延迟
        log_lines.append("F2键已按下")
        add_debug_log("✓ F2键已按下")

        # 步骤4: 延迟 - 500ms
        log_lines.append("[4/9] 延迟: 500ms...")
        add_debug_log(f"【步骤4】延迟: 500ms")
        time.sleep(0.5)
        log_lines.append("延迟完成")
        add_debug_log("✓ 延迟完成")

        # 步骤5: 鼠标点击 - 导出按钮
        log_lines.append(f"[5/9] 鼠标点击: 导出按钮 @ {zhuanglu_export}...")
        add_debug_log(f"【步骤5】鼠标点击: 导出按钮")
        add_debug_log(f"  坐标: ({zhuanglu_export[0]}, {zhuanglu_export[1]})")
        pyautogui.moveTo(zhuanglu_export[0], zhuanglu_export[1])
        pyautogui.click()
        add_debug_log(f"  延迟: 1000ms (等待保存对话框)")
        time.sleep(1.0)  # 点击后延迟，等待保存对话框弹出
        log_lines.append("导出按钮点击完成，等待保存对话框...")
        add_debug_log("✓ 导出按钮点击完成")

        # 步骤6: 直接输入完整路径+文件名
        log_lines.append("[6/9] 直接输入完整路径+文件名...")
        add_debug_log(f"【步骤6】直接输入完整路径+文件名")
        # 等待对话框完全弹出并获取焦点
        add_debug_log(f"  延迟: 1000ms (等待对话框)")
        time.sleep(1.0)
        # 构造临时文件路径（不带扩展名）
        temp_full_path = os.path.splitext(temp_zhuanglu_file)[0]
        add_debug_log(f"  临时文件路径: {temp_full_path}")
        import pyperclip
        pyperclip.copy(temp_full_path)
        add_debug_log(f"  已复制到剪贴板")
        add_debug_log(f"  延迟: 200ms")
        time.sleep(0.2)
        # 粘贴完整路径到文件名输入框
        add_debug_log(f"  执行: Ctrl+V 粘贴")
        pyautogui.hotkey('ctrl', 'v')
        add_debug_log(f"  延迟: 500ms")
        time.sleep(0.5)  # 输入后延迟
        log_lines.append(f"已输入完整路径: {temp_full_path}")
        add_debug_log(f"✓ 已输入完整路径")

        # 步骤8: 键盘按键 - Return
        log_lines.append("[8/8] 键盘按键: Return...")
        add_debug_log(f"【步骤8】键盘按键: Return")
        pyautogui.press('return')
        log_lines.append("回车键已按下")
        add_debug_log(f"✓ 回车键已按下")
        
        # 等待导出完成
        log_lines.append("等待导出完成...")
        add_debug_log(f"【等待导出完成】")
        add_debug_log(f"  延迟: 3000ms")
        time.sleep(3)
        add_debug_log(f"✓ 导出完成")
        
        # 确保所有Excel进程都已关闭（避免文件占用）
        log_lines.append("确保Excel进程已关闭...")
        add_debug_log(f"【关闭Excel进程】")
        try:
            import subprocess
            # 强制关闭所有Excel进程，使用creationflags隐藏窗口
            subprocess.run(
                ['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            add_debug_log(f"  延迟: 2000ms")
            time.sleep(2)
            log_lines.append("Excel进程已强制关闭")
            add_debug_log(f"✓ Excel进程已强制关闭")
        except Exception as e:
            log_lines.append(f"强制关闭Excel进程失败: {str(e)}")
            add_debug_log(f"✗ 强制关闭Excel进程失败: {str(e)}")
        
        # 原子性文件替换：将临时文件替换为正式文件
        log_lines.append("执行原子性文件替换...")
        add_debug_log(f"【原子性文件替换】")
        try:
            if os.path.exists(temp_zhuanglu_file):
                add_debug_log(f"  临时文件: {temp_zhuanglu_file}")
                add_debug_log(f"  目标文件: {zhuanglu_file}")
                # 执行原子性替换，使用重试机制
                success = self.atomic_file_replace(temp_zhuanglu_file, zhuanglu_file, max_retries=5, retry_delay=1.0)
                if success:
                    # 清理文件缓存，确保读取到最新数据
                    self.clear_file_cache(zhuanglu_file)
                    add_debug_log(f"✓ 原子性文件替换成功")
                    add_debug_log(f"✓ 文件缓存已清理")
                    log_lines.append("原子性文件替换成功")
                else:
                    add_debug_log(f"✗ 原子性文件替换失败")
                    log_lines.append("原子性文件替换失败")
            else:
                add_debug_log(f"✗ 临时文件不存在: {temp_zhuanglu_file}")
                log_lines.append("临时文件不存在")
        except Exception as e:
            add_debug_log(f"✗ 原子性文件替换异常: {str(e)}")
            log_lines.append(f"原子性文件替换异常: {str(e)}")
        
        # 导入数据到数据库
        log_lines.append("导入数据到数据库...")
        add_debug_log(f"【导入数据到数据库】")
        try:
            # 等待文件完全写入
            time.sleep(1.0)
            
            # 导入装炉顺序数据到数据库
            import_success = self.import_zhuanglu_shunxu_to_db(zhuanglu_file)
            if import_success:
                add_debug_log(f"✓ 装炉顺序数据导入数据库成功")
                # 导出后将数据读取到内存中
                add_debug_log(f"【读取数据到内存】")
                # 重新读取数据库数据到内存
                self.refresh_plan_list_from_file()
                add_debug_log(f"✓ 装炉顺序数据已读取到内存")
            else:
                add_debug_log(f"✗ 装炉顺序数据导入数据库失败")
        except Exception as e:
            log_lines.append(f"导入数据到数据库失败: {str(e)}")
            add_debug_log(f"✗ 导入数据到数据库失败: {str(e)}")
        
        # 刷新计划号列表（使用副本读取方案，避免文件占用）
        log_lines.append("刷新计划号列表...")
        add_debug_log(f"【刷新计划号列表】")
        try:
            self.refresh_plan_list_from_file()
            log_lines.append("计划号列表刷新完成")
            add_debug_log(f"✓ 计划号列表刷新完成")
        except Exception as e:
            log_lines.append(f"刷新计划号列表失败: {str(e)}")
            add_debug_log(f"✗ 刷新计划号列表失败: {str(e)}")
        
        log_lines.append("装炉顺序导出操作完成")
        add_debug_log(f"")
        add_debug_log(f"【导出完成】装炉顺序导出操作完成")
        return True, "\n".join(log_lines)
    
    def export_zhizhi_plan_list(self, test_window=None, test_mode=False, add_debug_log=None):
        """导出总计划号列表
        
        参数:
            test_window: 测试窗口标题，如果为None则自动选择
            test_mode: 是否为测试模式（简化版不再使用）
            add_debug_log: 调试日志函数
        """
        # 如果没有传入调试日志函数，使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import pyautogui
            import time
            
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("导出总计划号列表")
            add_debug_log("="*60)
            
            # 选择测试窗口
            if test_window is None:
                test_window = self.select_test_window()
            if not test_window:
                add_debug_log("✗ 用户取消选择测试窗口")
                print("✗ 用户取消选择测试窗口")
                return False
            
            add_debug_log(f"窗口标题: {test_window}")
            print("\n=== 导出总计划号列表 ===")
            
            # 文件路径 - 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            total_plan_file = os.path.join(plan_dir, "总计划号列表.xls")
            
            # 准备临时文件路径
            temp_total_plan_file = os.path.join(plan_dir, f"总计划号列表_{int(time.time())}.tmp.xls")
            # 导出前清理可能存在的临时文件
            import glob
            for temp_file in glob.glob(os.path.join(plan_dir, "总计划号列表_*.tmp.xls")):
                try:
                    os.remove(temp_file)
                    add_debug_log(f"✓ 已清理临时文件: {os.path.basename(temp_file)}")
                except Exception as e:
                    add_debug_log(f"✗ 清理临时文件失败: {str(e)}")
            
            # 从配置中读取坐标
            zhizhi_tab = self.coordinates.get("zhizhi_tab", (92, 85))
            plan_select = self.coordinates.get("plan_select", (860, 134))
            zhizhi_export_btn = self.coordinates.get("zhizhi_export_btn", (77, 501))
            
            add_debug_log(f"")
            add_debug_log(f"[坐标配置]")
            add_debug_log(f"  轧制计划管理标签: {zhizhi_tab}")
            add_debug_log(f"  选择计划号: {plan_select}")
            add_debug_log(f"  导出按钮: {zhizhi_export_btn}")
            
            # 步骤1: 跳过激活窗口（已在导出装炉顺序时激活）
            print("[1/7] 跳过激活窗口（已在导出装炉顺序时激活）...")
            add_debug_log(f"")
            add_debug_log(f"[步骤1] 跳过激活窗口（已在导出装炉顺序时激活）")
            
            # 步骤2: 点击轧制计划管理标签
            print(f"[2/7] 点击轧制计划管理标签...")
            add_debug_log(f"")
            add_debug_log(f"[步骤2] 点击轧制计划管理标签")
            add_debug_log(f"  坐标: ({zhizhi_tab[0]}, {zhizhi_tab[1]})")
            pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
            pyautogui.click()
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)
            
            # 步骤3: 选择计划号
            print(f"[3/7] 选择计划号...")
            add_debug_log(f"")
            add_debug_log(f"[步骤3] 选择计划号")
            add_debug_log(f"  坐标: ({plan_select[0]}, {plan_select[1]})")
            pyautogui.moveTo(plan_select[0], plan_select[1])
            pyautogui.click()
            add_debug_log(f"  延迟: 300ms")
            time.sleep(0.3)
            
            # 步骤4: 按Home键全选 + 回车确认
            print("[4/7] 按Home键选择所有计划号...")
            add_debug_log(f"")
            add_debug_log(f"[步骤4] 按Home键选择所有计划号")
            pyautogui.press('home')
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)
            pyautogui.press('return')
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)
            
            # 步骤5: 按F2刷新
            print("[5/7] 按F2刷新...")
            add_debug_log(f"")
            add_debug_log(f"[步骤5] 按F2刷新")
            pyautogui.press('f2')
            time.sleep(0.5)
            
            # 步骤6: 点击导出按钮
            print(f"[6/7] 点击导出按钮...")
            add_debug_log(f"")
            add_debug_log(f"[步骤6] 点击导出按钮")
            add_debug_log(f"  坐标: ({zhizhi_export_btn[0]}, {zhizhi_export_btn[1]})")
            pyautogui.moveTo(zhizhi_export_btn[0], zhizhi_export_btn[1])
            pyautogui.click()
            add_debug_log(f"  延迟: 1500ms (等待保存对话框)")
            time.sleep(1.5)
            
            # 步骤7: 直接输入完整路径+文件名
            print("[7/7] 直接输入完整路径+文件名...")
            add_debug_log(f"")
            add_debug_log(f"[步骤7] 直接输入完整路径+文件名")
            add_debug_log(f"  延迟: 500ms (等待对话框)")
            time.sleep(0.5)
            # 构造临时文件路径（不带扩展名）
            temp_full_path = os.path.splitext(temp_total_plan_file)[0]
            add_debug_log(f"  临时文件路径: {temp_full_path}")
            import pyperclip
            pyperclip.copy(temp_full_path)
            add_debug_log(f"  已复制到剪贴板")
            add_debug_log(f"  延迟: 200ms")
            time.sleep(0.2)
            # 粘贴完整路径到文件名输入框
            add_debug_log(f"  执行: Ctrl+V 粘贴")
            pyautogui.hotkey('ctrl', 'v')
            add_debug_log(f"  延迟: 500ms")
            time.sleep(0.5)  # 输入后延迟
            print(f"已输入完整路径: {temp_full_path}")
            add_debug_log(f"✓ 已输入完整路径")
            
            # 保存文件
            add_debug_log(f"")
            add_debug_log(f"[保存文件]")
            add_debug_log(f"  按键: Return")
            pyautogui.press('return')
            add_debug_log(f"  延迟: 2000ms (等待保存完成)")
            time.sleep(2)
            
            # 原子性文件替换：将临时文件替换为正式文件
            add_debug_log(f"")
            add_debug_log(f"[原子性文件替换]")
            try:
                if os.path.exists(temp_total_plan_file):
                    add_debug_log(f"  临时文件: {temp_total_plan_file}")
                    add_debug_log(f"  目标文件: {total_plan_file}")
                    # 执行原子性替换，使用重试机制
                    success = self.atomic_file_replace(temp_total_plan_file, total_plan_file, max_retries=5, retry_delay=1.0)
                    if success:
                        # 清理文件缓存，确保读取到最新数据
                        self.clear_file_cache(total_plan_file)
                        add_debug_log(f"✓ 原子性文件替换成功")
                        add_debug_log(f"✓ 文件缓存已清理")
                        print("总计划号列表已通过原子性操作保存到计划号文件夹")
                    else:
                        add_debug_log(f"✗ 原子性文件替换失败")
                        print("原子性文件替换失败")
                else:
                    add_debug_log(f"✗ 临时文件不存在: {temp_total_plan_file}")
                    print("临时文件不存在")
            except Exception as e:
                add_debug_log(f"✗ 原子性文件替换异常: {str(e)}")
                print(f"原子性文件替换异常: {str(e)}")
            
            # 导入总计划号列表数据到数据库
            add_debug_log(f"")
            add_debug_log(f"[导入数据到数据库]")
            print("导入总计划号列表数据到数据库...")
            try:
                import_success = self.import_zhizhi_plan_list_to_db(total_plan_file)
                if import_success:
                    add_debug_log(f"✓ 总计划号列表数据导入数据库成功")
                    # 导出后将数据读取到内存中
                    add_debug_log(f"【读取数据到内存】")
                    # 重新读取数据库数据到内存
                    self.read_zhizhi_plan_list_with_coords(add_debug_log=add_debug_log)
                    add_debug_log(f"✓ 总计划号列表数据已读取到内存")
                else:
                    add_debug_log(f"✗ 总计划号列表数据导入数据库失败")
            except Exception as e:
                print(f"导入总计划号列表数据到数据库失败: {str(e)}")
                add_debug_log(f"✗ 导入总计划号列表数据到数据库失败: {str(e)}")
            
            # 重新读取总计划号列表数据，更新缓存并计算坐标
            add_debug_log(f"")
            add_debug_log(f"[重新读取数据]")
            print("重新读取总计划号列表数据，更新缓存并计算坐标...")
            add_debug_log(f"  延迟: 1000ms")
            time.sleep(1)  # 添加1秒延迟
            self.read_zhizhi_plan_list_with_coords(add_debug_log=add_debug_log)
            
            print("✓ 总计划号列表导出成功")
            add_debug_log(f"✓ 总计划号列表导出成功")
            return True
            
        except Exception as e:
            print(f"✗ 导出总计划号列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_zhizhi_plan_list_with_coords(self, add_debug_log=None):
        """读取总计划号列表数据，返回计划号到坐标的映射字典
        
        根据设置页面中的第一个计划号坐标和计划号间距，
        计算每个计划号的实际屏幕坐标。
        
        参数:
            add_debug_log: 调试日志函数（可选）
            
        返回: {计划号: (x, y)} 的字典
        """
        # 如果没有传入调试日志函数，使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import sqlite3
            import os
            
            add_debug_log(f"")
            add_debug_log(f"[读取总计划号列表]")
            add_debug_log(f"  数据库路径: {self.db_path}")
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 从数据库获取总计划号列表数据
            cursor.execute('''
                SELECT plan_no, seq_no 
                FROM total_plan_list 
                ORDER BY seq_no
            ''')
            plan_data = cursor.fetchall()
            
            if not plan_data:
                add_debug_log(f"  ✗ 数据库中无数据")
                print(f"总计划号列表数据不存在")
                conn.close()
                return None
            
            add_debug_log(f"  ✓ 数据库读取成功")
            print(f"读取总计划号列表数据并计算坐标")
            
            # 从配置中读取第一个计划号坐标、间距和偏移量
            first_plan = self.coordinates.get("first_plan", (239, 208))
            plan_spacing = self.coordinates.get("plan_spacing", 21)
            # 第一个计划号的纵坐标偏移量（用于校准中点位置）
            first_plan_offset = self.coordinates.get("first_plan_offset", 0)
            
            first_x = first_plan[0]
            first_y = first_plan[1] + first_plan_offset  # 应用偏移量校准
            
            add_debug_log(f"")
            add_debug_log(f"[坐标计算配置]")
            add_debug_log(f"  第一个计划号原始坐标: ({first_plan[0]}, {first_plan[1]})")
            add_debug_log(f"  偏移量: {first_plan_offset}")
            add_debug_log(f"  校准后坐标: ({first_x}, {first_y})")
            add_debug_log(f"  计划号间距: {plan_spacing} 像素")
            
            print(f"第一个计划号原始坐标: ({first_plan[0]}, {first_plan[1]})")
            print(f"第一个计划号偏移量: {first_plan_offset}")
            print(f"第一个计划号校准后坐标: ({first_x}, {first_y})")
            print(f"计划号间距: {plan_spacing} 像素")
            
            # 读取计划号并计算坐标
            plan_coord_map = {}
            zhizhi_plan_list = []  # 临时存储序号和计划号
            
            add_debug_log(f"")
            add_debug_log(f"[读取计划号并计算坐标]")
            add_debug_log(f"  数据行数: {len(plan_data)}")
            
            for row_index, (plan_no, seq_value) in enumerate(plan_data):
                if plan_no:
                    # 直接使用行索引计算坐标，不依赖序号值
                    # row_index 从0开始，正好对应第一个计划号的索引
                    coord_y = first_y + (row_index * plan_spacing)
                    coord_x = first_x
                    
                    plan_coord_map[plan_no] = (coord_x, coord_y)
                    zhizhi_plan_list.append((seq_value, plan_no))
                    # 只显示前5个，避免日志过长
                    if row_index < 5:
                        add_debug_log(f"    {plan_no}: 行={row_index}, 坐标=({coord_x}, {coord_y})")
                    elif row_index == 5:
                        add_debug_log(f"    ... 还有 {len(plan_data) - 6} 个计划号")
                    print(f"  计划号 {plan_no}: 行索引={row_index}, 坐标=({coord_x}, {coord_y})")
            
            # 关闭数据库连接
            conn.close()
            
            add_debug_log(f"")
            add_debug_log(f"  总计: {len(plan_coord_map)} 个计划号坐标")
            print(f"\n从总计划号列表计算了 {len(plan_coord_map)} 个计划号的坐标")
            
            # 更新缓存
            self.zhizhi_plan_list = zhizhi_plan_list
            self.zhizhi_plan_coord_map = plan_coord_map
            add_debug_log(f"  ✓ 已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            print(f"已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            
            add_debug_log(f"  ✓ 坐标计算完成")
            return plan_coord_map
            
        except Exception as e:
            print(f"读取总计划号列表并计算坐标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_single_plan_detail(self, plan_no, plan_coord, plan_detail_export_btn=None, test_window=None, add_debug_log=None):
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
            add_debug_log: 调试日志函数
            
        返回:
            True - 导出成功
            False - 导出失败
        """
        # 如果没有传入调试日志函数，使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import pyautogui
            import time
            
            print(f"\n=== 导出计划 {plan_no} 的明细 ===")
            print(f"计划号坐标: {plan_coord}")
            
            add_debug_log(f"  开始导出明细...")
            
            # 选择测试窗口
            if test_window is None:
                test_window = self.select_test_window()
            if not test_window:
                add_debug_log(f"    ✗ 用户取消选择测试窗口")
                print("✗ 用户取消选择测试窗口")
                return False
            
            add_debug_log(f"    窗口: {test_window}")
            
            # 激活窗口
            add_debug_log(f"    [1] 激活窗口...")
            if not self.activate_window(test_window):
                add_debug_log(f"    ✗ 激活窗口失败")
                print("✗ 激活窗口失败")
                return False
            add_debug_log(f"    ✓ 窗口已激活")
            add_debug_log(f"    延迟: 300ms")
            time.sleep(0.3)
            
            # 获取导出计划明细按钮坐标
            if plan_detail_export_btn is None:
                plan_detail_export_btn = self.coordinates.get("plan_detail_export", (79, 870))
            
            # 步骤1: 鼠标点击计划号坐标
            print(f"[1/7] 点击计划号 {plan_no} 坐标 {plan_coord}...")
            add_debug_log(f"    [2] 点击计划号坐标: {plan_coord}")
            pyautogui.moveTo(plan_coord[0], plan_coord[1])
            pyautogui.click()
            add_debug_log(f"    延迟: 500ms")
            time.sleep(0.5)  # 延迟500ms
            
            # 步骤2: 鼠标点击导出计划明细按钮
            print(f"[2/7] 点击导出计划明细按钮 {plan_detail_export_btn}...")
            add_debug_log(f"    [3] 点击导出按钮: {plan_detail_export_btn}")
            pyautogui.moveTo(plan_detail_export_btn[0], plan_detail_export_btn[1])
            pyautogui.click()
            add_debug_log(f"    延迟: 500ms (等待对话框)")
            time.sleep(0.5)  # 等待保存对话框弹出
            
            # 步骤3: 键盘输入计划号（使用剪贴板粘贴）
            print(f"[3/7] 输入计划号 '{plan_no}'...")
            add_debug_log(f"    [4] 输入计划号: {plan_no}")
            import pyperclip
            pyperclip.copy(plan_no)
            add_debug_log(f"    延迟: 200ms")
            time.sleep(0.2)
            add_debug_log(f"    执行: Ctrl+V 粘贴")
            pyautogui.hotkey('ctrl', 'v')
            add_debug_log(f"    延迟: 300ms")
            time.sleep(0.3)
            
            # 步骤4: 按回车确认
            print("[4/4] 按回车确认...")
            add_debug_log(f"    [5] 按键: Return")
            pyautogui.press('return')
            add_debug_log(f"    延迟: 2000ms (等待保存完成)")
            time.sleep(2)  # 等待保存完成
            
            add_debug_log(f"    ✓ 导出完成")
            print(f"✓ 计划 {plan_no} 明细导出成功")
            return True
            
        except Exception as e:
            add_debug_log(f"    ✗ 导出失败: {str(e)}")
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
                if file.startswith("装炉顺序") or file.startswith("总计划号列表") or file in ["装炉顺序_显示.xls", "合并文件.xls"]:
                    print(f"跳过系统文件: {file}")
                    skipped_count += 1
                    continue
                
                # 只处理xls和xlsx文件
                if not (file.endswith(".xls") or file.endswith(".xlsx")):
                    continue
                
                # 尝试读取文件获取计划号
                try:
                    import tempfile
                    import shutil
                    
                    # 使用副本读取策略
                    temp_file_path = None
                    try:
                        # 创建临时副本（存储在计划号文件夹中）
                        plan_dir = os.path.join(self.plan_dir, "计划号")
                        temp_file_name = f"temp_{os.path.basename(file_path)}_{int(time.time())}.xls"
                        temp_file_path = os.path.join(plan_dir, temp_file_name)
                        shutil.copy2(file_path, temp_file_path)
                        print(f"已创建临时副本: {temp_file_path}")
                        
                        # 读取临时副本
                        success, result = self.safe_read_excel(temp_file_path, max_retries=3, retry_delay=0.5)
                        if not success:
                            print(f"读取副本失败 {file}: {result}，尝试直接读取...")
                            # 副本读取失败，尝试直接读取
                            success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
                            if not success:
                                print(f"读取文件失败 {file}: {result}")
                                skipped_count += 1
                                continue
                    except Exception as e:
                        print(f"创建副本失败 {file}: {str(e)}，尝试直接读取...")
                        # 创建副本失败，尝试直接读取
                        success, result = self.safe_read_excel(file_path, max_retries=3, retry_delay=0.5)
                        if not success:
                            print(f"读取文件失败 {file}: {result}")
                            skipped_count += 1
                            continue
                    finally:
                        # 清理临时文件
                        if temp_file_path and os.path.exists(temp_file_path):
                            try:
                                os.unlink(temp_file_path)
                                print(f"已删除临时副本: {temp_file_path}")
                            except:
                                pass
                    
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
            import win32con

            def callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    if window_title in win32gui.GetWindowText(hwnd):
                        extra.append(hwnd)

            hwnds = []
            win32gui.EnumWindows(callback, hwnds)

            if hwnds:
                hwnd = hwnds[0]

                # 恢复窗口（如果最小化）
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.3)

                # 方法1: 显示窗口
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.2)

                # 方法2: 将窗口置于最顶层
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法3: 取消最顶层（恢复正常层级，但已经在前面了）
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法4: 设置前台窗口
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)

                # 方法5: 将窗口带到最前面
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)

                return True
            return False
        except Exception as e:
            print(f"激活窗口失败: {str(e)}")
            # 如果win32gui不可用，尝试使用pyautogui
            import pyautogui
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.typewrite(window_title)
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            return True
    
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
        file_path = os.path.join(self.plan_dir, "APS.txt")
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
        import json
        
        # 默认坐标值
        default_coords = {
            # 装炉顺序导出坐标
            "zhuanglu_tab": (284, 84),           # 装炉顺作成管理标签
            "zhuanglu_export_btn": (988, 808),   # 装炉顺序导出按钮
            
            # 轧制计划管理页面坐标
            "zhizhi_tab": (107, 85),             # 轧制计划管理标签
            "plan_select": (734, 135),            # 选择计划号
            "zhizhi_export_btn": (78, 626),       # 导出总计划号列表按钮
            
            # 计划明细导出坐标
            "first_plan": (235, 207),            # 第一个计划号
            "plan_spacing": 21,                  # 计划号间距（垂直）
            "first_plan_offset": 0,              # 第一个计划号纵坐标偏移量
            "plan_detail_export": (79, 851),     # 计划明细导出按钮
            
            # 测试窗口和速度设置
            "test_window": "BGCMS1-宝钢股份多基地制造管理系统运行环境",  # 默认测试窗口
            "export_speed": "中",               # 默认导出速度
            "custom_window_title": "",          # 自定义窗口名称
            
            # 操作提示设置
            "show_operation_warning": True,       # 是否显示"不要操作鼠标键盘"提示
            # 导出后处理设置
            "auto_process_after_export": False,    # 导出完成后是否自动处理计划
            "auto_print_after_export": False,      # 处理完成后是否自动打印计划
            
            # 调试模式
            "debug_mode": False,                   # 调试模式（显示详细日志）
            
            # 防退出登录设置
            "anti_logout_interval_value": 100,      # 防退出登录时间间隔值
            "anti_logout_interval": 6000,          # 防退出登录时间间隔（毫秒）
            "anti_logout_unit": "分钟",             # 防退出登录时间单位
            
            # 自动执行设置
            "auto_exec_interval": 30,              # 自动执行时间间隔（分钟）
            "auto_exec_times": ""                  # 自动执行指定时间
        }
        
        config_file = os.path.join(self.plan_dir, "export_coordinates.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # 合并默认值和保存值
                    default_coords.update(saved)
                    return default_coords
            except Exception as e:
                print(f"加载坐标配置失败: {str(e)}")
        return default_coords

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
        "zhuanglu_tab": (284, 84),           # 装炉顺作成管理标签
        "zhuanglu_export_btn": (988, 808),   # 装炉顺序导出按钮
        
        # 轧制计划管理页面坐标
        "zhizhi_tab": (107, 85),             # 轧制计划管理标签
        "plan_select": (734, 135),            # 选择计划号
        "zhizhi_export_btn": (78, 626),       # 导出总计划号列表按钮
        
        # 计划明细导出坐标
        "first_plan": (235, 207),            # 第一个计划号
        "plan_spacing": 21,                  # 计划号间距（垂直）
        "first_plan_offset": 0,              # 第一个计划号纵坐标偏移量
        "plan_detail_export": (79, 851),     # 计划明细导出按钮
        
        # 测试窗口和速度设置
        "test_window": "BGCMS1-宝钢股份多基地制造管理系统运行环境",  # 默认测试窗口
        "export_speed": "中",               # 默认导出速度
        "custom_window_title": "",          # 自定义窗口名称
        
        # 操作提示设置
        "show_operation_warning": False,       # 是否显示"不要操作鼠标键盘"提示
        # 导出后处理设置
        "auto_process_after_export": True,    # 导出完成后是否自动处理计划
        "auto_print_after_export": True,      # 处理完成后是否自动打印计划
        
        # 调试模式
        "debug_mode": False,                   # 调试模式（显示详细日志）
        
        # 防退出登录设置
        "anti_logout_interval_value": 100,      # 防退出登录时间间隔值
        "anti_logout_interval": 6000,          # 防退出登录时间间隔（毫秒）
        "anti_logout_unit": "分钟",             # 防退出登录时间单位
        
        # 自动执行设置
        "auto_exec_interval": 30,              # 自动执行时间间隔（分钟）
        "auto_exec_times": ""                  # 自动执行指定时间
    }

    def __init__(self, root, plan_dir, main_app=None):
        self.root = root
        self.plan_dir = plan_dir
        self.main_app = main_app  # MainApp实例，用于实时更新配置
        
        # 导入os模块
        import os
        
        self.config_file = os.path.join(plan_dir, "export_coordinates.json")
        
        # 如果有main_app，使用main_app的coordinates
        if main_app and hasattr(main_app, 'coordinates'):
            self.coordinates = main_app.coordinates
        else:
            self.coordinates = self.load_coordinates()
            
        # 初始化状态标签字典
        self.status_labels = {}  
        
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
        spacing_entry = ttk.Entry(spacing_frame, textvariable=self.plan_spacing_var, width=10)
        spacing_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(spacing_frame, text="像素").pack(side=tk.LEFT)
        
        # 实时更新计划号间距
        def on_spacing_change(*args):
            try:
                self.coordinates["plan_spacing"] = int(self.plan_spacing_var.get())
                # 立即保存到文件
                self.save_coordinates()
            except:
                pass
        self.plan_spacing_var.trace_add("write", on_spacing_change)
        
        # 第一个计划号纵坐标偏移量（用于校准中点位置）
        offset_frame = ttk.Frame(detail_frame)
        offset_frame.pack(fill=tk.X, pady=5)
        ttk.Label(offset_frame, text="纵坐标偏移量:", width=20).pack(side=tk.LEFT)
        self.first_plan_offset_var = tk.StringVar()
        offset_entry = ttk.Entry(offset_frame, textvariable=self.first_plan_offset_var, width=10)
        offset_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(offset_frame, text="像素 (正值向下,负值向上)").pack(side=tk.LEFT)
        
        # 实时更新纵坐标偏移量
        def on_offset_change(*args):
            try:
                self.coordinates["first_plan_offset"] = int(self.first_plan_offset_var.get())
                # 立即保存到文件
                self.save_coordinates()
            except:
                pass
        self.first_plan_offset_var.trace_add("write", on_offset_change)
        
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
                          command=lambda v=value: (self.coordinates.update({"test_window": v}), 
                                                  self.log(f"测试窗口已设置为: {v}"),
                                                  self.save_coordinates())).pack(anchor=tk.W, padx=10, pady=2)
        
        # 速度设置
        speed_label = ttk.Label(test_settings_frame, text="自动导出速度:", font=('微软雅黑', 10, 'bold'))
        speed_label.pack(anchor=tk.W, pady=5)
        
        self.export_speed_var = tk.StringVar(value=self.coordinates.get("export_speed", "中"))
        
        speed_options = ["慢", "中", "快"]
        speed_frame = ttk.Frame(test_settings_frame)
        speed_frame.pack(anchor=tk.W, pady=2)
        
        for speed in speed_options:
            ttk.Radiobutton(speed_frame, text=speed, variable=self.export_speed_var, value=speed, 
                          command=lambda v=speed: (self.coordinates.update({"export_speed": v}),
                                                  self.save_coordinates())).pack(side=tk.LEFT, padx=15)
        
        # 自定义窗口名称
        custom_window_frame = ttk.Frame(test_settings_frame)
        custom_window_frame.pack(anchor=tk.W, pady=10, fill=tk.X)
        
        ttk.Label(custom_window_frame, text="自定义窗口名称:", font=('微软雅黑', 10, 'bold')).pack(anchor=tk.W)
        
        self.custom_window_var = tk.StringVar(value=self.coordinates.get("custom_window_title", ""))
        custom_window_entry = ttk.Entry(custom_window_frame, textvariable=self.custom_window_var, width=50)
        custom_window_entry.pack(anchor=tk.W, pady=2)
        
        # 实时更新自定义窗口名称
        def on_custom_window_change(*args):
            self.coordinates["custom_window_title"] = self.custom_window_var.get().strip()
            # 立即保存到文件
            self.save_coordinates()
        self.custom_window_var.trace_add("write", on_custom_window_change)
        
        ttk.Label(custom_window_frame, text="如果设置，将优先使用此窗口名称进行激活（留空使用上面选择的窗口）", 
                 foreground="gray", font=('微软雅黑', 9)).pack(anchor=tk.W)
        
        # 调试模式
        debug_frame = ttk.Frame(test_settings_frame)
        debug_frame.pack(anchor=tk.W, pady=10)
        
        self.debug_mode_var = tk.BooleanVar(value=self.coordinates.get("debug_mode", False))
        self.debug_checkbox = ttk.Checkbutton(
            debug_frame, 
            text="调试模式（显示详细操作日志）", 
            variable=self.debug_mode_var,
            command=self.on_debug_mode_changed
        )
        self.debug_checkbox.pack(anchor=tk.W)
        
        ttk.Label(debug_frame, text="自动导出时显示详细的操作步骤和坐标信息，便于排查问题", 
                 foreground="gray", font=('微软雅黑', 9)).pack(anchor=tk.W, padx=20)
        
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
        
        # 默认设置为选中
        self.auto_process_var = tk.BooleanVar(value=self.coordinates.get("auto_process_after_export", True))
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
        # 默认设置为选中
        self.auto_print_var = tk.BooleanVar(value=self.coordinates.get("auto_print_after_export", True))
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
        
        # 恢复默认值按钮
        ttk.Button(btn_frame, text="🔄 恢复默认值",
                  command=self.restore_defaults).pack(side=tk.LEFT, padx=5)
        
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
        entry = ttk.Entry(row, textvariable=string_var, width=12)
        entry.pack(side=tk.LEFT, padx=5)
        
        # 实时更新坐标
        def on_coord_change(*args):
            coord = self.parse_coord(string_var.get())
            if coord:
                self.coordinates[coord_key] = coord
                self.update_status(coord_key, coord)
                # 立即保存到文件
                self.save_coordinates()
        string_var.trace_add("write", on_coord_change)
        
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
        self.zhuanglu_tab_var.set(self.format_coord(self.coordinates.get("zhuanglu_tab", self.DEFAULT_COORDS["zhuanglu_tab"])))
        self.zhuanglu_export_var.set(self.format_coord(self.coordinates.get("zhuanglu_export_btn", self.DEFAULT_COORDS["zhuanglu_export_btn"])))
        
        # 轧制计划管理页面坐标
        self.zhizhi_tab_var.set(self.format_coord(self.coordinates.get("zhizhi_tab", self.DEFAULT_COORDS["zhizhi_tab"])))
        self.plan_select_var.set(self.format_coord(self.coordinates.get("plan_select", self.DEFAULT_COORDS["plan_select"])))
        self.zhizhi_export_var.set(self.format_coord(self.coordinates.get("zhizhi_export_btn", self.DEFAULT_COORDS["zhizhi_export_btn"])))
        
        # 计划明细导出坐标
        self.first_plan_var.set(self.format_coord(self.coordinates.get("first_plan", self.DEFAULT_COORDS["first_plan"])))
        self.plan_spacing_var.set(str(self.coordinates.get("plan_spacing", self.DEFAULT_COORDS["plan_spacing"])))
        self.first_plan_offset_var.set(str(self.coordinates.get("first_plan_offset", self.DEFAULT_COORDS["first_plan_offset"])))
        self.plan_detail_export_var.set(self.format_coord(self.coordinates.get("plan_detail_export", self.DEFAULT_COORDS["plan_detail_export"])))
        
        # 测试设置
        self.test_window_var.set(self.coordinates.get("test_window", self.DEFAULT_COORDS["test_window"]))
        self.export_speed_var.set(self.coordinates.get("export_speed", self.DEFAULT_COORDS["export_speed"]))
        self.show_warning_var.set(self.coordinates.get("show_operation_warning", self.DEFAULT_COORDS["show_operation_warning"]))
        self.auto_process_var.set(self.coordinates.get("auto_process_after_export", self.DEFAULT_COORDS["auto_process_after_export"]))
        self.auto_print_var.set(self.coordinates.get("auto_print_after_export", self.DEFAULT_COORDS["auto_print_after_export"]))
        self.debug_mode_var.set(self.coordinates.get("debug_mode", self.DEFAULT_COORDS["debug_mode"]))
        self.custom_window_var.set(self.coordinates.get("custom_window_title", self.DEFAULT_COORDS["custom_window_title"]))
        
        # 更新状态显示
        self.update_all_status()

    def on_warning_changed(self):
        """操作提示开关状态改变时的回调"""
        self.coordinates["show_operation_warning"] = self.show_warning_var.get()
        status = "启用" if self.show_warning_var.get() else "禁用"
        self.log(f"操作提示已{status}")
        
        # 立即更新到MainApp的coordinates中
        if self.main_app:
            self.main_app.coordinates.update({"show_operation_warning": self.show_warning_var.get()})
        
        # 立即保存到文件
        self.save_coordinates()
    
    def on_auto_process_changed(self):
        """自动处理开关状态改变时的回调"""
        self.coordinates["auto_process_after_export"] = self.auto_process_var.get()
        status = "启用" if self.auto_process_var.get() else "禁用"
        self.log(f"导出后自动处理已{status}")
        
        # 立即更新到MainApp的coordinates中
        if self.main_app:
            self.main_app.coordinates.update({"auto_process_after_export": self.auto_process_var.get()})
        
        # 立即保存到文件
        self.save_coordinates()
    
    def on_auto_print_changed(self):
        """自动打印开关状态改变时的回调"""
        self.coordinates["auto_print_after_export"] = self.auto_print_var.get()
        status = "启用" if self.auto_print_var.get() else "禁用"
        self.log(f"处理后自动打印已{status}")
        
        # 立即更新到MainApp的coordinates中
        if self.main_app:
            self.main_app.coordinates.update({"auto_print_after_export": self.auto_print_var.get()})
        
        # 立即保存到文件
        self.save_coordinates()
    
    def on_debug_mode_changed(self):
        """调试模式开关状态改变时的回调"""
        self.coordinates["debug_mode"] = self.debug_mode_var.get()
        status = "启用" if self.debug_mode_var.get() else "禁用"
        self.log(f"调试模式已{status}")
        
        # 立即更新到MainApp的coordinates中
        if self.main_app:
            self.main_app.coordinates.update({"debug_mode": self.debug_mode_var.get()})
        
        # 立即保存到文件
        self.save_coordinates()
    


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
            self.custom_messagebox("警告", f"{name} 未设置坐标，请先获取坐标")
            return

        if not PYAUTOGUI_AVAILABLE:
            self.custom_messagebox("错误", "pyautogui未安装")
            return

        # 直接使用设置中选择的窗口
        test_window = self.coordinates.get("test_window", "BGCMS1-宝钢股份多基地制造管理系统运行环境")

        # 确认测试
        if not self.custom_messagebox("确认测试", f"即将测试点击 {name}\n坐标: {coord}\n测试窗口: {test_window}\n\n是否继续？", msg_type='yesno'):
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

    def custom_messagebox(self, title, message, msg_type='info'):
        """自定义消息框"""
        import tkinter as tk
        from tkinter import ttk

        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.geometry("500x300")
        msg_window.resizable(True, True)

        # 计算居中位置
        screen_width = msg_window.winfo_screenwidth()
        screen_height = msg_window.winfo_screenheight()
        x = (screen_width // 2) - (500 // 2)
        y = (screen_height // 2) - (300 // 2)
        msg_window.geometry(f"500x300+{x}+{y}")

        msg_window.configure(bg='#f0f0f0')

        main_frame = tk.Frame(msg_window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        message_label = tk.Label(
            main_frame,
            text=message,
            font=('宋体', 12),
            bg='#f0f0f0',
            justify=tk.LEFT,
            wraplength=450
        )
        message_label.pack(expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(side=tk.BOTTOM, pady=20)

        if msg_type == 'yesno':
            user_choice = [False]

            def on_yes():
                user_choice[0] = True
                msg_window.destroy()

            def on_no():
                user_choice[0] = False
                msg_window.destroy()

            ttk.Button(btn_frame, text="是", command=on_yes, width=10).pack(side=tk.LEFT, padx=10)
            ttk.Button(btn_frame, text="否", command=on_no, width=10).pack(side=tk.LEFT, padx=10)

            msg_window.transient(self.root)
            msg_window.grab_set()
            msg_window.lift()
            msg_window.focus_force()
            msg_window.wait_window()

            return user_choice[0]
        else:
            ttk.Button(btn_frame, text="确定", command=msg_window.destroy, width=10).pack()

            msg_window.transient(self.root)
            msg_window.grab_set()
            msg_window.lift()
            msg_window.focus_force()
            msg_window.wait_window()

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
        # 保存自动打印设置
        self.coordinates["auto_print_after_export"] = self.auto_print_var.get()
        # 保存调试模式设置
        self.coordinates["debug_mode"] = self.debug_mode_var.get()
        # 保存自定义窗口名称
        self.coordinates["custom_window_title"] = self.custom_window_var.get().strip()
        
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
        """恢复默认值"""
        print("restore_defaults方法被调用")
        import tkinter.messagebox as messagebox
        if self.custom_messagebox("确认", "确定要恢复默认值吗？", msg_type='yesno'):
            print("用户确认恢复默认值")
            
            # 使用DEFAULT_COORDS中定义的默认值
            default_coords = self.DEFAULT_COORDS.copy()
            print(f"默认值: {default_coords}")
            
            # 直接更新UI变量
            self.zhuanglu_tab_var.set(self.format_coord(default_coords["zhuanglu_tab"]))
            self.zhuanglu_export_var.set(self.format_coord(default_coords["zhuanglu_export_btn"]))
            self.zhizhi_tab_var.set(self.format_coord(default_coords["zhizhi_tab"]))
            self.plan_select_var.set(self.format_coord(default_coords["plan_select"]))
            self.zhizhi_export_var.set(self.format_coord(default_coords["zhizhi_export_btn"]))
            self.first_plan_var.set(self.format_coord(default_coords["first_plan"]))
            self.plan_spacing_var.set(str(default_coords["plan_spacing"]))
            self.first_plan_offset_var.set(str(default_coords["first_plan_offset"]))
            self.plan_detail_export_var.set(self.format_coord(default_coords["plan_detail_export"]))
            self.test_window_var.set(default_coords["test_window"])
            self.export_speed_var.set(default_coords["export_speed"])
            self.show_warning_var.set(default_coords["show_operation_warning"])
            self.auto_process_var.set(default_coords["auto_process_after_export"])
            self.auto_print_var.set(default_coords["auto_print_after_export"])
            self.debug_mode_var.set(default_coords["debug_mode"])
            self.custom_window_var.set(default_coords["custom_window_title"])
            
            # 更新coordinates
            self.coordinates = default_coords
            print(f"已更新coordinates: {self.coordinates}")
            
            # 强制更新所有状态
            for key, value in default_coords.items():
                self.update_status(key, value)
            
            # 立即更新到MainApp
            if self.main_app:
                self.main_app.coordinates = default_coords
                print("已更新主程序坐标")
            
            # 保存到文件
            print(f"保存到文件: {self.config_file}")
            self.save_coordinates()
            print("保存完成")
            
            # 记录日志
            self.log("✓ 已恢复默认值")

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
                time.sleep(0.5)

            # 激活窗口 - 使用多种方法确保窗口被激活
            try:
                print("尝试激活窗口...")

                # 方法1: 显示窗口
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                time.sleep(0.2)

                # 方法2: 将窗口置于最顶层
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法3: 取消最顶层（恢复正常层级，但已经在前面了）
                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.2)

                # 方法4: 设置前台窗口
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.2)

                # 方法5: 设置活动窗口
                win32gui.SetActiveWindow(hwnd)
                time.sleep(0.2)

                # 方法6: 设置焦点
                win32gui.SetFocus(hwnd)
                time.sleep(0.3)

                # 方法7: 将窗口带到最前面
                win32gui.BringWindowToTop(hwnd)
                time.sleep(0.2)

                print("窗口激活成功")
                return True
            except Exception as e:
                print(f"激活窗口失败: {str(e)}")
                # 备用方案：使用pyautogui点击窗口
                if PYAUTOGUI_AVAILABLE:
                    print("使用pyautogui备用方案...")
                    try:
                        import pyautogui
                        # 获取窗口位置并点击
                        rect = win32gui.GetWindowRect(hwnd)
                        x = rect[0] + 10
                        y = rect[1] + 10
                        pyautogui.click(x, y)
                        time.sleep(0.5)
                        print("pyautogui备用方案执行成功")
                        return True
                    except Exception as e2:
                        print(f"pyautogui备用方案也失败: {str(e2)}")
                return False
        else:
            print(f"未找到窗口: {window_title}")
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
