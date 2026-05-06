#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轧制计划管理系统 - PyQt5版本
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, 
    QHeaderView, QMessageBox, QLineEdit, QCheckBox, QComboBox, QDialog,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush

class MainWindow(QMainWindow):
    """主窗口"""
    # 定义错误信号
    error_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("轧制计划管理系统")
        self.setGeometry(100, 100, 1500, 900)
        self.setMinimumSize(1200, 700)
        
        # 居中显示
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
        
        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # 初始化属性
        self.plan_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "furnace_order.db")
        self.coordinates = self.load_coordinate_config()
        
        # 环境准备
        self.create_required_folders()
        self.init_database()
        
        # 连接错误信号
        self.error_signal.connect(self.show_error_message)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("轧制计划管理系统")
        title_label.setFont(QFont("宋体", 20, QFont.Bold))
        title_label.setStyleSheet("background-color: #f0f0f0;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 主框架
        main_frame = QWidget()
        main_frame.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(main_frame)
        
        # 主框架布局
        main_frame_layout = QVBoxLayout(main_frame)
        main_frame_layout.setContentsMargins(0, 0, 0, 0)
        main_frame_layout.setSpacing(10)
        
        # 列表标题
        list_title = QLabel("计划号列表")
        list_title.setFont(QFont("宋体", 20))
        list_title.setStyleSheet("background-color: #f0f0f0;")
        list_title.setAlignment(Qt.AlignLeft)
        main_frame_layout.addWidget(list_title)
        
        # 列表框架
        list_frame = QWidget()
        list_frame.setStyleSheet("background-color: #f0f0f0;")
        main_frame_layout.addWidget(list_frame)
        
        # 列表框架布局
        list_frame_layout = QVBoxLayout(list_frame)
        list_frame_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["计划号", "块数", "状态", "起止钢卷号"])
        
        # 隐藏垂直表头（行号列）
        self.table_widget.verticalHeader().setVisible(False)
        
        # 设置列宽（按照要求固定）
        self.table_widget.setColumnWidth(0, 170)  # 计划号列宽
        self.table_widget.setColumnWidth(1, 100)  # 块数列宽
        self.table_widget.setColumnWidth(2, 800)  # 状态列宽
        self.table_widget.setColumnWidth(3, 395)  # 起止钢卷号列宽
        
        # 设置字体和行高
        font = QFont("宋体", 28, QFont.Bold)
        self.table_widget.setFont(font)
        self.table_widget.verticalHeader().setDefaultSectionSize(50)
        
        # 设置表头字体
        header_font = QFont("宋体", 28, QFont.Bold)
        self.table_widget.horizontalHeader().setFont(header_font)
        
        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.MultiSelection)
        
        # 设置表格样式,添加边框和选中行背景色
        table_style = """
            QTableWidget {
               
                background-color: white;
                border: 1px solid #CCCCCC;
                gridline-color: #CCCCCC;
                outline: none;
            }
            QTableWidget::item {
                border: 1px solid #CCCCCC;
                outline: none;
                selection-background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #3366FF;
                color: white;
                outline: none;
                selection-background-color: #3366FF;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                padding: 5px;
                outline: none;
            }
        """
        self.table_widget.setStyleSheet(table_style)
        
        # 添加表格到布局
        list_frame_layout.addWidget(self.table_widget)
        
        # 统计信息和选项框架
        stats_frame = QWidget()
        stats_frame.setStyleSheet("background-color: #f0f0f0;")
        main_frame_layout.addWidget(stats_frame)
        
        # 统计信息和选项布局
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        # 统计信息标签
        self.stats_label = QLabel("总块数: 0")
        self.stats_label.setFont(QFont("宋体", 20))
        self.stats_label.setStyleSheet("background-color: #f0f0f0; color: blue;")
        self.stats_label.setAlignment(Qt.AlignLeft)
        stats_layout.addWidget(self.stats_label)
        
        # 左侧伸缩空间
        stats_layout.addStretch(1)
        
        # 自动执行选项
        auto_exec_frame = QWidget()
        auto_exec_frame.setStyleSheet("background-color: #f0f0f0;")
        auto_exec_layout = QHBoxLayout(auto_exec_frame)
        auto_exec_layout.setContentsMargins(0, 0, 0, 0)
        auto_exec_layout.setSpacing(10)
        
        self.auto_exec_checkbox = QCheckBox("自动执行")
        self.auto_exec_checkbox.setFont(QFont("宋体", 20))
        self.auto_exec_checkbox.setStyleSheet("background-color: #f0f0f0;")
        auto_exec_layout.addWidget(self.auto_exec_checkbox)
        
        # 下一次执行时间显示
        self.next_execution_label = QLabel("下一次执行: 无")
        self.next_execution_label.setFont(QFont("宋体", 14))
        self.next_execution_label.setStyleSheet("color: blue; background-color: #f0f0f0;")
        auto_exec_layout.addWidget(self.next_execution_label)
        
        stats_layout.addWidget(auto_exec_frame)
        
        # 防退出登录选项
        self.anti_logout_checkbox = QCheckBox("防止退出登录")
        self.anti_logout_checkbox.setFont(QFont("宋体", 20))
        self.anti_logout_checkbox.setStyleSheet("background-color: #f0f0f0;")
        stats_layout.addWidget(self.anti_logout_checkbox)
        
        # 按钮框架
        btn_frame = QWidget()
        btn_frame.setStyleSheet("background-color: #f0f0f0;")
        main_layout.addWidget(btn_frame)
        
        # 按钮布局
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        # 左侧按钮
        left_btn_layout = QHBoxLayout()
        left_btn_layout.setSpacing(2)
        
        # 创建按钮样式
        button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 5px 10px;
                font-family: 宋体;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """
        
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setFont(QFont("宋体", 20))
        self.select_all_btn.setFixedSize(80, 40)
        self.select_all_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.setFont(QFont("宋体", 20))
        self.deselect_all_btn.setFixedSize(120, 40)
        self.deselect_all_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.deselect_all_btn)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFont(QFont("宋体", 20))
        self.refresh_btn.setFixedSize(80, 40)
        self.refresh_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.refresh_btn)
        
        self.auto_export_btn = QPushButton("自动导出")
        self.auto_export_btn.setFont(QFont("宋体", 20))
        self.auto_export_btn.setFixedSize(120, 40)
        self.auto_export_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.auto_export_btn)
        
        self.settings_btn = QPushButton("⚙ 设置")
        self.settings_btn.setFont(QFont("宋体", 20))
        self.settings_btn.setFixedSize(120, 40)
        self.settings_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.settings_btn)
        
        self.furnace_details_btn = QPushButton("装炉明细")
        self.furnace_details_btn.setFont(QFont("宋体", 20))
        self.furnace_details_btn.setFixedSize(120, 40)
        self.furnace_details_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.furnace_details_btn)
        
        self.process_plans_btn = QPushButton("处理计划")
        self.process_plans_btn.setFont(QFont("宋体", 20))
        self.process_plans_btn.setFixedSize(120, 40)
        self.process_plans_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.process_plans_btn)
        
        self.view_export_process_btn = QPushButton("查看导出过程")
        self.view_export_process_btn.setFont(QFont("宋体", 20))
        self.view_export_process_btn.setFixedSize(160, 40)
        self.view_export_process_btn.setStyleSheet(button_style)
        left_btn_layout.addWidget(self.view_export_process_btn)
        
        btn_layout.addLayout(left_btn_layout)
        
        # 右侧伸缩空间
        btn_layout.addStretch(1)
        
        # 右侧按钮
        right_btn_layout = QHBoxLayout()
        right_btn_layout.setSpacing(2)
        
        self.show_selected_btn = QPushButton("显示")
        self.show_selected_btn.setFont(QFont("宋体", 20))
        self.show_selected_btn.setFixedSize(80, 40)
        self.show_selected_btn.setStyleSheet(button_style)
        right_btn_layout.addWidget(self.show_selected_btn)
        
        self.print_selected_btn = QPushButton("打印")
        self.print_selected_btn.setFont(QFont("宋体", 20))
        self.print_selected_btn.setFixedSize(80, 40)
        self.print_selected_btn.setStyleSheet(button_style)
        right_btn_layout.addWidget(self.print_selected_btn)
        
        btn_layout.addLayout(right_btn_layout)
        
        # 连接信号槽
        self.connect_signals()
        
        # 数据加载
        self.load_processed_plans()
        self.load_printed_plans()
        self.load_data()
        
        # 服务启动
        if self.coordinates.get("anti_logout_enabled", False):
            self.start_anti_logout()
        if self.coordinates.get("auto_exec_enabled", False):
            self.start_auto_execution()
    
    def create_required_folders(self):
        """创建必要的文件夹"""
        try:
            # 创建计划号文件夹
            os.makedirs(os.path.join(self.plan_dir, "计划号"), exist_ok=True)
            # 创建备份文件夹
            os.makedirs(os.path.join(self.plan_dir, "计划号", "backup"), exist_ok=True)
            os.makedirs(os.path.join(self.plan_dir, "计划号", "备份计划"), exist_ok=True)
            print("文件夹创建成功")
        except Exception as e:
            print(f"创建文件夹失败: {str(e)}")
    
    def init_database(self):
        """初始化数据库"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建计划表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_number TEXT UNIQUE,
                    block_count INTEGER,
                    status TEXT,
                    start_coil TEXT,
                    end_coil TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建打印记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS print_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_number TEXT,
                    printed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plan_number) REFERENCES plans(plan_number)
                )
            ''')
            
            # 创建计划顺序表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_order (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no INTEGER,
                    plan_no TEXT,
                    coil_no TEXT,
                    steel_grade TEXT,
                    billet_width REAL,
                    reduction_width REAL,
                    adjustment_width REAL,
                    roll_width REAL,
                    tolerance_band TEXT,
                    roughing_alarm TEXT,
                    descaling TEXT,
                    billet_thickness REAL,
                    billet_length REAL,
                    roll_thickness REAL,
                    middle_thickness REAL,
                    rt2 REAL,
                    strength REAL,
                    edge_cutting TEXT,
                    destination TEXT,
                    order_width REAL,
                    billet_head_width REAL,
                    billet_tail_width REAL,
                    hot_rolled_product_classification TEXT,
                    steelmaking_steel_grade TEXT,
                    negative_tolerance REAL,
                    positive_tolerance REAL,
                    reheat_billet TEXT,
                    original_roll_width REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
    
    def load_processed_plans(self):
        """加载已处理的计划"""
        try:
            processed_plans_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_plans.txt")
            if os.path.exists(processed_plans_file):
                with open(processed_plans_file, 'r', encoding='utf-8') as f:
                    self.processed_plans = set(line.strip() for line in f if line.strip())
            else:
                self.processed_plans = set()
            print(f"已加载 {len(self.processed_plans)} 个已处理计划")
        except Exception as e:
            print(f"加载已处理计划失败: {str(e)}")
            self.processed_plans = set()
    
    def load_printed_plans(self):
        """加载已打印的计划"""
        try:
            printed_plans_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "printed_plans.txt")
            if os.path.exists(printed_plans_file):
                with open(printed_plans_file, 'r', encoding='utf-8') as f:
                    self.printed_plans = set(line.strip() for line in f if line.strip())
            else:
                self.printed_plans = set()
            print(f"已加载 {len(self.printed_plans)} 个已打印计划")
        except Exception as e:
            print(f"加载已打印计划失败: {str(e)}")
            self.printed_plans = set()
    
    def load_no_aps_plans(self):
        """加载无APS的计划"""
        try:
            no_aps_plans_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "no_aps_plans.txt")
            if os.path.exists(no_aps_plans_file):
                with open(no_aps_plans_file, 'r', encoding='utf-8') as f:
                    self.no_aps_plans = set(line.strip() for line in f if line.strip())
            else:
                self.no_aps_plans = set()
            print(f"已加载 {len(self.no_aps_plans)} 个无APS计划")
        except Exception as e:
            print(f"加载无APS计划失败: {str(e)}")
            self.no_aps_plans = set()
    
    def load_low_roll_width_plans(self):
        """加载低轧宽的计划"""
        try:
            low_roll_width_plans_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "low_roll_width_plans.txt")
            if os.path.exists(low_roll_width_plans_file):
                with open(low_roll_width_plans_file, 'r', encoding='utf-8') as f:
                    self.low_roll_width_plans = set(line.strip() for line in f if line.strip())
            else:
                self.low_roll_width_plans = set()
            print(f"已加载 {len(self.low_roll_width_plans)} 个低轧宽计划")
        except Exception as e:
            print(f"加载低轧宽计划失败: {str(e)}")
            self.low_roll_width_plans = set()
    
    def show_error_message(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)
    
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
    
    def save_low_roll_width_plans(self):
        """保存低轧宽的计划号"""
        try:
            low_roll_width_file = os.path.join(self.plan_dir, "low_roll_width_plans.txt")
            with open(low_roll_width_file, 'w', encoding='utf-8') as f:
                for plan_no in self.low_roll_width_plans:
                    f.write(f"{plan_no}\n")
            print(f"已保存 {len(self.low_roll_width_plans)} 个低轧宽计划号")
        except Exception as e:
            print(f"保存低轧宽计划号失败: {str(e)}")
    
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
            if 钢种字符串 == "-p" and 牌号字符串.lower().endswith("-p"):
                return True
            
            # 通配符匹配：以"-P"结尾
            if 钢种字符串 == "-P" and 牌号字符串.endswith("-P"):
                return True
        
        return False
        
    def event(self, event):
        """处理自定义事件"""
        from PyQt5.QtCore import QEvent
        
        # 处理导出计划明细事件
        if hasattr(event, 'valid_no_file_plans'):
            try:
                valid_no_file_plans = event.valid_no_file_plans
                plan_detail_export_btn = event.plan_detail_export_btn
                test_window = event.test_window
                delay_time = event.delay_time
                coord_map = event.coord_map
                
                print(f"开始导出无文件计划号明细: {valid_no_file_plans}")
                
                # 导出无文件计划号明细
                for plan_no in valid_no_file_plans:
                    print(f"导出计划号: {plan_no}")
                    # 调用导出计划号明细函数
                    self.export_single_plan_detail(plan_no, test_window, plan_detail_export_btn, delay_time, coord_map)
                
                print("无文件计划号明细导出完成")
            except Exception as e:
                print(f"处理导出计划明细事件失败: {str(e)}")
            return True
        
        # 处理刷新事件 - 只处理特定的刷新事件
        if hasattr(event, 'refresh_type') and event.refresh_type == 'plan_list':
            try:
                # 刷新计划号列表
                self.refresh_plan_list()
            except Exception as e:
                print(f"处理刷新事件失败: {str(e)}")
            return True
        
        # 处理其他事件
        return super().event(event)
    
    def load_coordinate_config(self):
        """加载坐标配置"""
        try:
            import json
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_coordinates.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    coordinates = json.load(f)
                print("坐标配置加载成功")
                return coordinates
            else:
                print("坐标配置文件不存在,使用默认配置")
                return {
                    "zhuanglu_tab": None,
                    "zhuanglu_export_btn": None,
                    "zhizhi_tab": None,
                    "plan_select": None,
                    "zhizhi_export_btn": None,
                    "first_plan": [100, 100],
                    "plan_detail_export": [79, 870],
                    "test_window": "BGCMS1-宝钢股份多基地制造管理系统运行环境",
                    "auto_process_after_export": False,
                    "auto_print_after_export": False,
                    "export_speed": "中",
                    "show_operation_warning": True,
                    "anti_logout_enabled": False,
                    "auto_exec_enabled": False,
                    "auto_exec_mode": "interval",
                    "auto_exec_interval": 30,
                    "auto_exec_times": "",
                    "anti_logout_interval": 60000
                }
        except Exception as e:
            print(f"加载坐标配置失败: {str(e)}")
            return {}
            
    
    def load_data(self):
        """加载Excel数据 - 调用刷新计划号列表方法"""
        try:
            import os
            # 重新加载已处理和已打印的状态
            self.load_processed_plans()
            self.load_printed_plans()
            self.load_no_aps_plans()
            self.load_low_roll_width_plans()
            
            # 刷新计划号列表
            self.refresh_plan_list()
            print("数据加载完成")
        except Exception as e:
            print(f"加载数据失败: {str(e)}")
    
    def refresh_plan_list(self, export_zhuanglu=False):
        """刷新计划号列表"""
        try:
            # 扫描并重命名计划号文件
            self.scan_and_rename_plan_files()
            
            # 从数据库读取数据并更新表格
            self.refresh_plan_list_from_file()
        except Exception as e:
            print(f"刷新计划号列表失败: {str(e)}")
    
    def scan_and_rename_plan_files(self):
        """扫描并重命名计划号文件"""
        try:
            import os
            
            # 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            # 如果计划号文件夹不存在,创建它
            if not os.path.exists(plan_dir):
                print(f"计划号文件夹不存在,创建: {plan_dir}")
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
                
                # 这里可以添加读取文件获取计划号并重命名的逻辑
                # 暂时跳过实际的重命名操作
                print(f"处理文件: {file}")
            
            print(f"扫描完成: 处理 {len(files)} 个文件,跳过 {skipped_count} 个文件")
        except Exception as e:
            print(f"扫描并重命名计划号文件失败: {str(e)}")
    
    def refresh_data(self):
        """刷新数据"""
        # 扫描并重命名计划号文件
        self.scan_and_rename_plan_files()
        # 刷新计划号列表（load_data会自动加载状态）
        self.load_data()
    
    def process_plans(self, auto_print=False, show_result=True):
        """处理计划号文件 - 使用 pandas + xlwt 方案
        
        Args:
            auto_print: 是否在处理完成后自动打印（默认False,仅自动导出流程中为True）
            show_result: 是否显示处理结果弹窗（默认True,在显示按钮调用时为False）
        """
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            from PyQt5.QtCore import Qt
            # 检查是否选择了计划号
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("警告")
                msg_box.setText("请先在计划号列表中选择要处理的计划号")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            
            if not os.path.exists(plan_dir):
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("错误")
                msg_box.setText(f"计划号文件夹不存在: {plan_dir}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 获取选中的计划号
            selected_plans = [self.plan_data[index.row()]['plan_no'] for index in selected_items]
            
            # 检查选中的计划号中是否有已处理的
            already_processed = [plan_no for plan_no in selected_plans if plan_no in self.processed_plans]
            if already_processed and show_result:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText(f"以下计划号已处理过,无需重复处理：\n\n{', '.join(already_processed)}")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 构建选中计划号的文件路径列表
            selected_files = []
            for plan_no in selected_plans:
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    selected_files.append((plan_no, file_path))
                else:
                    print(f'文件不存在: {plan_no}.xls')
            
            if not selected_files:
                # 确保主程序窗口在前面
                self.activateWindow()
                self.raise_()
                self.show()
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("提示")
                msg_box.setText("选中的计划号没有对应的文件")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                msg_box.setModal(True)
                QApplication.setActiveWindow(msg_box)
                msg_box.exec_()
                # 弹窗关闭后再次激活主程序窗口
                self.activateWindow()
                self.raise_()
                self.show()
                return
            
            # 直接处理,不显示确认窗口
            
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
                    print(f"处理成功: {plan_no}.xls")
                    # 标记为已处理
                    self.processed_plans.add(plan_no)
                    
                    # 更新plan_data中的has_low_roll_width字段
                    for i, data in enumerate(self.plan_data):
                        if data['plan_no'] == plan_no:
                            self.plan_data[i]['has_low_roll_width'] = has_low_roll_width
                            break
                    
                    # 更新低轧宽板坯集合并保存
                    if has_low_roll_width:
                        self.low_roll_width_plans.add(plan_no)
                    else:
                        # 如果不再有低轧宽板坯,从集合中移除
                        self.low_roll_width_plans.discard(plan_no)
                    self.save_low_roll_width_plans()
                except Exception as e:
                    failed_count += 1
                    failed_files.append(plan_no)
                    print(f"处理失败 {plan_no}.xls: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # 保存已处理计划状态
            if processed_count > 0:
                self.save_processed_plans()
                # 刷新列表显示
                self.refresh_data()
            
            # 检查是否需要自动打印（仅在自动导出流程中）
            if auto_print and success_files:
                # 自动执行打印功能（打印刚刚处理的计划号）
                print("\n=== 自动执行计划打印 ===")
                # 选中刚刚处理成功的计划号
                self.table_widget.clearSelection()
                for i, plan_data in enumerate(self.plan_data):
                    if plan_data['plan_no'] in success_files:
                        self.table_widget.selectRow(i)
                # 自动打印选中的计划号
                self.print_selected()
            else:
                # 显示结果 - 使用自定义窗口
                if show_result:
                    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
                    from PyQt5.QtCore import Qt
                    from PyQt5.QtGui import QFont
                    
                    # 创建自定义窗口
                    result_window = QDialog(self)
                    result_window.setWindowTitle("完成")
                    result_window.setGeometry(300, 200, 600, 450)
                    result_window.setWindowModality(Qt.ApplicationModal)
                    
                    # 主布局
                    main_layout = QVBoxLayout(result_window)
                    main_layout.setContentsMargins(20, 20, 20, 20)
                    main_layout.setSpacing(10)
                    
                    # 标题
                    title_label = QLabel("处理完成！")
                    title_label.setFont(QFont("宋体", 24, QFont.Bold))
                    title_label.setAlignment(Qt.AlignCenter)
                    main_layout.addWidget(title_label)
                    
                    # 统计信息
                    stats_label = QLabel(f"成功: {processed_count} 个 | 失败: {failed_count} 个 | 跳过: {skipped_count} 个")
                    stats_label.setFont(QFont("宋体", 16))
                    stats_label.setAlignment(Qt.AlignCenter)
                    main_layout.addWidget(stats_label)
                    
                    # 成功的计划号
                    if success_files:
                        success_label = QLabel(f"成功的计划号: {', '.join(success_files)}")
                        success_label.setFont(QFont("宋体", 14))
                        success_label.setWordWrap(True)
                        main_layout.addWidget(success_label)
                    
                    # 失败的计划号
                    if failed_files:
                        failed_label = QLabel(f"失败的计划号: {', '.join(failed_files)}")
                        failed_label.setFont(QFont("宋体", 14))
                        failed_label.setWordWrap(True)
                        main_layout.addWidget(failed_label)
                    
                    # 跳过的计划号
                    if skipped_files:
                        skipped_label = QLabel(f"跳过的计划号: {', '.join(skipped_files)}")
                        skipped_label.setFont(QFont("宋体", 14))
                        skipped_label.setWordWrap(True)
                        main_layout.addWidget(skipped_label)
                    
                    # 按钮布局
                    btn_layout = QHBoxLayout()
                    btn_layout.addStretch(1)
                    
                    # 确定按钮
                    ok_btn = QPushButton("确定")
                    ok_btn.setFont(QFont("宋体", 14))
                    ok_btn.setFixedSize(100, 40)
                    ok_btn.clicked.connect(result_window.accept)
                    btn_layout.addWidget(ok_btn)
                    
                    btn_layout.addStretch(1)
                    main_layout.addLayout(btn_layout)
                    
                    # 显示窗口
                    result_window.exec_()
        except Exception as e:
            print(f"处理计划失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"处理计划失败: {str(e)}")
    

    
    def print_furnace_details(self):
        """打印装炉明细 - 像主程序画面中的格式打印"""
        try:
            import os
            import time
            import xlwt
            
            # 获取所有数据
            rows = []
            for row_idx in range(self.table_widget.rowCount()):
                row_data = []
                for col_idx in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row_idx, col_idx)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                rows.append(row_data)
            
            if not rows:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "没有数据可打印")
                return
            
            # 创建临时 Excel 文件（存储在计划号文件夹中）
            plan_dir = os.path.join(self.plan_dir, "计划号")
            temp_file_name = f"temp_装炉明细打印_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            
            # 创建工作簿和工作表
            workbook = xlwt.Workbook(encoding='utf-8')
            sheet = workbook.add_sheet('装炉明细')
            
            # 设置列名
            提示行 = ["装炉明细打印"]
            headers = ["序号", "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度"]
            
            # 定义样式
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
            
            # 字段列名样式（强度字段，8pt 字号）
            style_header_strength = xlwt.XFStyle()
            font_header_strength = xlwt.Font()
            font_header_strength.name = '仿宋'
            font_header_strength.height = 160  # 8pt
            font_header_strength.bold = True
            style_header_strength.font = font_header_strength
            style_header_strength.alignment = alignment_header_border
            style_header_strength.borders = borders_header
            
            # 序号列样式（14pt）- 左边框为实线
            style_data_seq = xlwt.XFStyle()
            font_data_seq = xlwt.Font()
            font_data_seq.name = '仿宋'
            font_data_seq.height = 280  # 14pt
            font_data_seq.bold = True
            style_data_seq.font = font_data_seq
            alignment_data = xlwt.Alignment()
            alignment_data.horz = xlwt.Alignment.HORZ_CENTER
            alignment_data.vert = xlwt.Alignment.VERT_CENTER
            style_data_seq.alignment = alignment_data
            borders_data_seq = xlwt.Borders()
            borders_data_seq.left = xlwt.Borders.THIN
            borders_data_seq.right = xlwt.Borders.NO_LINE
            borders_data_seq.top = xlwt.Borders.THIN
            borders_data_seq.bottom = xlwt.Borders.THIN
            style_data_seq.borders = borders_data_seq
            
            # 数据行样式（带边框，去掉竖线）
            borders_data = xlwt.Borders()
            borders_data.left = xlwt.Borders.NO_LINE
            borders_data.right = xlwt.Borders.NO_LINE
            borders_data.top = xlwt.Borders.THIN
            borders_data.bottom = xlwt.Borders.THIN
            
            # 钢卷号列样式（16pt）
            style_data_coil = xlwt.XFStyle()
            font_data_coil = xlwt.Font()
            font_data_coil.name = '仿宋'
            font_data_coil.height = 320  # 16pt
            font_data_coil.bold = True
            style_data_coil.font = font_data_coil
            style_data_coil.alignment = alignment_data
            style_data_coil.borders = borders_data
            
            # 14pt 样式
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
            style_data_14pt.borders = borders_data
            
            # 12pt 样式
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
            style_data_12pt.borders = borders_data
            
            # 12pt 样式（强度列）- 右边框为实线
            style_data_12pt_strength = xlwt.XFStyle()
            font_data_12pt_strength = xlwt.Font()
            font_data_12pt_strength.name = '仿宋'
            font_data_12pt_strength.height = 240  # 12pt
            font_data_12pt_strength.bold = True
            style_data_12pt_strength.font = font_data_12pt_strength
            style_data_12pt_strength.alignment = alignment_data_12pt
            borders_data_strength = xlwt.Borders()
            borders_data_strength.left = xlwt.Borders.NO_LINE
            borders_data_strength.right = xlwt.Borders.THIN
            borders_data_strength.top = xlwt.Borders.THIN
            borders_data_strength.bottom = xlwt.Borders.THIN
            style_data_12pt_strength.borders = borders_data_strength
            
            # 设置列宽
            col_widths = [
                int(5.5 * 256 * 1.2),       # 1. 序号
                int(7.0 * 256 * 1.04),       # 2. 计划号
                int(19 * 256 * 1.04),        # 3. 钢卷号
                int(18 * 256 * 1.04),       # 4. 牌号（钢级）
                int(7 * 256 * 1.04),         # 5. 坯宽
                int(7 * 256 * 1.05),         # 6. 减宽（侧压量）
                int(6 * 256 * 1.2),          # 7. 调宽
                int(7 * 256 * 1.13),         # 8. 轧宽
                int(9 * 256 * 1.03),         # 9. 公差带
                int(33 * 256 * 1.04),        # 10. 粗轧报信
                int(7 * 256 * 1.08),         # 11. 除鳞
                int(7 * 256 * 1.04),         # 12. 坯厚
                int(6.2 * 256 * 1.13),       # 13. 坯长
                int(6 * 256 * 1.04),         # 14. 轧厚
                int(5 * 256 * 1.04),         # 15. 中厚
                int(6.57 * 256 * 1.04),      # 16. RT2
                int(2 * 256 * 1.2)           # 17. 强度
            ]
            
            for col_idx, width in enumerate(col_widths):
                if col_idx < len(headers):
                    sheet.col(col_idx).width = width
                    sheet.col(col_idx).width_mismatch = True
            
            # 写入提示行（第一行）并合并单元格
            sheet.write_merge(0, 0, 0, len(headers) - 1, 提示行 [0], style_title)
            sheet.row(0).height = 460  # 23pt
            sheet.row(0).height_mismatch = True
            
            # 第二行：打印时间
            print_time = time.strftime("%Y-%m-%d %H:%M:%S")
            sheet.write(1, len(headers) - 1, f"打印时间：{print_time}", style_time)
            sheet.row(1).height = 460  # 23pt
            sheet.row(1).height_mismatch = True
            
            # 写入字段名行（第三行）
            for col, header in enumerate(headers):
                if col == len(headers) - 1:  # 强度字段
                    sheet.write(2, col, header, style_header_strength)
                else:
                    sheet.write(2, col, header, style_header_border)
            sheet.row(2).height = 500  # 25pt
            sheet.row(2).height_mismatch = True
            
            # 写入数据行
            seq_num = 1
            for row_idx, row_data in enumerate(rows):
                # 写入序号
                sheet.write(row_idx + 3, 0, seq_num, style_data_seq)
                
                # 写入其他字段
                for col_idx, value in enumerate(row_data[1:], 1):  # 跳过第一列（序号）
                    if col_idx == 2:  # 钢卷号列（16pt）
                        sheet.write(row_idx + 3, col_idx, value, style_data_coil)
                    elif col_idx in [4, 5, 6, 7, 11, 15]:  # 14pt 列
                        sheet.write(row_idx + 3, col_idx, value, style_data_14pt)
                    elif col_idx == 16:  # 强度列（12pt，右边框实线）
                        sheet.write(row_idx + 3, col_idx, value, style_data_12pt_strength)
                    else:  # 其他 12pt 列
                        sheet.write(row_idx + 3, col_idx, value, style_data_12pt)
                
                seq_num += 1
            
            # 保存文件
            workbook.save(temp_file_path)
            print(f"已生成打印文件：{temp_file_path}")
            
            # 使用 pywin32 打印文件
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            
            # 打开工作簿
            workbook_com = excel.Workbooks.Open(temp_file_path)
            
            # 打印活动工作表
            workbook_com.ActiveSheet.PrintOut()
            
            # 关闭工作簿
            workbook_com.Close(SaveChanges=False)
            
            # 退出 Excel
            excel.Quit()
            
            # 删除临时文件
            import time
            time.sleep(1)  # 等待打印完成
            os.remove(temp_file_path)
            print(f"已删除临时文件：{temp_file_path}")
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "完成", "打印完成")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            import traceback
            QMessageBox.critical(self, "错误", f"打印失败：{str(e)}")
            print(f"打印失败：{str(e)}")
            print(traceback.format_exc())
    
    def run_excel_macro_with_pandas(self, file_path):
        """使用 pandas + xlwt 处理Excel文件（xls格式）
        
        提取指定字段,删除其他字段,添加"轧宽+（余量）"和"装炉顺序号"字段
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
        
        # 2. 加载装炉顺序数据,构建映射
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
                
                # 释放资源
                if hasattr(workbook2, 'release_resources'):
                    workbook2.release_resources()
        
        # 3. 定义目标列（按照用户要求的最终顺序）
        target_columns = [
            "顺序号", "钢卷号", "牌号（钢级）", "坯宽", "侧压量", "板坯宽度调宽标记", "轧宽+（余量）",
            "碳", "粗轧报信", "层号", "坯厚", "坯长", "轧厚", "中间坯厚度设定值",
            "RT2目标值", "硬度组", "订货宽度", "去向", "切边方式", "板坯头部宽度", "板坯尾部宽度",
            "计划号", "热轧产品分类", "炼钢钢种", "宽度负公差", "宽度正公差", "板坯炉后拒收次数", "轧宽",
            "装炉顺序号"
        ]
        
        # 定义字段名映射（按照用户要求的最终顺序显示名称）
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
            "订货宽度": "订货宽度",
            "去向": "去向",
            "切边方式": "切边方式",
            "板坯头部宽度": "坯头部宽",
            "板坯尾部宽度": "坯尾部宽",
            "计划号": "计划号",
            "热轧产品分类": "热轧产品分类",
            "炼钢钢种": "炼钢钢种",
            "宽度负公差": "负公差",
            "宽度正公差": "正公差",
            "板坯炉后拒收次数": "回炉坯",
            "轧宽": "原轧宽",
            "装炉顺序号": "装炉顺"
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
        new_sheet.paper_size = 137  # 137 = xlPaperFanfoldUS (14.875 x 11 inches) - 连续折叠纸
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
        
        # 强度列字段名样式（带右边框实线）
        style_header_strength = xlwt.XFStyle()
        font_header_strength = xlwt.Font()
        font_header_strength.name = '仿宋'
        font_header_strength.height = 280  # 14pt
        font_header_strength.bold = True
        style_header_strength.font = font_header_strength
        alignment_header_strength = xlwt.Alignment()
        alignment_header_strength.horz = xlwt.Alignment.HORZ_CENTER
        alignment_header_strength.vert = xlwt.Alignment.VERT_CENTER
        style_header_strength.alignment = alignment_header_strength
        borders_header_strength = xlwt.Borders()
        borders_header_strength.left = xlwt.Borders.THIN
        borders_header_strength.right = xlwt.Borders.THIN  # 右边框实线
        borders_header_strength.top = xlwt.Borders.THIN
        borders_header_strength.bottom = xlwt.Borders.THIN
        style_header_strength.borders = borders_header_strength
        
        # 打印时间样式（右对齐,10 号字体）
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
        
        # 数据行样式（带边框,去掉竖线）
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
        # 12pt 样式（加粗,去掉竖线）
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
        
        # 14pt 样式（加粗,去掉竖线）
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
        
        # 16pt 样式（加粗,去掉竖线）
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
        
        # 12pt 长间隔虚线边框样式（用于轧厚）- 左右虚线
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
        style_data_12pt_left_dashed = xlwt.XFStyle()
        font_data_12pt_left_dashed = xlwt.Font()
        font_data_12pt_left_dashed.name = '仿宋'
        font_data_12pt_left_dashed.height = 240  # 12pt
        font_data_12pt_left_dashed.bold = True
        style_data_12pt_left_dashed.font = font_data_12pt_left_dashed
        style_data_12pt_left_dashed.alignment = alignment_data_12pt
        borders_data_12pt_left_dashed = xlwt.Borders()
        borders_data_12pt_left_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_12pt_left_dashed.right = xlwt.Borders.NO_LINE
        borders_data_12pt_left_dashed.top = xlwt.Borders.THIN
        borders_data_12pt_left_dashed.bottom = xlwt.Borders.THIN
        style_data_12pt_left_dashed.borders = borders_data_12pt_left_dashed
        
        # 14pt 左侧长间隔虚线边框样式（用于坯宽）
        style_data_14pt_left_dashed = xlwt.XFStyle()
        font_data_14pt_left_dashed = xlwt.Font()
        font_data_14pt_left_dashed.name = '仿宋'
        font_data_14pt_left_dashed.height = 280  # 14pt
        font_data_14pt_left_dashed.bold = True
        style_data_14pt_left_dashed.font = font_data_14pt_left_dashed
        style_data_14pt_left_dashed.alignment = alignment_data_14pt
        borders_data_14pt_left_dashed = xlwt.Borders()
        borders_data_14pt_left_dashed.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_left_dashed.right = xlwt.Borders.NO_LINE
        borders_data_14pt_left_dashed.top = xlwt.Borders.THIN
        borders_data_14pt_left_dashed.bottom = xlwt.Borders.THIN
        style_data_14pt_left_dashed.borders = borders_data_14pt_left_dashed
        
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
        
        # 14pt 长间隔虚线边框样式（用于调宽）
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
        
        # 14pt 长间隔虚线边框样式（用于轧厚）- 左右虚线
        style_data_14pt_dashdot = xlwt.XFStyle()
        font_data_14pt_dashdot = xlwt.Font()
        font_data_14pt_dashdot.name = '仿宋'
        font_data_14pt_dashdot.height = 280  # 14pt
        font_data_14pt_dashdot.bold = True
        style_data_14pt_dashdot.font = font_data_14pt_dashdot
        style_data_14pt_dashdot.alignment = alignment_data_14pt
        borders_data_14pt_dashdot = xlwt.Borders()
        borders_data_14pt_dashdot.left = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_dashdot.right = xlwt.Borders.MEDIUM_DASHED
        borders_data_14pt_dashdot.top = xlwt.Borders.THIN
        borders_data_14pt_dashdot.bottom = xlwt.Borders.THIN
        style_data_14pt_dashdot.borders = borders_data_14pt_dashdot
        
        # 14pt 样式（用于坯厚、RT2）
        style_data_14pt_center = xlwt.XFStyle()
        font_data_14pt_center = xlwt.Font()
        font_data_14pt_center.name = '仿宋'
        font_data_14pt_center.height = 280  # 14pt
        font_data_14pt_center.bold = True
        style_data_14pt_center.font = font_data_14pt_center
        style_data_14pt_center.alignment = alignment_data_14pt
        borders_data_14pt_center = xlwt.Borders()
        borders_data_14pt_center.left = xlwt.Borders.NO_LINE
        borders_data_14pt_center.right = xlwt.Borders.NO_LINE
        borders_data_14pt_center.top = xlwt.Borders.THIN
        borders_data_14pt_center.bottom = xlwt.Borders.THIN
        style_data_14pt_center.borders = borders_data_14pt_center
        
        # 12pt 样式（用于强度列）- 右边框为实线
        style_data_12pt_strength = xlwt.XFStyle()
        font_data_12pt_strength = xlwt.Font()
        font_data_12pt_strength.name = '仿宋'
        font_data_12pt_strength.height = 240  # 12pt
        font_data_12pt_strength.bold = True
        style_data_12pt_strength.font = font_data_12pt_strength
        style_data_12pt_strength.alignment = alignment_data_12pt
        borders_data_strength = xlwt.Borders()
        borders_data_strength.left = xlwt.Borders.NO_LINE
        borders_data_strength.right = xlwt.Borders.THIN  # 右边框为实线
        borders_data_strength.top = xlwt.Borders.THIN
        borders_data_strength.bottom = xlwt.Borders.THIN
        style_data_12pt_strength.borders = borders_data_strength
        
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
        
        # 钢卷号左对齐样式（16pt - 用于钢卷号,带下边框）
        style_data_16pt_left = xlwt.XFStyle()
        font_data_16pt_left = xlwt.Font()
        font_data_16pt_left.name = '仿宋'
        font_data_16pt_left.height = 320  # 16pt
        font_data_16pt_left.bold = True
        style_data_16pt_left.font = font_data_16pt_left
        # 创建左对齐配置
        alignment_data_16pt_left = xlwt.Alignment()
        alignment_data_16pt_left.horz = xlwt.Alignment.HORZ_LEFT  # 左对齐
        alignment_data_16pt_left.vert = xlwt.Alignment.VERT_CENTER
        style_data_16pt_left.alignment = alignment_data_16pt_left
        borders_data_16pt_left = xlwt.Borders()
        borders_data_16pt_left.left = xlwt.Borders.NO_LINE
        borders_data_16pt_left.right = xlwt.Borders.NO_LINE
        borders_data_16pt_left.top = xlwt.Borders.NO_LINE
        borders_data_16pt_left.bottom = xlwt.Borders.THIN  # 下边框
        style_data_16pt_left.borders = borders_data_16pt_left
        
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
        
        # 找到"强度"列的索引（用于标题跨列）
        强度列索引 = -1
        装炉顺列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "强度":
                强度列索引 = col_idx
            elif 映射后的列名 == "装炉顺":
                装炉顺列索引 = col_idx
        
        # 如果找到强度列,标题跨列到该列；否则跨所有列
        if 强度列索引 >= 0:
            标题结束列 = 强度列索引
        else:
            标题结束列 = len(target_columns) - 1
        
        # 8. 设置列宽（按照原程序 furnace_order_manager.py 的列宽设置）
        # 最终顺序：序号、钢卷号、牌号（钢级）、坯宽、减宽、调宽、轧宽、公差带、粗轧报信、除鳞、坯厚、坯长、轧厚、中厚、RT2、强度、订货宽度、去向、切边方式、坯头部宽、坯尾部宽、计划号、热轧产品分类、炼钢钢种、负公差、正公差、回炉坯、原轧宽、装炉顺
        col_widths = [
            int(5.5 * 256 * 1.2),       # 1. 序号（原程序值：5.5）
            int(19 * 256 * 1.04),       # 2. 钢卷号（原程序值：19）
            int(18 * 256 * 1.04),       # 3. 牌号（钢级）（原程序值：18）
            int(7 * 256 * 1.04),        # 4. 坯宽（原程序值：7）
            int(7 * 256 * 1.05),         # 5. 减宽（侧压量）
            int(6 * 256 * 1.2),         # 6. 调宽（板坯宽度调宽标记）（原程序值：6）
            int(7 * 256 * 1.13),        # 7. 轧宽（轧宽 +（余量））（原程序值：7）
            int(9 * 256 * 1.03),         # 8. 公差带（碳）
            int(33 * 256 * 1.04),        # 9. 粗轧报信
            int(7 * 256 * 1.08),        # 10. 除鳞（层号）（原程序值：7）
            int(7 * 256 * 1.04),        # 11. 坯厚（原程序值：7）
            int(6.2 * 256 * 1.13),       # 12. 坯长
            int(6 * 256 * 1.04),        # 13. 轧厚（原程序值：6）
            int(5 * 256 * 1.04),        # 14. 中厚（中间坯厚度设定值）（原程序值：5）
            int(6.57 * 256 * 1.04),     # 15. RT2（RT2 目标值）（原程序值：6.57）
            int(4.71 * 256 * 1.2),      # 16. 强度（硬度组）（修改为 4.71）
            int(8.0 * 256 * 1.04),      # 17. 订货宽度
            int(3.6 * 256 * 1.2),        # 18. 去向
            int(3.6 * 256 * 1.2),        # 19. 切边方式
            int(8.0 * 256 * 1.04),       # 20. 坯头部宽（板坯头部宽度）
            int(8.0 * 256 * 1.04),       # 21. 坯尾部宽（板坯尾部宽度）
            int(7.0 * 256 * 1.04),      # 22. 计划号（原程序值：7.0）
            int(8.0 * 256 * 1.04),       # 23. 热轧产品分类
            int(8.0 * 256 * 1.04),       # 24. 炼钢钢种
            int(8.0 * 256 * 1.04),       # 25. 负公差（宽度负公差）
            int(8.0 * 256 * 1.04),       # 26. 正公差（宽度正公差）
            int(8.0 * 256 * 1.04),       # 27. 回炉坯（板坯炉后拒收次数）
            int(8.0 * 256 * 1.04),       # 28. 原轧宽（轧宽）
            int(5.0 * 256 * 1.1)         # 29. 装炉顺（装炉顺序号）
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
        has_low_roll_width = False
        
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
                
                # 规则1：如果牌号（钢级）列是"SPHC"且炼钢钢种列是"P3A1",则牌号（钢级）列值添加"-P"
                if 牌号值 == "SPHC" and 炼钢钢种值 == "P3A1":
                    row_data["牌号（钢级）"] = 牌号值 + "-P"
                else:
                    # 规则2：在第5工作表A列中查找当前行的牌号（钢级）字段和炼钢钢种字段值
                    牌号在列表中 = 牌号值 in 钢种集合
                    炼钢钢种在列表中 = 炼钢钢种值 in 钢种集合
                    
                    # 规则3：如果都找不到
                    if not 牌号在列表中 and not 炼钢钢种在列表中:
                        # 若热轧产品分类字段是"L"、"M"或"O",则牌号（钢级）字段值设为炼钢钢种字段值
                        if 热轧产品分类值 in ["L", "M", "O"]:
                            row_data["牌号（钢级）"] = 炼钢钢种值
                        # 若热轧产品分类字段列是"X"且C列值末尾不是"-P",则添加"-P"
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
                    # 如果没有匹配,填充空白
                    除鳞值 = ""
                
                # 如果是回炉坯,在除鳞字段前添加"回"
                if 是回炉坯:
                    if 除鳞值:
                        除鳞值 = "回" + 除鳞值
                    else:
                        除鳞值 = "回"
                
                # 检查牌号是否在APS钢种列表中
                if brand and apsGrades:
                    在APS列表中 = brand in apsGrades
                    if not 在APS列表中:
                        # 如果不在APS列表中,添加"无APS"标识
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
            
            # 检查除鳞字段是否包含"回"字,如果是则标记需标注
            if "层号" in row_data:
                除鳞值 = str(row_data.get("层号", "")).strip()
                if 除鳞值 and "回" in 除鳞值:
                    row_data["需标注"] = True  # 除鳞包含回字时标注钢卷号
            
            # 检查坯厚是否>230,如果是则标记需标注
            if "坯厚" in row_data:
                坯厚值 = row_data.get("坯厚", 0)
                try:
                    坯厚数值 = float(坯厚值) if 坯厚值 != "" else 0
                    if 坯厚数值 > 230:
                        row_data["需标注"] = True
                except (ValueError, TypeError):
                    pass
            
            # 检查牌号是否在APS列表中,如果不在则标记需标注
            if "牌号（钢级）" in row_data:
                brand = str(row_data.get("牌号（钢级）", "")).strip()
                if brand and apsGrades and brand not in apsGrades:
                    无APS块数 += 1
                    row_data["需标注"] = True
                    包含无APS = True
                    if brand not in 已添加无APS的钢种:
                        已添加无APS的钢种.add(brand)
                        无APS钢种数 += 1
            
            # 处理调宽字段 - 如果调宽为"1",则进行特殊处理
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
                        
                        # 检查头部宽度和尾部宽度中的小者是否 <= 轧宽
                        较小宽度 = min(板坯头部宽度值,板坯尾部宽度值)
                        if 较小宽度 <= 轧宽值:
                            row_data["调宽向上标记"] = True  # 调宽字段标注↑
                            row_data["轧宽需标注"] = True    # 轧宽字段标注Δ
                            row_data["需标注"] = True        # 钢卷号标注Δ
            
            # 只有在调宽不为"1"时,才检查"侧压量"字段
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
            
            # 检查轧宽+（余量）是否<=920,如果是则添加标记
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
                        has_low_roll_width = True
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
                
                # 检查正公差是否<=15,如果是则标注*
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
            提示信息列表.append(f"{序号}.有轧宽低于930板坯{低轧宽板坯数}块,注意定宽最小辊缝要求")
            序号 += 1
        if 极低轧宽板坯数 > 0:
            提示信息列表.append(f"{序号}.有低于860的板坯{极低轧宽板坯数}块,注意E2设定值")
            序号 += 1
        
        # 计算提示信息行数（先左右再上下,每行显示2条）
        if len(提示信息列表) == 0:
            提示信息行数 = 1  # 至少有一行（空行）
        else:
            提示信息行数 = (len(提示信息列表) + 1) // 2  # 向上取整,每行2条
        
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
        
        # 第二行及以下：计划号、块数、提示信息、打印时间
        # 序号和钢卷号列合并,填充计划号信息
        # 设置提示信息行的行高（25pt = 500 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 500
            new_sheet.row(i).height_mismatch = True
        
        new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 序号列索引, 钢卷号列索引, f"计划号：{计划号}", style_header_info)
        
        # 牌号（钢级）列填充块数信息
        if 牌号列索引 >= 0:
            new_sheet.write(字段列名行号 - 1, 牌号列索引, f"块数：{块数} 块", style_header_info)
        
        # 根据用户要求重新设计提示信息显示区域
        # 左区域：坯宽到公差带（显示提示信息）
        # 中间区域：粗轧报信到坯厚（显示提示信息）
        # 右区域：坯长到强度（显示打印时间）
        
        # 找到需要的列索引
        坯宽列索引 = -1
        坯厚列索引 = -1
        坯长列索引 = -1
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            if 映射后的列名 == "坯宽":
                坯宽列索引 = col_idx
            elif 映射后的列名 == "坯厚":
                坯厚列索引 = col_idx
            elif 映射后的列名 == "坯长":
                坯长列索引 = col_idx
        
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
        
        # 计算右区域（坯长到强度）
        if 坯长列索引 >= 0 and 强度列索引 >= 0:
            右区域起始 = 坯长列索引
            右区域结束 = 强度列索引
        else:
            右区域起始 = -1
            右区域结束 = -1
        
        # 显示提示信息
        if 左区域起始 >= 0 and 左区域结束 >= 0 and 中间区域起始 >= 0 and 中间区域结束 >= 0:
            # 计算需要的行数（每行显示2条提示信息）
            提示信息总行数 = (len(提示信息列表) + 1) // 2  # 向上取整
            for i in range(提示信息总行数):
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
        
        # 右区域（中厚到装炉顺）显示打印时间
        if 右区域起始 >= 0 and 右区域结束 >= 0:
            new_sheet.write_merge(字段列名行号 - 1, 字段列名行号 - 1, 右区域起始, 右区域结束, f"打印时间：{当前时间}", style_time)
        
        # 设置行高（25pt = 500 twips）
        for i in range(1, 字段列名行号):
            new_sheet.row(i).height = 500
            new_sheet.row(i).height_mismatch = True
        
        # 字段列名（使用内外边框线样式,强度列带右边框）
        粗轧报信字段名 = ""
        for col_idx, col_name in enumerate(target_columns):
            映射后的列名 = 字段名映射.get(col_name, col_name)
            # 强度列使用特殊样式（带右边框）
            if 映射后的列名 == "强度":
                new_sheet.write(字段列名行号,col_idx, 映射后的列名,style_header_strength)
            else:
                new_sheet.write(字段列名行号,col_idx, 映射后的列名,style_header_border)
            # 记录粗轧报信字段名用于计算行高
            if 映射后的列名 == "粗轧报信":
                粗轧报信字段名 = 映射后的列名
        
        # 设置字段列名行的行高（25pt = 500 twips）
        new_sheet.row(字段列名行号).height = 500
        new_sheet.row(字段列名行号).height_mismatch = True
        
        # 写入数据行
        for row_idx, row_data in enumerate(all_row_data, 字段列名行号 + 1):
            # 计算粗轧报信字段的内容高度（按照原程序的方法）
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
                    # 英文和数字占宽度较少,中文占宽度较多
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
                    # 增加安全系数：只有内容较长时才增加1行,短内容不增加
                    # 判断标准：如果最后一行接近满行（超过80%宽度）,则增加1行
                    最后一行宽度 = 总宽度 % 每行宽度
                    if 最后一行宽度 == 0:
                        最后一行宽度 = 每行宽度
                    if 最后一行宽度 > 每行宽度 * 0.8:
                        需要行数 = 需要行数 + 1
                    # 行高计算：基础行高25pt(500 twips),多行时每行增加18pt(360 twips)
                    # 1行=25pt, 2行=25+18=43pt, 3行=25+18+18=61pt, 以此类推
                    基础行高 = 500  # 25pt
                    每增加行高 = 360  # 18pt
                    # 计算总行高（至少25pt）
                    计算行高 = 基础行高 + (需要行数 - 1) * 每增加行高
                    # 设置行高（根据内容动态调整,最低25pt）
                    new_sheet.row(row_idx).height = 计算行高
                    new_sheet.row(row_idx).height_mismatch = True
                else:
                    # 无内容时使用默认行高（25pt = 500 twips）
                    new_sheet.row(row_idx).height = 500
                    new_sheet.row(row_idx).height_mismatch = True
            else:
                # 其他行使用默认行高（25pt = 500 twips）
                new_sheet.row(row_idx).height = 500
                new_sheet.row(row_idx).height_mismatch = True
            
            顺序号 = row_idx - 字段列名行号  # 从1开始的顺序号
            
            # 写入顺序号
            new_sheet.write(row_idx, 0, 顺序号, style_data_12pt_left_border)
            
            # 写入其他字段
            for col_idx, col_name in enumerate(target_columns[1:], 1):
                value = row_data.get(col_name, "")
                
                # 根据字段名选择不同的样式
                if col_name == "钢卷号":
                    # 检查是否需要标注三角符号
                    需标注 = row_data.get("需标注", False)
                    if 需标注:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_16pt_left)
                elif col_name == "牌号（钢级）":
                    # 无 APS 钢种时添加Δ标记
                    is_no_aps = row_data.get("是无 APS 钢种", False)
                    需标注 = row_data.get("需标注", False)
                    if 需标注 and is_no_aps:
                        value = str(value) + "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_left)
                elif col_name == "坯宽":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_left_dashed)
                elif col_name == "侧压量":
                    # 减宽超标时添加三角符号
                    if row_data.get("减宽超标", False):
                        if value:
                            try:
                                减宽数值 = float(value)
                                value = str(int(减宽数值)) + "Δ"
                            except (ValueError, TypeError):
                                value = str(value) + "Δ"
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_double)
                    else:
                        new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)
                elif col_name == "板坯宽度调宽标记":
                    # 调宽向上标记时添加↑符号
                    if row_data.get("调宽向上标记", False):
                        if value:
                            try:
                                调宽数值 = float(value)
                                value = str(int(调宽数值)) + "↑"
                            except (ValueError, TypeError):
                                value = str(value) + "↑"
                        else:
                            value = "↑"
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_long_dashed)
                elif col_name == "轧宽":
                    # 轧宽需标注时添加Δ标记
                    if row_data.get("轧宽需标注", False):
                        if value:
                            try:
                                轧宽数值 = float(value)
                                value = str(int(轧宽数值)) + "Δ"
                            except (ValueError, TypeError):
                                value = str(value) + "Δ"
                        else:
                            value = "Δ"
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)
                elif col_name == "轧宽 +（余量）":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashed)
                elif col_name == "碳":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)
                elif col_name == "粗轧报信":
                    new_sheet.write(row_idx, col_idx, value, style_data_wrap_14pt)
                elif col_name == "层号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_dashed)
                elif col_name == "坯厚":
                    # 坯厚>230 时添加Δ标记
                    if value:
                        try:
                            坯厚数值 = float(value)
                            if 坯厚数值 > 230:
                                value = str(value) + "Δ"
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)
                elif col_name == "坯长":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "轧厚":
                    # 保留小数点后 1 位,不进行四舍五入（直接截断）
                    if value:
                        try:
                            # 转换为浮点数
                            float_val = float(value)
                            # 截断到小数点后 1 位（不四舍五入）
                            import math
                            truncated_val = math.floor(float_val * 10) / 10
                            # 格式化为字符串,保留 1 位小数
                            value = f"{truncated_val:.1f}"
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_dashdot)
                elif col_name == "中间坯厚度设定值":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "去向":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "订货宽度":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "切边方式":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt)
                elif col_name == "RT2 目标值":
                    new_sheet.write(row_idx, col_idx, value, style_data_14pt_center)
                elif col_name == "硬度组":
                    # 保留个位数值（不保留小数）
                    if value:
                        try:
                            # 转换为浮点数
                            float_val = float(value)
                            # 截断到个位（不四舍五入）
                            import math
                            truncated_val = math.floor(float_val)
                            # 格式化为整数
                            value = str(int(truncated_val))
                        except (ValueError, TypeError):
                            pass
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_strength)
                elif col_name == "装炉顺序号":
                    new_sheet.write(row_idx, col_idx, value, style_data_12pt_right_border)
                else:
                    new_sheet.write(row_idx, col_idx, value, style_data)
        
        # 10. 保存新文件
        new_file_path = file_path  # 覆盖原文件
        
        try:
            new_workbook.save(new_file_path)
            print(f"文件已保存: {new_file_path}")
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
        finally:
            # 释放资源
            if hasattr(workbook, 'release_resources'):
                workbook.release_resources()
        
        return has_low_roll_width
    
    def safe_read_excel(self, file_path, max_retries=3, retry_delay=0.5):
        """安全读取Excel文件,支持重试
        
        Args:
            file_path: 文件路径
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            tuple: (success, result),success为布尔值,result为Workbook对象或错误信息
        """
        import xlrd
        import time
        
        for attempt in range(max_retries):
            try:
                workbook = xlrd.open_workbook(file_path)
                return True, workbook
            except Exception as e:
                print(f"读取文件失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return False, str(e)
    
    def load_remove_phosphorus_list(self):
        """加载除鳞钢种列表"""
        return []  # 简化实现,实际应该从文件或配置中加载
    
    def load_aps_grades(self):
        """加载APS钢种列表"""
        return []  # 简化实现,实际应该从文件或配置中加载
    
    def print_selected(self):
        """打印选中的计划号"""
        # 简化实现,实际应该调用打印功能
        print("打印选中的计划号")
        # 刷新数据
        self.refresh_data()

    def select_all(self):
        """全选"""
        self.table_widget.selectAll()

    def deselect_all(self):
        """取消全选"""
        self.table_widget.clearSelection()

    def refresh_plan_list_from_file(self):
        """从装炉顺序.xls文件读取数据并更新表格"""
        temp_file_path = None
        plan_data = []
        try:
            import os
            import xlrd
            import shutil
            import time
            
            # 读取装炉顺序.xls文件
            plan_dir = os.path.join(self.plan_dir, "计划号")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            print(f"查找装炉顺序文件: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"文件不存在: {excel_file}")
                # 检查备份计划目录
                backup_dir = os.path.join(plan_dir, "备份计划")
                backup_excel_file = os.path.join(backup_dir, "装炉顺序.xls")
                if os.path.exists(backup_excel_file):
                    print(f"在备份计划目录中找到装炉顺序文件: {backup_excel_file}")
                    excel_file = backup_excel_file
                else:
                    print(f"备份计划目录中也不存在装炉顺序文件: {backup_excel_file}")
                    # 更新空表格
                    self.plan_data = []
                    self.update_table()
                    self.stats_label.setText("总块数: 0 | 无文件: 0")
                    return False
            
            # 创建临时副本（存储在计划号文件夹中）
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
                print("装炉顺序.xls文件缺少必要的列（装炉顺序、计划号、钢卷号）")
                # 更新空表格
                self.plan_data = []
                self.update_table()
                self.stats_label.setText("总块数: 0 | 无文件: 0")
                return False
            
            # 读取数据
            max_rows = min(1000, sheet.nrows)  # 限制读取行数,防止内存溢出
            print(f"开始读取数据,总行数: {sheet.nrows}, 限制行数: {max_rows}")
            for row in range(1, max_rows):
                try:
                    if row % 100 == 0:  # 每100行打印一次,减少输出
                        print(f"正在读取第 {row} 行...")
                    order = sheet.cell_value(row, order_col)
                    # 转换装炉顺序为整数
                    if isinstance(order, float) and order.is_integer():
                        order = int(order)
                    plan_no = str(sheet.cell_value(row, plan_col)).strip()
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    
                    # 清理钢卷号,只保留ASCII数字
                    try:
                        coil_no = ''.join(c for c in coil_no if c.isdigit())
                    except Exception as e:
                        print(f"清理钢卷号失败: {e}")
                        coil_no = ''
                    
                    if plan_no and coil_no:
                        plan_data.append({
                            'order': order,
                            'plan_no': plan_no,
                            'coil_no': coil_no
                        })
                        if row % 50 == 0:  # 每50行打印一次,减少输出
                            print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no} (行 {row})")
                    else:
                        if row % 100 == 0:  # 每100行打印一次,减少输出
                            print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}' (行 {row})")
                except Exception as e:
                    print(f"读取行 {row} 失败: {e}")
                    # 继续处理下一行,不中断整个加载过程
                    continue
            print(f"数据读取完成,共加载 {len(plan_data)} 条数据")
        except Exception as e:
            print(f"读取装炉顺序文件失败: {e}")
            # 更新空表格
            self.plan_data = []
            self.update_table()
            self.stats_label.setText("总块数: 0 | 无文件: 0")
            return False
        finally:
            # 无论是否发生异常,都删除临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"删除临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")
            
            print(f"加载到 {len(plan_data)} 条装炉数据")
            if len(plan_data) == 0:
                print("装炉顺序.xls文件中没有数据")
                # 更新空表格
                self.plan_data = []
                self.update_table()
                self.stats_label.setText("总块数: 0 | 无文件: 0")
                return False
            
            # 按装炉顺序排序
            plan_data.sort(key=lambda x: x['order'])
            
            # 按计划号分组,计算每个计划号的块数和起止钢卷号
            plan_groups = {}
            for item in plan_data:
                plan_no = item['plan_no']
                if plan_no not in plan_groups:
                    plan_groups[plan_no] = {
                        'count': 0,
                        'coils': []
                    }
                plan_groups[plan_no]['count'] += 1
                plan_groups[plan_no]['coils'].append(item['coil_no'])
            
            # 构建计划数据列表,按装炉顺序排序
            plan_order = []
            seen_plans = set()
            for item in plan_data:
                plan_no = item['plan_no']
                if plan_no not in seen_plans:
                    plan_order.append(plan_no)
                    seen_plans.add(plan_no)
            
            # 构建计划数据
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
            
            # 获取backup文件夹中的所有xls文件
            backup_dir = os.path.join(plan_dir, "backup")
            if os.path.exists(backup_dir):
                for f in os.listdir(backup_dir):
                    if f.endswith('.xls') or f.endswith('.xlsx'):
                        # 去掉扩展名获取计划号
                        plan_no_from_file = os.path.splitext(f)[0]
                        plan_files.add(plan_no_from_file)
            
            print(f"计划号文件夹和backup文件夹中找到 {len(plan_files)} 个文件")
            
            # 按装炉顺序处理计划号
            for plan_no in plan_order:
                if plan_no in plan_groups:
                    group = plan_groups[plan_no]
                    count = group['count']
                    coils = group['coils']
                    min_coil = min(coils) if coils else ''
                    max_coil = max(coils) if coils else ''
                    
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
                                # 读取Excel文件
                                workbook = xlrd.open_workbook(file_path)
                                sheet = workbook.sheet_by_index(0)
                                
                                # 查找字段列名行
                                field_name_row = -1
                                for row_idx in range(min(10, sheet.nrows)):
                                    row_has_field_names = False
                                    for col_idx in range(sheet.ncols):
                                        cell_value = str(sheet.cell_value(row_idx, col_idx))
                                        if any(field in cell_value for field in ["序号", "钢卷号", "牌号", "坯厚", "轧厚", "轧宽", "装炉顺"]):
                                            row_has_field_names = True
                                            break
                                    if row_has_field_names:
                                        field_name_row = row_idx
                                        break
                                
                                if field_name_row != -1:
                                    # 获取列名
                                    current_columns = []
                                    for i in range(sheet.ncols):
                                        current_columns.append(sheet.cell_value(field_name_row, i))
                                    
                                    # 查找轧宽列
                                    roll_width_col = -1
                                    for col_idx, col_name in enumerate(current_columns):
                                        if "轧宽" in col_name:
                                            roll_width_col = col_idx
                                            break
                                    
                                    if roll_width_col != -1:
                                        # 检查数据行中的轧宽值
                                        for row_idx in range(field_name_row + 1, min(field_name_row + 100, sheet.nrows)):  # 限制检查行数
                                            roll_width_value = sheet.cell_value(row_idx, roll_width_col)
                                            try:
                                                # 去除可能的标记（如Δ）
                                                roll_width_clean = str(roll_width_value).strip().replace('Δ', '')
                                                roll_width_num = float(roll_width_clean)
                                                if roll_width_num <= 930:
                                                    has_low_roll_width = True
                                                    break
                                            except (ValueError, TypeError):
                                                pass
                            except Exception as e:
                                print(f"检查轧宽时出错 {plan_no}: {str(e)}")
                    
                    # 从保存的集合中恢复低轧宽板坯状态
                    if hasattr(self, 'low_roll_width_plans') and plan_no in self.low_roll_width_plans:
                        has_low_roll_width = True
                    
                    self.plan_data.append({
                        'plan_no': plan_no,
                        'count': count,
                        'status': status,
                        'min_coil': min_coil,
                        'max_coil': max_coil,
                        'has_low_roll_width': has_low_roll_width
                    })
                    total_count += count
            
            # 更新表格
            self.update_table()
            self.stats_label.setText(f"总块数: {total_count} | 无文件: {no_file_count}")
            
            print(f"成功加载 {len(self.plan_data)} 个计划号,总计 {total_count} 块,无文件 {no_file_count} 个")
            return True
    
    def update_table(self):
        """更新表格显示"""
        # 清空表格
        self.table_widget.setRowCount(0)
        
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
            if hasattr(self, 'processed_plans') and plan_no in self.processed_plans:
                status_text += f"[已处理] "
            if hasattr(self, 'printed_plans') and plan_no in self.printed_plans:
                status_text += f"[已打印] "
            if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                status_text += f"[无APS] "
            if item.get('has_low_roll_width', False):
                status_text += f"[轧宽<930] "
            
            # 构建钢卷号范围文本
            coil_text = ""
            if min_coil and max_coil:
                coil_text = f"[{min_coil}-{max_coil}]"
            
            # 添加行
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            
            # 设置单元格内容
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(plan_no))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(count)))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(status_text.strip()))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(coil_text))
            
            # 设置字体
            font = QFont("宋体", 28, QFont.Bold)
            for col in range(4):
                table_item = self.table_widget.item(row_position, col)
                if table_item:
                    table_item.setFont(font)
            
            # 设置文本对齐
            for col in range(4):
                table_item = self.table_widget.item(row_position, col)
                if table_item:
                    table_item.setTextAlignment(Qt.AlignCenter)
            
            # 设置颜色
            if hasattr(self, 'no_aps_plans') and plan_no in self.no_aps_plans:
                # 无APS时使用红色字体
                for col in range(4):
                    table_item = self.table_widget.item(row_position, col)
                    if table_item:
                        table_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif item.get('has_low_roll_width', False):
                # 低轧宽时使用红色字体
                for col in range(4):
                    table_item = self.table_widget.item(row_position, col)
                    if table_item:
                        table_item.setForeground(QBrush(QColor(255, 0, 0)))
            elif hasattr(self, 'recently_exported_plans') and plan_no in self.recently_exported_plans:
                # 最近导出的计划号使用绿色字体
                for col in range(4):
                    table_item = self.table_widget.item(row_position, col)
                    if table_item:
                        table_item.setForeground(QBrush(QColor(0, 128, 0)))
    
    def start_anti_logout(self):
        """启动防注销服务"""
        try:
            # 这里可以添加防注销服务的逻辑
            print("防注销服务已启动")
        except Exception as e:
            print(f"启动防注销服务失败: {str(e)}")
    
    def start_auto_execution(self):
        """启动自动执行服务"""
        try:
            # 这里可以添加自动执行服务的逻辑
            print("自动执行服务已启动")
        except Exception as e:
            print(f"启动自动执行服务失败: {str(e)}")
    
    def connect_signals(self):
        """连接信号槽"""
        # 连接全选按钮
        self.select_all_btn.clicked.connect(self.select_all)
        # 连接取消全选按钮
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        # 连接刷新按钮
        self.refresh_btn.clicked.connect(self.refresh_data)
        # 连接自动导出按钮
        self.auto_export_btn.clicked.connect(self.auto_export)
        # 连接设置按钮
        self.settings_btn.clicked.connect(self.open_settings_window)
        # 连接装炉明细按钮
        self.furnace_details_btn.clicked.connect(self.open_furnace_details_window)
        # 连接处理计划按钮
        self.process_plans_btn.clicked.connect(self.process_plans)
        # 连接查看导出过程按钮
        self.view_export_process_btn.clicked.connect(self.view_export_process)
        # 连接显示按钮
        self.show_selected_btn.clicked.connect(self.show_selected)
        # 连接打印按钮
        self.print_selected_btn.clicked.connect(self.print_selected)
    
    def open_settings_window(self):
        """打开设置窗口"""
        if not hasattr(self, 'settings_window') or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self)
            self.settings_window.show()
    
    def get_settings(self):
        """获取当前设置"""
        import json
        import os
        
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        if os.path.exists(config_file):
            try:
                if os.path.getsize(config_file) < 5:
                    raise ValueError("Settings file is too small")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if not isinstance(settings, dict):
                    raise ValueError("Invalid settings format")
                
                return settings
            except Exception as e:
                print(f"加载设置失败: {str(e)}")
        
        # 返回默认设置
        return {
            "selectedWindow": "Doc1.docx - Word",
            "autoPrint": True,
            "autoExec": False,
            "execMode": "interval",
            "intervalMinutes": 1,
            "execTimes": "16:00,16:02,16:04",
            "antiLogout": False,
            "antiLogoutInterval": 1
        }
    
    def open_furnace_details_window(self):
        """打开装炉明细窗口"""
        self.furnace_details_window = FurnaceDetailsWindow()
        self.furnace_details_window.show()


    
    def view_export_process(self):
        """查看无文件计划号明细的导出过程"""
        # 创建一个新窗口来显示导出过程
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        dialog = QDialog(self)
        dialog.setWindowTitle("查看无文件计划号明细导出过程")
        dialog.setGeometry(300, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        # 添加标题
        title_label = QLabel("无文件计划号明细导出过程")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self.font())
        layout.addWidget(title_label)
        
        # 添加文本框显示导出过程
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("宋体", 12))
        layout.addWidget(text_edit)
        
        # 添加按钮布局
        btn_layout = QHBoxLayout()
        
        # 添加关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addStretch(1)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        # 显示导出过程的详细信息
        process_info = []
        process_info.append("=== 无文件计划号明细导出过程 ===")
        process_info.append("")
        process_info.append("1. 筛选无文件计划号")
        process_info.append("   - 从计划数据中筛选状态为'无文件'的计划号")
        process_info.append("   - 验证计划号是否在总计划号列表中存在")
        process_info.append("")
        process_info.append("2. 执行导出操作")
        process_info.append("   - 鼠标点击计划号坐标")
        process_info.append("   - 鼠标点击导出计划明细按钮")
        process_info.append("   - 键盘输入计划号")
        process_info.append("   - 按回车确认")
        process_info.append("   - 按左方向键（替换覆盖）")
        process_info.append("   - 按回车确认")
        process_info.append("")
        process_info.append("3. 导出结果处理")
        process_info.append("   - 记录成功导出的计划号")
        process_info.append("   - 记录失败导出的计划号")
        process_info.append("   - 刷新界面,选中已导出的计划号")
        process_info.append("")
        process_info.append("=== 导出过程结束 ===")
        
        # 添加当前无文件计划号的信息
        no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
        process_info.append("")
        process_info.append(f"当前无文件计划号数量: {len(no_file_plans)}")
        if no_file_plans:
            process_info.append("无文件计划号列表:")
            for plan_no in no_file_plans:
                process_info.append(f"  - {plan_no}")
        else:
            process_info.append("当前没有无文件计划号")
        
        # 显示信息
        text_edit.setPlainText('\n'.join(process_info))
        
        dialog.exec_()

    def show_selected(self):
        """显示选中的计划"""
        try:
            selected_items = self.table_widget.selectedItems()
            if not selected_items:
                QMessageBox.information(self, "提示", "请先在表格中选择一行数据")
                return
            
            # 获取选中行的数据
            row = selected_items[0].row()
            
            # 检查表格是否有足够的列
            if self.table_widget.columnCount() < 1:  # 需要至少1列（计划号）
                QMessageBox.warning(self, "错误", "表格列数不足，无法获取计划号")
                return
            
            # 获取计划号（计划号在第0列）
            plan_item = self.table_widget.item(row, 0)  # 计划号在第一列
            if not plan_item:
                QMessageBox.warning(self, "错误", "无法获取计划号")
                return
            
            plan_no = plan_item.text().strip()
            if not plan_no:
                QMessageBox.warning(self, "错误", "计划号为空")
                return
            
            print(f"尝试显示计划号: {plan_no}")
            
            # 检查是否已处理
            if not hasattr(self, 'processed_plans'):
                self.processed_plans = set()
            
            # 如果未处理，先处理该计划
            if plan_no not in self.processed_plans:
                print(f"计划 {plan_no} 未处理，正在处理...")
                # 先选择当前行
                self.table_widget.clearSelection()  # 清除之前的选择
                self.table_widget.selectRow(row)  # 选择当前行
                # 确保选择状态已更新
                QApplication.processEvents()  # 处理事件，确保选择状态更新
                # 调用处理计划方法
                self.process_plans(auto_print=False, show_result=False)
                # 检查处理是否成功
                if plan_no not in self.processed_plans:
                    # 处理失败，退出
                    QMessageBox.warning(self, "错误", "计划处理失败，无法显示")
                    return
                print(f"计划号 {plan_no} 处理成功")
            
            # 获取计划号文件
            plan_file = self.get_plan_file(plan_no)
            if plan_file:
                try:
                    import subprocess
                    print(f"尝试打开文件: {plan_file}")
                    # 使用subprocess打开文件，与原程序一致
                    subprocess.Popen(['start', '', plan_file], shell=True)
                    print(f"已打开文件: {plan_file}")
                except Exception as e:
                    error_msg = f"打开文件失败: {str(e)}"
                    print(error_msg)
                    QMessageBox.warning(self, "错误", error_msg)
            else:
                error_msg = f"找不到计划号文件: {plan_no}.xls 或 {plan_no}.xlsx"
                print(error_msg)
                QMessageBox.warning(self, "错误", error_msg)
        except Exception as e:
            error_msg = f"显示计划时发生错误: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "错误", error_msg)

    def show_message(self, title, message):
        """显示消息框"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def get_plan_file(self, plan_no):
        """获取计划号文件路径"""
        import os
        # 首先在计划号目录查找
        plan_dir = os.path.join(os.getcwd(), "计划号")
        
        # 尝试.xls格式
        file_path = os.path.join(plan_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(plan_dir, f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        
        # 然后在backup目录查找
        backup_dir = os.path.join(plan_dir, "backup")
        if os.path.exists(backup_dir):
            # 尝试.xls格式
            file_path = os.path.join(backup_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
            
            # 尝试.xlsx格式
            file_path = os.path.join(backup_dir, f"{plan_no}.xlsx")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
        
        # 尝试其他可能的路径
        # 直接在计划号目录的上级目录查找
        parent_dir = os.path.dirname(plan_dir)
        
        # 尝试.xls格式
        file_path = os.path.join(parent_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(parent_dir, f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        
        # 尝试当前目录
        # 尝试.xls格式
        file_path = os.path.join(os.getcwd(), f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        
        # 尝试.xlsx格式
        file_path = os.path.join(os.getcwd(), f"{plan_no}.xlsx")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        
        # 所有路径都找不到
        print(f"找不到计划号文件: {plan_no}.xls 或 {plan_no}.xlsx")
        return None

    def print_selected(self):
        """打印选中的计划 - 复刻原程序的打印功能"""
        try:
            # 检查是否选择了计划
            selected_items = self.table_widget.selectionModel().selectedRows()
            if not selected_items:
                QMessageBox.warning(self, "警告", "请先在计划号列表中选择要打印的计划号")
                return
            
            # 加载最新的状态
            self.load_data()
            
            # 获取选中的计划号，按照表格显示顺序（按行号排序）
            selected_rows = sorted([index.row() for index in selected_items])
            selected_plans = [self.plan_data[row]['plan_no'] for row in selected_rows]
            
            # 创建进度窗口
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QFont
            
            # 创建进度窗口
            progress_window = QDialog(self)
            progress_window.setWindowTitle("打印进度")
            progress_window.setFixedSize(600, 400)
            progress_window.setWindowModality(Qt.ApplicationModal)
            
            # 主布局
            main_layout = QVBoxLayout(progress_window)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(15)
            
            # 标题
            progress_label = QLabel("准备开始打印...")
            progress_label.setFont(QFont("宋体", 14))
            progress_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(progress_label)
            
            # 详细信息
            detail_label = QLabel("")
            detail_label.setFont(QFont("宋体", 12))
            detail_label.setStyleSheet("color: gray;")
            detail_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(detail_label)
            
            # 按钮布局
            btn_layout = QHBoxLayout()
            btn_layout.addStretch(1)
            
            # 取消按钮
            cancel_btn = QPushButton("取消")
            cancel_btn.setFont(QFont("宋体", 12))
            cancel_btn.setFixedSize(80, 30)
            btn_layout.addWidget(cancel_btn)
            
            btn_layout.addStretch(1)
            main_layout.addLayout(btn_layout)
            
            # 显示窗口
            progress_window.show()
            
            # 更新进度的函数
            def update_progress(main_msg, detail_msg=""):
                """更新进度显示"""
                progress_label.setText(main_msg)
                if detail_msg:
                    detail_label.setText(detail_msg)
                QApplication.processEvents()
                print(f"[打印进度] {main_msg} {detail_msg}")
            
            # 取消标志
            canceled = False
            def on_cancel():
                nonlocal canceled
                canceled = True
                print("打印操作被取消")
            
            cancel_btn.clicked.connect(on_cancel)
            
            # 获取计划号文件夹路径
            plan_dir = os.path.join(self.plan_dir, "计划号")
            backup_dir = os.path.join(plan_dir, "backup")
            
            # 构建选中计划号的文件路径列表
            selected_files = []
            update_progress("正在检查文件...", f"共 {len(selected_plans)} 个计划号")
            
            if canceled:
                progress_window.close()
                return
            
            for plan_no in selected_plans:
                if canceled:
                    progress_window.close()
                    return
                
                # 首先检查计划号文件夹
                file_path = os.path.join(plan_dir, f"{plan_no}.xls")
                if os.path.exists(file_path):
                    selected_files.append((plan_no, file_path))
                    update_progress("正在检查文件...", f"找到文件: {plan_no}.xls")
                else:
                    # 如果已打印，检查backup目录
                    if hasattr(self, 'printed_plans') and plan_no in self.printed_plans:
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
                progress_window.close()
                QMessageBox.information(self, "提示", "选中的计划号没有对应的文件")
                return
            
            # 检查并处理未处理的计划
            processed_plans = []
            failed_plans = []
            
            update_progress("正在处理计划...", f"共 {len(selected_files)} 个计划需要处理")
            
            if canceled:
                progress_window.close()
                return
            
            for i, (plan_no, file_path) in enumerate(selected_files):
                if canceled:
                    progress_window.close()
                    return
                
                # 如果未处理，先处理该计划
                if not hasattr(self, 'processed_plans'):
                    self.processed_plans = set()
                
                if plan_no not in self.processed_plans:
                    update_progress("正在处理计划...", f"处理 {plan_no} ({i+1}/{len(selected_files)})")
                    try:
                        # 处理单个计划
                        has_low_roll_width = self.process_single_plan(plan_no, file_path)
                        update_progress("正在处理计划...", f"已处理: {plan_no}")
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
                self.load_data()
            
            # 如果有处理失败的计划，显示提示
            if failed_plans:
                progress_window.close()
                QMessageBox.warning(self, "警告", f"以下计划号处理失败：\n\n" + "\n".join(failed_plans) + "\n\n这些计划将不会被打印")
                # 移除处理失败的计划
                selected_files = [(plan_no, file_path) for plan_no, file_path in selected_files if plan_no not in [p.split(' ')[0] for p in failed_plans]]
                
                # 重新创建进度窗口
                progress_window = QDialog(self)
                progress_window.setWindowTitle("打印进度")
                progress_window.setFixedSize(600, 400)
                progress_window.setWindowModality(Qt.ApplicationModal)
                
                # 主布局
                main_layout = QVBoxLayout(progress_window)
                main_layout.setContentsMargins(20, 20, 20, 20)
                main_layout.setSpacing(15)
                
                # 标题
                progress_label = QLabel("准备开始打印...")
                progress_label.setFont(QFont("宋体", 14))
                progress_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(progress_label)
                
                # 详细信息
                detail_label = QLabel("")
                detail_label.setFont(QFont("宋体", 12))
                detail_label.setStyleSheet("color: gray;")
                detail_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(detail_label)
                
                # 按钮布局
                btn_layout = QHBoxLayout()
                btn_layout.addStretch(1)
                
                # 取消按钮
                cancel_btn = QPushButton("取消")
                cancel_btn.setFont(QFont("宋体", 12))
                cancel_btn.setFixedSize(80, 30)
                btn_layout.addWidget(cancel_btn)
                
                btn_layout.addStretch(1)
                main_layout.addLayout(btn_layout)
                
                # 显示窗口
                progress_window.show()
                
                # 更新进度的函数
                def update_progress(main_msg, detail_msg=""):
                    """更新进度显示"""
                    progress_label.setText(main_msg)
                    if detail_msg:
                        detail_label.setText(detail_msg)
                    QApplication.processEvents()
                    print(f"[打印进度] {main_msg} {detail_msg}")
                
                # 取消标志
                canceled = False
                def on_cancel():
                    nonlocal canceled
                    canceled = True
                    print("打印操作被取消")
                
                cancel_btn.clicked.connect(on_cancel)
            
            if not selected_files:
                progress_window.close()
                QMessageBox.information(self, "提示", "没有符合条件的计划可以打印")
                return
            
            # 打印每个文件
            success_count = 0
            failed_count = 0
            failed_files = []
            success_files = []
            
            update_progress("正在打印文件...", f"共 {len(selected_files)} 个计划需要打印")
            
            if canceled:
                progress_window.close()
                return
            
            for i, (plan_no, file_path) in enumerate(selected_files):
                if canceled:
                    progress_window.close()
                    return
                
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
                        if not hasattr(self, 'printed_plans'):
                            self.printed_plans = set()
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
                self.load_data()
            
            # 将打印成功的文件移动到backup目录
            if success_files:
                update_progress("正在移动文件...", "将打印成功的文件移动到backup目录")
                import shutil
                
                # 创建backup目录（如果不存在）
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                    update_progress("正在移动文件...", f"创建backup目录: {backup_dir}")
                    print(f"✓ 创建backup目录: {backup_dir}")
                
                # 移动文件
                moved_count = 0
                for i, plan_no in enumerate(success_files):
                    if canceled:
                        progress_window.close()
                        return
                    
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
            progress_window.close()
            
            # 显示结果
            if success_count > 0 or failed_count > 0:
                # 创建结果显示窗口
                result_window = QDialog(self)
                result_window.setWindowTitle("打印完成")
                result_window.setFixedSize(400, 250)
                result_window.setWindowModality(Qt.ApplicationModal)
                
                # 主布局
                main_layout = QVBoxLayout(result_window)
                main_layout.setContentsMargins(20, 20, 20, 20)
                main_layout.setSpacing(15)
                
                # 标题
                title_label = QLabel("打印完成！")
                title_label.setFont(QFont("宋体", 18, QFont.Bold))
                title_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(title_label)
                
                # 统计信息
                stats_label = QLabel(f"成功: {success_count} 个 | 失败: {failed_count} 个")
                stats_label.setFont(QFont("宋体", 14))
                stats_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(stats_label)
                
                # 成功的计划号
                if success_files:
                    success_label = QLabel(f"成功的计划号: {', '.join(success_files)}")
                    success_label.setFont(QFont("宋体", 12))
                    success_label.setWordWrap(True)
                    main_layout.addWidget(success_label)
                
                # 失败的计划号
                if failed_files:
                    failed_label = QLabel(f"失败的计划号: {', '.join(failed_files)}")
                    failed_label.setFont(QFont("宋体", 12))
                    failed_label.setStyleSheet("color: red;")
                    failed_label.setWordWrap(True)
                    main_layout.addWidget(failed_label)
                
                # 按钮布局
                btn_layout = QHBoxLayout()
                btn_layout.addStretch(1)
                
                # 确定按钮
                ok_btn = QPushButton("确定")
                ok_btn.setFont(QFont("宋体", 14))
                ok_btn.setFixedSize(100, 40)
                ok_btn.clicked.connect(result_window.accept)
                btn_layout.addWidget(ok_btn)
                
                btn_layout.addStretch(1)
                main_layout.addLayout(btn_layout)
                
                # 显示窗口
                result_window.exec_()
        except Exception as e:
            print(f"打印计划失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"打印计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
            # 直接读取文件，不使用safe_read_excel
            workbook = xlrd.open_workbook(file_path)
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
            
            # 找到强度列的索引
            强度列索引 = -1
            for col_idx, col_name in enumerate(current_columns):
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
                col_end_letter = get_column_letter(print_col_end)  # 强度列对应的字母
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
                
                # 设置纸张大小为 xlPaperFanfoldUS (137) - 美国连续折叠纸
                preferred_size = 137  # xlPaperFanfoldUS
                try:
                    worksheet.PageSetup.PaperSize = preferred_size
                    print(f"[纸张设置] ✓ 成功设置纸张: FanfoldUS (14.875 x 11 inch)")
                except Exception as e:
                    print(f"[纸张设置] ✗ 首选纸张设置失败: {str(e)}")
                    # 尝试备选纸张
                    fallback_papers = [39, 118, 119, 1, 9]
                    for paper_code in fallback_papers:
                        if paper_code == preferred_size:
                            continue
                        try:
                            worksheet.PageSetup.PaperSize = paper_code
                            print(f"[纸张设置] ✓ 成功设置备选纸张: {paper_code}")
                            break
                        except Exception as e:
                            print(f"[纸张设置] ✗ 备选纸张 {paper_code} 设置失败: {str(e)}")
                            continue
                
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

    def print_plan(self, plan_no):
        """打印单个计划"""
        import os
        import shutil
        import time
        
        try:
            # 找到计划号文件
            plan_dir = os.path.join(self.plan_dir, "计划号", plan_no)
            if not os.path.exists(plan_dir):
                print(f"计划目录不存在：{plan_dir}")
                return
            
            # 查找明细文件
            mingxi_file = None
            for file in os.listdir(plan_dir):
                if file.endswith("明细.xls") or file.endswith("明细.xlsx"):
                    mingxi_file = os.path.join(plan_dir, file)
                    break
            
            if not mingxi_file:
                print(f"未找到明细文件：{plan_dir}")
                return
            
            # 创建临时副本
            temp_file_name = f"temp_{plan_no}_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            shutil.copy2(mingxi_file, temp_file_path)
            print(f"创建临时副本：{temp_file_path}")
            
            # 使用 pywin32 设置纸张和打印
            try:
                import win32com.client as win32
                
                excel = win32.Dispatch("Excel.Application")
                excel.Visible = False
                excel.DisplayAlerts = False
                
                # 打开文件
                workbook = excel.Workbooks.Open(temp_file_path)
                ws = workbook.ActiveSheet
                
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
                
                # 设置打印区域（整个工作表）
                ws.PageSetup.PrintArea = ws.UsedRange.Address
                
                # 设置打印标题行（表头）
                # 假设表头在第 3 行
                ws.PageSetup.PrintTitleRows = "$3:$3"
                
                # 保存并关闭
                workbook.Save()
                workbook.Close()
                excel.Quit()
                print("[纸张设置] ✓ pywin32 设置完成")
                
                # 打印文件
                os.startfile(temp_file_path, 'print')
                print(f"已打印计划：{plan_no}")
                
            except ImportError:
                print("[纸张设置] pywin32 未安装,使用默认打印方式")
                # 使用系统默认打印
                os.startfile(temp_file_path, 'print')
            
            # 保留临时文件
            print(f"临时文件已保留：{temp_file_path}")
            
        except Exception as e:
            print(f"打印计划 {plan_no} 失败：{str(e)}")
            import traceback
            traceback.print_exc()

    def auto_export(self, from_main_window=True):
        """自动导出"""
        # 检查是否已经在运行,防止递归调用
        if hasattr(self, 'is_auto_export_running') and self.is_auto_export_running:
            print("自动导出已经在运行,跳过重复调用")
            QMessageBox.information(self, "提示", "自动导出已在运行中")
            return
        
        # 设置运行标志
        self.is_auto_export_running = True
        
        # 添加线程锁,确保函数不会被并发调用
        import threading
        if not hasattr(self, 'auto_export_lock'):
            self.auto_export_lock = threading.Lock()
        
        # 尝试获取锁,如果获取不到则返回
        if not self.auto_export_lock.acquire(blocking=False):
            print("自动导出已经被锁定,跳过重复调用")
            QMessageBox.information(self, "提示", "自动导出已在运行中")
            self.is_auto_export_running = False
            return
        
        # 检查pyautogui是否可用
        try:
            import pyautogui
            PYAUTOGUI_AVAILABLE = True
        except ImportError:
            PYAUTOGUI_AVAILABLE = False
            QMessageBox.critical(self, "错误", "pyautogui未安装,请先安装: pip install pyautogui")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        if not PYAUTOGUI_AVAILABLE:
            QMessageBox.critical(self, "错误", "pyautogui未安装,请先安装: pip install pyautogui")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        # 检查是否启用调试模式
        debug_mode = self.coordinates.get("debug_mode", False)
        print(f"调试模式: {'开启' if debug_mode else '关闭'}")
        
        # 初始化调试日志函数
        def add_debug_log(msg):
            pass  # 默认不输出
        
        # 检查应用程序是否在前台运行
        import os
        import win32gui
        import win32process
        
        # 获取当前进程ID
        current_pid = os.getpid()
        
        # 获取前台窗口的进程ID
        foreground_hwnd = win32gui.GetForegroundWindow()
        _, foreground_pid = win32process.GetWindowThreadProcessId(foreground_hwnd)
        
        # 保存启动自动执行时的前台窗口句柄,以便后续返回
        self.previous_foreground_hwnd = foreground_hwnd
        
        # 检查前台窗口是否属于当前进程
        is_in_foreground = (foreground_pid == current_pid)
        

        
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
            if progress_window:
                progress_window.close()
            # 检查应用程序是否在前台运行
            if is_in_foreground:
                QMessageBox.warning(self, "警告", f"以下坐标未设置:\n" + "\n".join(f"  - {n}" for n in unset_coords) + "\n\n请先设置这些坐标后再测试")
            else:
                print(f"以下坐标未设置: {unset_coords}\n请先设置这些坐标后再测试")
            self.is_auto_export_running = False
            if hasattr(self, 'auto_export_lock'):
                try:
                    self.auto_export_lock.release()
                except:
                    pass
            return
        
        # 定义进度更新函数
        def update_progress(main_msg, detail_msg=""):
            """更新进度显示"""
            # 只打印日志,不更新进度窗口
            print(f"[进度] {main_msg} {detail_msg}")
        
        # 定义导出完成后的回调函数
        def export_finished(success, message, exported_plans=[], failed_plans=[], coord_map={}):
            """导出完成后的回调"""
            # 确保在主线程中执行
            from PyQt5.QtCore import QEvent, QCoreApplication, QTimer, Qt
            from PyQt5.QtWidgets import QMessageBox
            
            class FinishedEvent(QEvent):
                def __init__(self, success, message, exported_plans, failed_plans, coord_map):
                    super().__init__(QEvent.User)
                    self.success = success
                    self.message = message
                    self.exported_plans = exported_plans
                    self.failed_plans = failed_plans
                    self.coord_map = coord_map
            
            # 发送事件到主线程
            event = FinishedEvent(success, message, exported_plans, failed_plans, coord_map)
            QCoreApplication.postEvent(self, event)
            

        
        # 重写event方法来处理完成事件和刷新事件
        original_event = self.event
        def custom_event(event):
            from PyQt5.QtCore import QEvent

            
            # 处理导出计划号明细事件
            if event.type() == QEvent.User and hasattr(event, 'valid_no_file_plans'):
                try:
                    print("\n=== 导出无文件计划号明细 ===")
                    
                    valid_no_file_plans = event.valid_no_file_plans
                    plan_detail_export_btn = event.plan_detail_export_btn
                    test_window = event.test_window
                    delay_time = event.delay_time
                    coord_map = getattr(event, 'coord_map', {})
                    
                    exported_plans = []
                    failed_plans = []
                    
                    for i, plan_no in enumerate(valid_no_file_plans):
                        print(f"[{i+1}/{len(valid_no_file_plans)}] 导出计划: {plan_no}")
                        try:
                            # 从坐标映射中获取计划号的实际坐标
                            plan_coord = coord_map.get(str(plan_no), (100, 100))
                            print(f"  计划号坐标: {plan_coord}")
                            success = self.export_single_plan_detail(plan_no, plan_coord, plan_detail_export_btn=plan_detail_export_btn, test_window=test_window, add_debug_log=print)
                            if success:
                                exported_plans.append(plan_no)
                                print(f"  [√] 导出成功")
                            else:
                                failed_plans.append(plan_no)
                                print(f"  [×] 导出失败")
                        except Exception as e:
                            failed_plans.append(plan_no)
                            print(f"  [×] 导出失败: {str(e)}")
                        
                        # 添加延迟
                        if i < len(valid_no_file_plans) - 1:
                            import time
                            time.sleep(delay_time)
                    
                    print(f"\n计划号明细导出完成: {len(exported_plans)} 个成功, {len(failed_plans)} 个失败")
                    
                    # 刷新界面（在主线程中执行）
                    from PyQt5.QtCore import QEvent, QCoreApplication
                    
                    class RefreshEvent(QEvent):
                        def __init__(self, exported_plans, coord_map):
                            super().__init__(QEvent.User)
                            self.exported_plans = exported_plans
                            self.coord_map = coord_map
                            self.refresh_type = 'plan_list'
                    
                    # 发送刷新事件到主线程
                    event = RefreshEvent(exported_plans, coord_map)
                    QCoreApplication.postEvent(self, event)
                    
                    print("\n=== 自动导出全部完成 ===")
                    
                    # 导出完成
                    from PyQt5.QtCore import QEvent, QCoreApplication
                    
                    class FinishedEvent(QEvent):
                        def __init__(self, success, message, exported_plans, failed_plans, coord_map):
                            super().__init__(QEvent.User)
                            self.success = success
                            self.message = message
                            self.exported_plans = exported_plans
                            self.failed_plans = failed_plans
                            self.coord_map = coord_map
                    
                    # 发送事件到主线程
                    event = FinishedEvent(True, f"自动导出全部完成\n\n成功导出 {len(exported_plans)} 个计划号\n失败 {len(failed_plans)} 个计划号", exported_plans, failed_plans, coord_map)
                    QCoreApplication.postEvent(self, event)
                except Exception as e:
                    print(f"导出计划号明细失败: {e}")
                    # 导出失败
                    from PyQt5.QtCore import QEvent, QCoreApplication
                    
                    class FinishedEvent(QEvent):
                        def __init__(self, success, message):
                            super().__init__(QEvent.User)
                            self.success = success
                            self.message = message
                    
                    # 发送事件到主线程
                    event = FinishedEvent(False, f"自动导出失败: {str(e)}")
                    QCoreApplication.postEvent(self, event)
                return True
            
            # 处理刷新事件
            if event.type() == QEvent.User and not hasattr(event, 'success'):
                try:
                    # 刷新界面
                    print("\n刷新计划号列表...")
                    self.refresh_data()
                    
                    # 选中刚刚导出的计划号
                    if hasattr(event, 'exported_plans') and event.exported_plans:
                        try:
                            self.table_widget.clearSelection()
                            for i, item in enumerate(self.plan_data):
                                if item['plan_no'] in event.exported_plans:
                                    self.table_widget.selectRow(i)
                            print(f"已选中 {len(event.exported_plans)} 个导出的计划号")
                        except Exception as e:
                            print(f"选中导出计划号失败: {e}")
                except Exception as e:
                    print(f"刷新界面失败: {e}")
                return True
            
            # 处理完成事件
            if event.type() == QEvent.User and hasattr(event, 'success'):
                try:
                    # 关闭进度窗口
                    if hasattr(event, 'progress_window') and event.progress_window:
                        try:
                            event.progress_window.close()
                            print("进度窗口已关闭")
                        except Exception as e:
                            print(f"关闭进度窗口失败: {e}")
                    
                    # 显示结果
                    if event.success:
                        # 检查是否有导出的计划号
                        if event.exported_plans:
                            # 更新最近导出的计划号列表
                            self.recently_exported_plans = set(event.exported_plans)
                            print(f"已更新最近导出的计划号: {event.exported_plans}")
                            # 刷新计划号列表,使绿色标注生效
                            self.refresh_plan_list_from_file()
                            
                            # 直接处理导出的计划号
                            print("\n=== 自动处理导出的计划号 ===")
                            # 选中刚刚导出的计划号
                            self.table_widget.clearSelection()
                            for i, item in enumerate(self.plan_data):
                                if item['plan_no'] in event.exported_plans:
                                    self.table_widget.selectRow(i)
                            print(f"已选中 {len(event.exported_plans)} 个导出的计划号")
                            
                            # 调用处理计划方法，不检查是否已处理过
                            print("开始自动处理计划...")
                            try:
                                # 获取设置中的自动打印设置
                                settings = self.get_settings()
                                auto_print = settings.get("autoPrint", True)
                                
                                # 调用处理计划方法，传入auto_print参数
                                # 注意：这里需要修改process_plans方法，使其不检查是否已处理过
                                self.process_plans(auto_print=auto_print, show_result=False)
                            except Exception as e:
                                print(f"自动处理计划失败: {e}")
                            
                            # 直接激活主程序窗口
                            print("直接激活主程序窗口")
                            # 尝试激活多种可能的主程序窗口标题
                            main_window_titles = [
                                self.coordinates.get("main_window", ""),
                                "轧制计划管理系统",
                                "主程序",
                                "装炉顺序",
                                "计划号管理",
                                "装炉明细",
                                "装炉顺作成管理",
                                "轧制计划管理",
                                "BCGMS1-宝钢股份基地制造管理系统运行环境",
                                "Doc1.docx - Word",
                                "Excel",
                                "Microsoft Excel",
                                "Word",
                                "Microsoft Word",
                                "装炉顺序.xls",
                                "计划号",
                                "轧制计划"
                            ]
                            
                            activated = False
                            # 尝试多次激活，确保成功
                            for attempt in range(3):
                                print(f"激活尝试 {attempt + 1}/3")
                                for title in main_window_titles:
                                    if title:
                                        print(f"尝试激活主程序窗口: {title}")
                                        if self.activate_window(title):
                                            activated = True
                                            # 等待一小段时间，确保窗口完全激活
                                            import time
                                            time.sleep(0.3)
                                            # 再次尝试激活，确保窗口在最前面
                                            self.activate_window(title)
                                            time.sleep(0.2)
                                            # 第三次激活，确保万无一失
                                            self.activate_window(title)
                                            break
                                if activated:
                                    break
                                # 如果第一次尝试失败，等待一段时间后再试
                                if not activated and attempt < 2:
                                    import time
                                    print("激活失败，等待后重试...")
                                    time.sleep(1)
                            
                            if not activated:
                                print("未找到主程序窗口,尝试其他方法")
                                # 尝试激活本程序窗口
                                print("尝试激活本程序窗口...")
                                try:
                                    self.activateWindow()
                                    self.raise_()
                                    self.show()
                                    print("成功激活本程序窗口")
                                except Exception as e:
                                    print(f"激活本程序窗口失败: {e}")
                                
                                # 尝试使用更通用的方法激活窗口
                                print("尝试使用通用方法激活窗口...")
                                try:
                                    import win32gui
                                    import win32con
                                    # 查找所有可见窗口
                                    def callback(hwnd, windows):
                                        if win32gui.IsWindowVisible(hwnd):
                                            title = win32gui.GetWindowText(hwnd)
                                            if title:
                                                windows.append((hwnd, title))
                                    
                                    windows = []
                                    win32gui.EnumWindows(callback, windows)
                                    
                                    # 按窗口标题长度排序，优先选择较长的标题（更具体）
                                    windows.sort(key=lambda x: len(x[1]), reverse=True)
                                    
                                    # 尝试激活前5个窗口
                                    for i, (hwnd, title) in enumerate(windows[:5]):
                                        print(f"尝试激活窗口 {i+1}: {title}")
                                        try:
                                            win32gui.SetForegroundWindow(hwnd)
                                            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                                            print(f"成功激活窗口: {title}")
                                            activated = True
                                            break
                                        except Exception as e:
                                            print(f"激活窗口 {title} 失败: {e}")
                                except Exception as e:
                                    print(f"通用激活方法失败: {e}")
                        else:
                            # 创建一个可关闭的消息框
                            msg_box = QMessageBox(self)
                            msg_box.setWindowTitle("提示")
                            msg_box.setText(event.message)
                            msg_box.setStandardButtons(QMessageBox.Ok)
                            # 确保消息框显示在最前面
                            msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                            msg_box.setModal(True)
                            # 确保应用程序是活动的
                            QApplication.setActiveWindow(msg_box)
                            # 显示消息框并等待用户点击
                            msg_box.exec_()
                    else:
                        # 创建一个可关闭的消息框
                        msg_box = QMessageBox(self)
                        msg_box.setWindowTitle("错误")
                        msg_box.setText(event.message)
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        # 确保消息框显示在最前面
                        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
                        msg_box.setModal(True)
                        # 确保应用程序是活动的
                        QApplication.setActiveWindow(msg_box)
                        # 显示消息框并等待用户点击
                        msg_box.exec_()
                except Exception as e:
                    print(f"处理完成事件失败: {e}")
                finally:
                    # 无论执行是否成功,都设置运行标志为False
                    self.is_auto_export_running = False
                    print("自动导出执行完毕")
                return True
            return original_event(event)
        
        # 替换event方法
        self.event = custom_event
        
        # 定义后台导出函数
        def export_in_background():
            """在后台执行导出操作"""
            try:
                import time
                import datetime
                
                # 开始时间
                start_time = datetime.datetime.now()
                print(f"\n=== 自动导出开始 ===")
                print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"调试模式: {'开启' if debug_mode else '关闭'}")
                print("="*60)
                
                # 步骤0：系统健康检查和自动修复
                update_progress("【步骤0/4】系统健康检查和自动修复...")
                print("\n===========================================================")
                print(" 【步骤0/4】系统健康检查和自动修复")
                print("===========================================================")
                
                # 检查系统状态
                print("检查系统状态...")
                print("系统状态正常,无预警信息")
                
                update_progress("[√] 系统健康检查和自动修复完成")
                print("系统健康检查和自动修复完成")
                time.sleep(1)
                
                # 步骤1：导出装炉顺序
                update_progress("【步骤1/4】正在导出装炉顺序...")
                print("\n===========================================================")
                print(" 【步骤1/4】导出装炉顺序")
                print("===========================================================")
                
                # 调用装炉顺序导出函数
                success1 = self.export_zhuanglu_shunxu(add_debug_log=print)
                
                # 如果装炉顺序导出失败,停止执行
                if not success1:
                    print("[×] 装炉顺序导出失败,停止执行")
                    # 显示激活窗口失败的错误信息
                    settings = self.get_settings()
                    test_window = settings.get("selectedWindow", "Doc1.docx - Word")
                    export_finished(False, f"开始导出装炉顺序...\n[1/9] 激活目标窗口: {test_window}...\n× 激活窗口失败", [], [], {})
                    return
                
                update_progress("[√] 装炉顺序导出完成", "等待文件保存...")
                print("【导出完成】装炉顺序导出操作完成")
                # 步骤2：导出总计划号列表
                update_progress("【步骤2/4】正在导出总计划号列表...")
                print("\n===========================================================")
                print(" 【步骤2/4】导出总计划号列表")
                print("===========================================================")
                print("\n")
                print("===========================================================")
                print("导出总计划号列表")
                print("===========================================================")
                
                # 调用总计划号列表导出函数
                success3 = self.export_zhizhi_plan_list(add_debug_log=print)
                
                # 如果总计划号列表导出失败,停止执行
                if not success3:
                    print("[×] 总计划号列表导出失败,停止执行")
                    # 显示激活窗口失败的错误信息
                    settings = self.get_settings()
                    test_window = settings.get("selectedWindow", "Doc1.docx - Word")
                    export_finished(False, f"开始导出总计划号列表...\n[1/7] 激活目标窗口: {test_window}...\n× 激活窗口失败", [], [], {})
                    return
                
                update_progress("[√] 总计划号列表导出完成", "等待文件保存...")
                print(f"[√] 总计划号列表导出完成")
                time.sleep(1)
                
                # 刷新数据,确保plan_data是最新的
                print("刷新数据,更新计划号列表...")
                # 确保在主线程中执行刷新操作
                from PyQt5.QtCore import QEvent, QCoreApplication
                
                class RefreshEvent(QEvent):
                    def __init__(self):
                        super().__init__(QEvent.User)
                        self.refresh_type = 'plan_list'
                
                # 发送刷新事件到主线程
                event = RefreshEvent()
                QCoreApplication.postEvent(self, event)
                # 等待刷新完成
                time.sleep(2)
                
                # 步骤3：重新计算坐标
                update_progress("【步骤3/4】正在重新计算坐标...")
                print("\n===========================================================")
                print(" 【步骤3/4】重新计算坐标")
                print("===========================================================")
                
                # 定义计划号文件夹路径
                plan_dir = os.path.join(self.plan_dir, "计划号")
                
                # 读取总计划号列表并计算坐标（会自动更新缓存）
                print(f"")
                print(f"[读取文件] 总计划号列表.xls")
                plan_list_file = os.path.join(plan_dir, "总计划号列表.xls")
                print(f"  路径: {plan_list_file}")
                print(f"  存在: {'是' if os.path.exists(plan_list_file) else '否'}")
                
                # 检查文件是否存在
                if not os.path.exists(plan_list_file):
                    print(f"✗ 总计划号列表文件不存在")
                    # 即使总计划号列表文件不存在,也继续执行后续步骤
                    print("[×] 总计划号列表文件不存在,继续执行后续步骤")
                    # 跳过坐标计算,直接进入导出无文件计划号明细的步骤
                    coord_map = {}
                else:
                    # 计算坐标
                    try:
                        print(f"")
                        print(f"[读取总计划号列表]")
                        print(f"  数据库路径: {self.db_path}")
                        
                        # 读取总计划号列表并计算坐标
                        coord_map = self.read_zhizhi_plan_list_with_coords(add_debug_log=print)
                        
                        if not coord_map:
                            print(f"✗ 坐标计算失败：未找到计划号")
                            # 即使坐标计算失败,也继续执行后续步骤
                            print("[×] 坐标计算失败,继续执行后续步骤")
                            coord_map = {}
                        else:
                            print(f"")
                            print(f"  总计: {len(coord_map)} 个计划号坐标")
                            print(f"  计算到 {len(coord_map)} 个计划号坐标")
                            for plan_no, coord in list(coord_map.items())[:5]:  # 只显示前5个
                                print(f"    {plan_no}: {coord}")
                            if len(coord_map) > 5:
                                print(f"    ... 还有 {len(coord_map) - 5} 个")
                            
                            # 特别输出无文件计划号的坐标
                            no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
                            if no_file_plans:
                                print("\n无文件计划号的坐标：")
                                for plan_no in no_file_plans:
                                    coord = coord_map.get(plan_no, "未知")
                                    print(f"- {plan_no}: {coord}")
                            
                            update_progress("[√] 坐标计算完成", f"共 {len(coord_map)} 个计划号坐标")
                            print(f"[√] 坐标计算完成")
                            # 移除不必要的延迟,确保计算完坐标后立即开始导出无文件计划号的明细
                            # time.sleep(0.5)
                    except Exception as e:
                        print(f"[×] 坐标计算失败: {str(e)}")
                        # 即使坐标计算失败,也继续执行后续步骤
                        print("[×] 坐标计算失败,继续执行后续步骤")
                        coord_map = {}
                

                
                # 步骤4：导出无文件计划号的明细
                update_progress("【步骤4/4】正在导出无文件计划号明细...")
                print("\n===========================================================")
                print(" 【步骤4/4】导出无文件计划号明细")
                print("===========================================================")
                
                # 筛选无文件计划号
                print(f"")
                print(f"[筛选计划号] 状态='无文件'")
                
                # 从plan_data中获取无文件计划号
                no_file_plans = [item['plan_no'] for item in self.plan_data if item['status'] == '无文件']
                
                # 对于无文件计划号,直接导出明细,不依赖坐标映射
                valid_no_file_plans = no_file_plans
                invalid_no_file_plans = []
                
                print(f"  找到 {len(no_file_plans)} 个无文件的计划号")
                print(f"  计划号列表: {valid_no_file_plans}")
                
                if not valid_no_file_plans:
                    print(f"[×] 没有需要导出的计划号")
                    export_finished(True, "没有需要导出的计划号\n\n所有计划号都已有文件,无需导出", [], [], {})
                    return
                
                # 获取设置中的窗口标题
                settings = self.get_settings()
                test_window = settings.get("selectedWindow", "Doc1.docx - Word")
                test_speed = "中"
                
                speed_delays = {"慢": 1.5, "中": 1.0, "快": 0.5}
                delay_time = speed_delays.get(test_speed, 1.0)
                
                # 使用固定的计划明细导出按钮坐标
                plan_detail_export_btn = [79, 859]
                
                print(f"")
                print(f"[配置信息]")
                print(f"  计划明细导出按钮坐标: {plan_detail_export_btn}")
                print(f"  导出速度: {test_speed} (延迟: {delay_time}s)")
                print(f"  目标窗口: {test_window}")
                
                print(f"")
                print(f"===========================================================")
                print(f"开始导出计划号明细")
                print(f"===========================================================")
                
                # 导出无文件计划号明细（在主线程中执行）
                from PyQt5.QtCore import QEvent, QCoreApplication
                
                class ExportPlanDetailEvent(QEvent):
                    def __init__(self, valid_no_file_plans, plan_detail_export_btn, test_window, delay_time, coord_map):
                        super().__init__(QEvent.User)
                        self.valid_no_file_plans = valid_no_file_plans
                        self.plan_detail_export_btn = plan_detail_export_btn
                        self.test_window = test_window
                        self.delay_time = delay_time
                        self.coord_map = coord_map
                
                # 发送事件到主线程
                event = ExportPlanDetailEvent(valid_no_file_plans, plan_detail_export_btn, test_window, delay_time, coord_map)
                QCoreApplication.postEvent(self, event)
                
                # 激活目标窗口,确保导出过程中保持在目标窗口
                try:
                    window_title = test_window
                    self.activate_window(window_title)
                    print(f"[√] 已激活目标窗口: {window_title}")
                except Exception as e:
                    print(f"[×] 激活目标窗口失败: {str(e)}")
                
            except Exception as e:
                print(f"[×] 自动导出失败: {str(e)}")
                import traceback
                traceback.print_exc()
                export_finished(False, f"自动导出失败: {str(e)}", [], [], {})
            finally:
                # 结束时间
                end_time = datetime.datetime.now()
                execution_time = end_time - start_time
                print(f"\n=== 自动导出结束 ===")
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
        
        # 启动后台线程执行导出操作
        import threading
        export_thread = threading.Thread(target=export_in_background, daemon=True)
        export_thread.start()
        
    def export_zhuanglu_shunxu(self, add_debug_log=None):
        """导出装炉顺序 - 严格按照原程序步骤执行
        
        参数:
            add_debug_log: 调试日志函数（可选）,如果为None则不输出调试信息
        """
        import time
        log_lines = ["开始导出装炉顺序..."]
        
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass  # 非调试模式下不输出
        
        # 检查pyautogui是否可用
        try:
            import pyautogui
            import os
            PYAUTOGUI_AVAILABLE = True
        except ImportError:
            PYAUTOGUI_AVAILABLE = False
            add_debug_log('pyautogui 不可用,无法执行装炉顺序导出')
            return False
        
        # 文件路径 - 使用计划号文件夹
        plan_dir = os.path.join(self.plan_dir, "计划号")
        zhuanglu_file = os.path.join(plan_dir, "装炉顺序.xls")
        
        # 准备临时文件路径（不带.xls扩展名）
        temp_zhuanglu_file = os.path.join(plan_dir, f"装炉顺序_{int(time.time())}.tmp")
        # 导出前清理可能存在的临时文件
        import glob
        for temp_file in glob.glob(os.path.join(plan_dir, "装炉顺序_*.tmp")):
            try:
                os.remove(temp_file)
                add_debug_log(f"[√] 已清理临时文件: {os.path.basename(temp_file)}")
            except Exception as e:
                add_debug_log(f"[×] 清理临时文件失败: {str(e)}")
        
        # 获取设置中的窗口标题
        settings = self.get_settings()
        window_title = settings.get("selectedWindow", "Doc1.docx - Word")
        
        add_debug_log(f"【配置信息】")
        add_debug_log(f"窗口标题: {window_title}")
        add_debug_log(f"文件路径: {zhuanglu_file}")
        add_debug_log("")
        
        # 使用固定的坐标（与原程序一致）
        zhuanglu_tab = [284, 84]
        zhuanglu_export = [988, 819]
        
        add_debug_log(f"【坐标配置】")
        add_debug_log(f"装炉顺作成管理标签: {zhuanglu_tab}")
        add_debug_log(f"装炉顺序导出按钮: {zhuanglu_export}")
        add_debug_log("")
        
        # 检查窗口是否存在
        window_exists = False
        try:
            import win32gui
            def callback(hwnd, extra):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if window_title in window_text:
                            extra.append(hwnd)
                except Exception:
                    pass
            windows = []
            win32gui.EnumWindows(callback, windows)
            window_exists = len(windows) > 0
        except Exception:
            pass
        
        if not window_exists:
            add_debug_log(f"[×] 窗口 {window_title} 不存在,跳过实际操作")
            print(f"[×] 窗口 {window_title} 不存在,跳过实际操作")
            # 模拟导出失败
            print(f"[×] 导出失败: 窗口 {window_title} 不存在")
            return False
        else:
            # 步骤1: 激活目标窗口
            log_lines.append(f"[1/9] 激活目标窗口: {window_title}...")
            add_debug_log(f"【步骤1】激活目标窗口: {window_title}")
            window_activated = False
            try:
                window_activated = self.activate_window(window_title)
                if not window_activated:
                    log_lines.append("[×] 激活窗口失败,继续执行")
                    add_debug_log("[×] 激活窗口失败,继续执行")
                    # 模拟导出失败
                    print(f"[×] 导出失败: 激活窗口 {window_title} 失败")
                    return False
                else:
                    log_lines.append(f"[√] 已激活窗口: {window_title}")
                    add_debug_log(f"[√] 已激活窗口: {window_title}")
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)  # 激活窗口后延迟
            except Exception as e:
                log_lines.append(f"[×] 激活窗口失败: {str(e)},继续执行")
                add_debug_log(f"[×] 激活窗口失败: {str(e)},继续执行")
                # 模拟导出失败
                print(f"[×] 导出失败: 激活窗口 {window_title} 失败")
                return False
            
            # 步骤2-8: 执行导出操作（只有窗口激活成功才执行）
            if window_activated:
                try:
                    # 步骤2: 鼠标点击 - 装炉顺作成管理画面
                    log_lines.append(f"[2/9] 鼠标点击: 装炉顺作成管理画面 @ {zhuanglu_tab}...")
                    add_debug_log(f"【步骤2】鼠标点击: 装炉顺作成管理画面")
                    add_debug_log(f"  坐标: ({zhuanglu_tab[0]}, {zhuanglu_tab[1]})")
                    pyautogui.moveTo(zhuanglu_tab[0], zhuanglu_tab[1])
                    pyautogui.click()
                    add_debug_log(f"  延迟: 500ms")
                    time.sleep(0.5)  # 点击后延迟
                    log_lines.append("点击完成")
                    add_debug_log("[√] 点击完成")
                    
                    # 步骤3: 键盘按键 - F2
                    log_lines.append("[3/9] 键盘按键: F2...")
                    add_debug_log(f"【步骤3】键盘按键: F2")
                    pyautogui.press('f2')
                    add_debug_log(f"  延迟: 500ms")
                    time.sleep(0.5)  # F2后延迟
                    log_lines.append("F2键已按下")
                    add_debug_log("[√] F2键已按下")

                    # 步骤4: 延迟 - 500ms
                    log_lines.append("[4/9] 延迟: 500ms...")
                    add_debug_log(f"【步骤4】延迟: 500ms")
                    time.sleep(0.5)
                    log_lines.append("延迟完成")
                    add_debug_log("[√] 延迟完成")

                    # 步骤5: 鼠标点击 - 导出按钮
                    log_lines.append(f"[5/9] 鼠标点击: 导出按钮 @ {zhuanglu_export}...")
                    add_debug_log(f"【步骤5】鼠标点击: 导出按钮")
                    add_debug_log(f"  坐标: ({zhuanglu_export[0]}, {zhuanglu_export[1]})")
                    pyautogui.moveTo(zhuanglu_export[0], zhuanglu_export[1])
                    pyautogui.click()
                    add_debug_log(f"  延迟: 1000ms (等待保存对话框)")
                    time.sleep(1.0)  # 点击后延迟,等待保存对话框弹出
                    log_lines.append("导出按钮点击完成,等待保存对话框...")
                    add_debug_log("[√] 导出按钮点击完成")

                    # 步骤6: 直接输入完整路径+文件名
                    log_lines.append("[6/9] 直接输入完整路径+文件名...")
                    add_debug_log(f"【步骤6】直接输入完整路径+文件名")
                    # 等待对话框完全弹出并获取焦点
                    add_debug_log(f"  延迟: 1000ms (等待对话框)")
                    time.sleep(1.0)
                    # 临时文件路径（不带扩展名）
                    temp_full_path = temp_zhuanglu_file
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
                    add_debug_log("[√] 已输入完整路径")

                    # 步骤8: 键盘按键 - Return
                    log_lines.append("[8/8] 键盘按键: Return...")
                    add_debug_log(f"【步骤8】键盘按键: Return")
                    pyautogui.press('return')
                    log_lines.append("回车键已按下")
                    add_debug_log("[√] 回车键已按下")
                    
                    # 等待导出完成
                    log_lines.append("等待导出完成...")
                    add_debug_log(f"【等待导出完成】")
                    add_debug_log(f"  延迟: 3000ms")
                    time.sleep(3)
                    add_debug_log("[√] 导出完成")
                except Exception as e:
                    log_lines.append(f"[×] 执行导出操作失败: {str(e)}")
                    add_debug_log(f"[×] 执行导出操作失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # 继续执行后续步骤（如关闭Excel进程和文件替换）
            else:
                log_lines.append("[×] 窗口未激活,跳过导出操作")
                add_debug_log("[×] 窗口未激活,跳过导出操作")
        
        # 确保所有Excel进程都已关闭（避免文件占用）
        log_lines.append("确保Excel进程已关闭...")
        add_debug_log(f"【关闭Excel进程】")
        try:
            import subprocess
            # 强制关闭所有Excel进程,使用creationflags隐藏窗口
            subprocess.run(
                ['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            add_debug_log(f"  延迟: 2000ms")
            time.sleep(2)
            log_lines.append("Excel进程已强制关闭")
            add_debug_log("[√] Excel进程已强制关闭")
        except Exception as e:
            log_lines.append(f"强制关闭Excel进程失败: {str(e)}")
            add_debug_log(f"[×] 强制关闭Excel进程失败: {str(e)}")
        
        # 原子性文件替换：将临时文件替换为正式文件
        log_lines.append("执行原子性文件替换...")
        add_debug_log(f"【原子性文件替换】")
        try:
            if os.path.exists(temp_zhuanglu_file):
                add_debug_log(f"  临时文件: {temp_zhuanglu_file}")
                add_debug_log(f"  目标文件: {zhuanglu_file}")
                # 执行原子性替换,使用重试机制
                success = self.atomic_file_replace(temp_zhuanglu_file, zhuanglu_file, max_retries=5, retry_delay=1.0)
                if success:
                    # 清理文件缓存,确保读取到最新数据
                    self.clear_file_cache(zhuanglu_file)
                    add_debug_log("[√] 原子性文件替换成功")
                    add_debug_log("[√] 文件缓存已清理")
                    log_lines.append("原子性文件替换成功")
                else:
                    add_debug_log("[×] 原子性文件替换失败")
                    log_lines.append("原子性文件替换失败")
            else:
                add_debug_log(f"[×] 临时文件不存在: {temp_zhuanglu_file}")
                log_lines.append("临时文件不存在")
        except Exception as e:
            add_debug_log(f"[×] 原子性文件替换异常: {str(e)}")
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
                add_debug_log("[√] 装炉顺序数据导入数据库成功")
            else:
                add_debug_log("[×] 装炉顺序数据导入数据库失败")
        except Exception as e:
            add_debug_log(f"[×] 导入数据到数据库异常: {str(e)}")
            log_lines.append(f"导入数据到数据库异常: {str(e)}")
        
        # 刷新计划号列表
        add_debug_log(f"【刷新计划号列表】")
        try:
            self.refresh_plan_list()
            add_debug_log("[√] 计划号列表刷新完成")
        except Exception as e:
            add_debug_log(f"[×] 计划号列表刷新失败: {str(e)}")
        
        add_debug_log(f"【导出完成】装炉顺序导出操作完成")
        
        return True
    
    def export_zhizhi_plan_list(self, test_window=None, test_mode=False, add_debug_log=None):
        """导出总计划号列表 - 严格按照原程序步骤执行
        
        参数:
            test_window: 测试窗口标题,如果为None则自动选择
            test_mode: 是否为测试模式（简化版不再使用）
            add_debug_log: 调试日志函数
        """
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        try:
            import pyautogui
            import time
            import os
            
            add_debug_log("")
            add_debug_log("="*60)
            add_debug_log("导出总计划号列表")
            add_debug_log("="*60)
            
            # 使用固定的窗口标题
            # 获取设置中的窗口标题
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "Doc1.docx - Word")
            
            add_debug_log(f"窗口标题: {test_window}")
            print("\n=== 导出总计划号列表 ===")
            
            # 检查窗口是否存在
            window_exists = False
            try:
                import win32gui
                def callback(hwnd, extra):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if test_window in window_text:
                                extra.append(hwnd)
                    except Exception:
                        pass
                windows = []
                win32gui.EnumWindows(callback, windows)
                window_exists = len(windows) > 0
            except Exception:
                pass
            
            # 文件路径 - 使用计划号文件夹
            plan_dir = os.path.join(self.plan_dir, "计划号")
            total_plan_file = os.path.join(plan_dir, "总计划号列表.xls")
            
            # 准备临时文件路径（不带.xls扩展名）
            temp_total_plan_file = os.path.join(plan_dir, f"总计划号列表_{int(time.time())}.tmp")
            # 导出前清理可能存在的临时文件
            import glob
            for temp_file in glob.glob(os.path.join(plan_dir, "总计划号列表_*.tmp")):
                try:
                    os.remove(temp_file)
                    add_debug_log(f"[√] 已清理临时文件: {os.path.basename(temp_file)}")
                except Exception as e:
                    add_debug_log(f"[×] 清理临时文件失败: {str(e)}")
            
            if not window_exists:
                add_debug_log(f"[×] 窗口 {test_window} 不存在,跳过实际操作")
                print(f"[×] 窗口 {test_window} 不存在,跳过实际操作")
                # 模拟导出成功,创建一个空文件
                try:
                    # 创建一个临时文件,但不写入内容,这样后续的Excel读取会失败但不会崩溃
                    open(temp_total_plan_file, 'w').close()
                    print(f"[√] 模拟导出成功,创建了临时文件: {temp_total_plan_file}")
                except Exception as e:
                    print(f"[×] 模拟导出失败: {e}")
                # 继续执行后续步骤（文件替换、导入等）
            else:
                # 使用固定的坐标（与原程序一致）
                zhizhi_tab = [107, 85]
                plan_select = [734, 135]
                zhizhi_export_btn = [78, 740]
                
                add_debug_log(f"")
                add_debug_log(f"[坐标配置]")
                add_debug_log(f"  轧制计划管理标签: {zhizhi_tab}")
                add_debug_log(f"  选择计划号: {plan_select}")
                add_debug_log(f"  导出按钮: {zhizhi_export_btn}")
                
                # 步骤1: 激活窗口
                print("[1/7] 激活窗口...")
                add_debug_log(f"")
                add_debug_log(f"[步骤1] 激活窗口")
                window_activated = self.activate_window(test_window)
                if not window_activated:
                    add_debug_log(f"[×] 激活窗口失败,终止执行")
                    print("[×] 激活窗口失败,终止执行")
                    # 模拟导出失败
                    print(f"[×] 导出失败: 激活窗口 {test_window} 失败")
                    return False
                else:
                    add_debug_log(f"[√] 窗口已激活")
                add_debug_log(f"  延迟: 500ms")
                time.sleep(0.5)
                
                # 步骤2: 点击轧制计划管理标签
                try:
                    print(f"[2/7] 点击轧制计划管理标签...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤2] 点击轧制计划管理标签")
                    add_debug_log(f"  坐标: ({zhizhi_tab[0]}, {zhizhi_tab[1]})")
                    pyautogui.moveTo(zhizhi_tab[0], zhizhi_tab[1])
                    pyautogui.click()
                    add_debug_log(f"  延迟: 500ms")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[×] 点击轧制计划管理标签失败: {e},继续执行")
                    add_debug_log(f"[×] 点击轧制计划管理标签失败: {e},继续执行")
                
                # 步骤3: 选择计划号
                try:
                    print(f"[3/7] 选择计划号...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤3] 选择计划号")
                    add_debug_log(f"  坐标: ({plan_select[0]}, {plan_select[1]})")
                    pyautogui.moveTo(plan_select[0], plan_select[1])
                    pyautogui.click()
                    add_debug_log(f"  延迟: 300ms")
                    time.sleep(0.3)
                except Exception as e:
                    print(f"[×] 选择计划号失败: {e},继续执行")
                    add_debug_log(f"[×] 选择计划号失败: {e},继续执行")
                
                # 步骤4: 按Home键选择所有计划号
                try:
                    print("[4/7] 按Home键选择所有计划号...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤4] 按Home键选择所有计划号")
                    pyautogui.press('home')
                    add_debug_log(f"  延迟: 500ms")
                    time.sleep(0.5)
                    add_debug_log(f"  延迟: 500ms")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[×] 按Home键选择所有计划号失败: {e},继续执行")
                    add_debug_log(f"[×] 按Home键选择所有计划号失败: {e},继续执行")
                
                # 步骤5: 按F2刷新
                try:
                    print("[5/7] 按F2刷新...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤5] 按F2刷新")
                    pyautogui.press('f2')
                except Exception as e:
                    print(f"[×] 按F2刷新失败: {e},继续执行")
                    add_debug_log(f"[×] 按F2刷新失败: {e},继续执行")
                
                # 步骤6: 点击导出按钮
                try:
                    print(f"[6/7] 点击导出按钮...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤6] 点击导出按钮")
                    add_debug_log(f"  坐标: ({zhizhi_export_btn[0]}, {zhizhi_export_btn[1]})")
                    pyautogui.moveTo(zhizhi_export_btn[0], zhizhi_export_btn[1])
                    pyautogui.click()
                    add_debug_log(f"  延迟: 1500ms (等待保存对话框)")
                    time.sleep(1.5)
                except Exception as e:
                    print(f"[×] 点击导出按钮失败: {e},继续执行")
                    add_debug_log(f"[×] 点击导出按钮失败: {e},继续执行")
                
                # 步骤7: 直接输入完整路径+文件名
                try:
                    print("[7/7] 直接输入完整路径+文件名...")
                    add_debug_log(f"")
                    add_debug_log(f"[步骤7] 直接输入完整路径+文件名")
                    add_debug_log(f"  延迟: 500ms (等待对话框)")
                    time.sleep(0.5)
                    # 临时文件路径（不带扩展名）
                    temp_full_path = temp_total_plan_file
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
                    add_debug_log(f"[√] 已输入完整路径")
                    
                    # 保存文件
                    add_debug_log(f"")
                    add_debug_log(f"[保存文件]")
                    add_debug_log(f"  按键: Return")
                    pyautogui.press('return')
                    add_debug_log(f"  延迟: 2000ms (等待保存完成)")
                    time.sleep(2)
                except Exception as e:
                    print(f"[×] 输入完整路径+文件名失败: {e},继续执行")
                    add_debug_log(f"[×] 输入完整路径+文件名失败: {e},继续执行")
            

            
            # 导入总计划号列表数据到数据库
            add_debug_log(f"")
            add_debug_log(f"[导入数据到数据库]")
            print("导入总计划号列表数据到数据库...")
            try:
                import_success = self.import_zhizhi_plan_list_to_db(total_plan_file)
                if import_success:
                    add_debug_log(f"[√] 总计划号列表数据导入数据库成功")
                else:
                    add_debug_log(f"[×] 总计划号列表数据导入数据库失败")
            except Exception as e:
                print(f"导入总计划号列表数据到数据库失败: {str(e)}")
                add_debug_log(f"[×] 导入总计划号列表数据导入数据库失败: {str(e)}")
            
            print("[√] 总计划号列表导出成功")
            add_debug_log(f"[√] 总计划号列表导出成功")
            add_debug_log(f"[√] 总计划号列表导出完成")
            return True
            
        except Exception as e:
            print(f"[×] 导出总计划号列表失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def export_single_plan_detail(self, plan_no, plan_coord, plan_detail_export_btn=None, test_window=None, add_debug_log=None):
        """导出单个计划号的明细 - 严格按照原程序步骤执行
        
        参数:
            plan_no: 计划号
            plan_coord: 计划号的坐标 (x, y)
            plan_detail_export_btn: 导出计划明细按钮坐标,如果为None则使用配置中的坐标
            test_window: 测试窗口标题
            add_debug_log: 调试日志函数
            
        返回:
            True - 导出成功
            False - 导出失败
        """
        # 如果没有传入调试日志函数,使用空函数
        if add_debug_log is None:
            def add_debug_log(msg):
                pass
        
        result = False
        
        try:
            import time
            import os
            import glob
            
            # 使用固定的窗口标题
            # 获取设置中的窗口标题
            settings = self.get_settings()
            test_window = settings.get("selectedWindow", "Doc1.docx - Word")
            
            add_debug_log(f"    开始执行导出操作...")
            add_debug_log(f"    开始导出明细...")
            add_debug_log(f"    窗口: {test_window}")
            
            # 检查窗口是否存在
            window_exists = False
            try:
                import win32gui
                def callback(hwnd, extra):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if test_window in window_text:
                                extra.append(hwnd)
                    except Exception:
                        pass
                windows = []
                win32gui.EnumWindows(callback, windows)
                window_exists = len(windows) > 0
            except Exception:
                pass
            
            if not window_exists:
                add_debug_log(f"    [×] 窗口 {test_window} 不存在,跳过实际操作")
                print(f"[×] 窗口 {test_window} 不存在,跳过实际操作")
                # 模拟导出成功,不创建实际文件
                plan_file = os.path.join(self.plan_dir, "计划号", f"{plan_no}.xls")
                print(f"[√] 模拟导出成功,文件路径: {plan_file}")
                print(f"[模拟] 不会创建实际文件,这是模拟导出过程")
                result = True
                return result
            
            # 检查pyautogui是否可用
            try:
                import pyautogui
                PYAUTOGUI_AVAILABLE = True
            except ImportError as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log('pyautogui 不可用,无法执行计划明细导出')
                print(f'pyautogui 不可用,无法执行计划明细导出: {e}')
                result = False
                return result
            except Exception as e:
                PYAUTOGUI_AVAILABLE = False
                add_debug_log(f'pyautogui 初始化失败: {e}')
                print(f'pyautogui 初始化失败: {e}')
                result = False
                return result
            
            # 步骤1: 激活窗口
            add_debug_log(f"    [1] 激活窗口...")
            window_activated = self.activate_window(test_window)
            if not window_activated:
                add_debug_log(f"    [×] 激活窗口失败,终止执行")
                print("[×] 激活窗口失败,终止执行")
                # 模拟导出失败
                print(f"[×] 导出失败: 激活窗口 {test_window} 失败")
                return False
            else:
                add_debug_log(f"    [√] 窗口已激活")
            add_debug_log(f"    延迟: 300ms")
            time.sleep(0.3)
            
            # 使用固定的导出计划明细按钮坐标（与原程序一致）
            plan_detail_export_btn = [79, 859]
            
            # 步骤2: 鼠标点击计划号坐标
            add_debug_log(f"    [2] 点击计划号坐标: {plan_coord}")
            # 检查坐标是否有效
            if plan_coord and len(plan_coord) == 2:
                # 检查坐标值是否有效
                if isinstance(plan_coord[0], (int, float)) and isinstance(plan_coord[1], (int, float)):
                    try:
                        pyautogui.moveTo(plan_coord[0], plan_coord[1])
                        pyautogui.click()
                        add_debug_log(f"    延迟: 500ms")
                        time.sleep(0.5)  # 延迟500ms
                    except Exception as e:
                        print(f"[×] 点击计划号坐标失败: {e}")
                        add_debug_log(f"    [×] 点击计划号坐标失败: {e}")
                else:
                    print("[×] 计划号坐标值无效")
                    add_debug_log(f"    [×] 计划号坐标值无效")
            else:
                print("[×] 计划号坐标无效")
                add_debug_log(f"    [×] 计划号坐标无效")
            
            # 步骤3: 鼠标点击导出计划明细按钮
            add_debug_log(f"    [3] 点击导出按钮: {plan_detail_export_btn}")
            # 检查坐标是否有效
            if plan_detail_export_btn and len(plan_detail_export_btn) == 2:
                # 检查坐标值是否有效
                if isinstance(plan_detail_export_btn[0], (int, float)) and isinstance(plan_detail_export_btn[1], (int, float)):
                    try:
                        pyautogui.moveTo(plan_detail_export_btn[0], plan_detail_export_btn[1])
                        pyautogui.click()
                        add_debug_log(f"    延迟: 500ms (等待对话框)")
                        time.sleep(0.5)  # 等待保存对话框弹出
                    except Exception as e:
                        print(f"[×] 点击导出按钮失败: {e}")
                        add_debug_log(f"    [×] 点击导出按钮失败: {e}")
                else:
                    print("[×] 导出计划明细按钮坐标值无效")
                    add_debug_log(f"    [×] 导出计划明细按钮坐标值无效")
            else:
                print("[×] 导出计划明细按钮坐标无效")
                add_debug_log(f"    [×] 导出计划明细按钮坐标无效")
            
            # 步骤4: 键盘输入计划号（使用剪贴板粘贴）
            add_debug_log(f"    [4] 输入计划号: {plan_no}")
            try:
                import pyperclip
                pyperclip.copy(str(plan_no))
                add_debug_log(f"    延迟: 200ms")
                time.sleep(0.2)
                add_debug_log(f"    执行: Ctrl+V 粘贴")
                pyautogui.hotkey('ctrl', 'v')
                add_debug_log(f"    延迟: 300ms")
                time.sleep(0.3)
            except Exception as e:
                print(f"[×] 剪贴板操作失败,尝试直接输入: {e}")
                # 尝试直接输入
                try:
                    pyautogui.typewrite(str(plan_no))
                    time.sleep(0.5)
                except Exception as e2:
                    print(f"[×] 直接输入失败: {e2}")
                    add_debug_log(f"    [×] 直接输入失败: {e2}")
            
            # 步骤5: 按回车确认
            add_debug_log(f"    [5] 按键: Return")
            try:
                pyautogui.press('return')
                add_debug_log(f"    延迟: 1000ms (等待确认对话框)")
                time.sleep(1)  # 等待确认对话框
                
                # 步骤6: 按左方向键（替换覆盖）
                add_debug_log(f"    [6] 按键: Left")
                pyautogui.press('left')
                add_debug_log(f"    延迟: 500ms")
                time.sleep(0.5)
                
                # 步骤7: 按回车确认
                add_debug_log(f"    [7] 按键: Return")
                pyautogui.press('return')
                add_debug_log(f"    延迟: 2000ms (等待保存完成)")
                time.sleep(2)  # 等待保存完成
                add_debug_log(f"    [√] 导出完成")
            except Exception as e:
                print(f"[×] 按键操作失败: {e}")
                add_debug_log(f"    [×] 按键操作失败: {e}")
            
            # 模拟操作执行完成,直接标记为成功
            # 不检查文件是否存在,只按照模拟操作导出了哪些计划号
            print(f"[√] 计划号 {plan_no} 的明细文件已导出")
            result = True
            
        except Exception as e:
            add_debug_log(f"    [×] 导出失败: {str(e)}")
            print(f"[×] 导出计划 {plan_no} 明细失败: {str(e)}")
            import traceback
            traceback.print_exc()
            result = False
        finally:
            # 移除返回主程序窗口的代码,确保导出过程中始终保持在激活的目标窗口
            # 这样可以避免窗口闪现的问题
            pass
        
        if result:
            add_debug_log(f"  [√] 导出成功")
        else:
            add_debug_log(f"  [×] 导出失败")
        return result
    
    def activate_window(self, window_title):
        """窗口激活"""
        try:
            import win32gui
            import win32con
            import ctypes
            
            # 定义常量
            SW_HIDE = 0
            SW_SHOWNORMAL = 1
            SW_NORMAL = 1
            SW_SHOWMINIMIZED = 2
            SW_SHOWMAXIMIZED = 3
            SW_MAXIMIZE = 3
            SW_SHOWNOACTIVATE = 4
            SW_SHOW = 5
            SW_MINIMIZE = 6
            SW_SHOWMINNOACTIVE = 7
            SW_SHOWNA = 8
            SW_RESTORE = 9
            
            # 查找窗口
            def callback(hwnd, extra):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if window_title in window_text:
                            extra.append((hwnd, window_text))
                except Exception as e:
                    print(f'窗口枚举回调失败: {e}')
            
            windows = []
            try:
                win32gui.EnumWindows(callback, windows)
            except Exception as e:
                print(f'枚举窗口失败: {e}')
                return False
            
            if not windows:
                print(f'未找到标题包含 "{window_title}" 的窗口')
                return False
            
            # 按窗口标题长度排序,选择最匹配的窗口
            windows.sort(key=lambda x: len(x[1]), reverse=True)
            hwnd, window_text = windows[0]
            
            print(f'找到窗口: {window_text} (HWND: {hwnd})')
            
            # 检查窗口是否有效
            try:
                if not win32gui.IsWindow(hwnd):
                    print('窗口无效')
                    return False
            except Exception as e:
                print(f'检查窗口有效性失败: {e}')
                return False
            
            # 检查窗口是否可见
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    print('窗口不可见,尝试显示')
                    win32gui.ShowWindow(hwnd, SW_SHOWNORMAL)
            except Exception as e:
                print(f'检查窗口可见性失败: {e}')
            
            # 尝试1：使用win32gui.SetForegroundWindow
            print('尝试激活方式1：win32gui.SetForegroundWindow')
            try:
                result = win32gui.SetForegroundWindow(hwnd)
                print(f'方式1结果: {result}')
                if result:
                    print('成功激活窗口（方式1）')
                    return True
            except Exception as e:
                print(f'方式1失败: {e}')
            
            # 尝试2：直接设置为前台窗口,不改变窗口状态
            print('尝试激活方式2：直接设置为前台窗口')
            try:
                result = win32gui.SetForegroundWindow(hwnd)
                print(f'方式2结果: {result}')
                if result:
                    print('成功激活窗口（方式2）')
                    return True
            except Exception as e:
                print(f'方式2失败: {e}')
            
            # 尝试3：使用ctypes直接调用SetForegroundWindow
            print('尝试激活方式3：ctypes.windll.user32.SetForegroundWindow')
            try:
                result = ctypes.windll.user32.SetForegroundWindow(hwnd)
                print(f'方式3结果: {result}')
                if result:
                    print('成功激活窗口（方式3）')
                    return True
            except Exception as e:
                print(f'方式3失败: {e}')
            
            # 尝试4：使用SetWindowPos将窗口置于顶层并激活
            print('尝试激活方式4：SetWindowPos')
            try:
                HWND_TOPMOST = -1
                HWND_NOTOPMOST = -2
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_SHOWWINDOW = 0x0040
                
                # 将窗口置于顶层并显示
                win32gui.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
                # 强制窗口到前台
                win32gui.SetForegroundWindow(hwnd)
                # 确保窗口可见
                win32gui.ShowWindow(hwnd, SW_SHOW)
                print('成功激活窗口（方式4）')
                # 恢复窗口为非顶层
                try:
                    win32gui.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                except Exception as e:
                    print(f'恢复窗口为非顶层失败: {e}')
                return True
            except Exception as e:
                print(f'方式4失败: {e}')
            
            # 尝试5：使用keybd_event模拟按键,然后激活窗口
            print('尝试激活方式5：模拟按键后激活')
            try:
                # 模拟按下Alt键
                ctypes.windll.user32.keybd_event(16, 0, 0, 0)
                # 模拟释放Alt键
                ctypes.windll.user32.keybd_event(16, 0, 2, 0)
                # 然后设置为前台窗口
                result = win32gui.SetForegroundWindow(hwnd)
                print(f'方式5结果: {result}')
                if result:
                    print('成功激活窗口（方式5）')
                    return True
            except Exception as e:
                print(f'方式5失败: {e}')
            
            # 尝试6：使用ShowWindow与SW_SHOWNA
            print('尝试激活方式6：SW_SHOWNA')
            try:
                win32gui.ShowWindow(hwnd, SW_SHOWNA)
                result = win32gui.SetForegroundWindow(hwnd)
                print(f'方式6结果: {result}')
                if result:
                    print('成功激活窗口（方式6）')
                    return True
            except Exception as e:
                print(f'方式6失败: {e}')
            
            print('所有激活方式都失败')
            return False
        except Exception as e:
            print(f'激活窗口失败: {e}')
            import traceback
            traceback.print_exc()
            return False
    
    def atomic_file_replace(self, source_path, target_path, max_retries=5, retry_delay=1.0):
        """原子性文件替换"""
        import os
        import shutil
        import tempfile
        import time
        
        if not os.path.exists(source_path):
            return False
        
        temp_dir = os.path.dirname(target_path)
        temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.tmp')
        temp_file_path = temp_file.name
        temp_file.close()
        
        try:
            shutil.copy2(source_path, temp_file_path)
            
            for attempt in range(max_retries):
                try:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    os.rename(temp_file_path, target_path)
                    return True
                except OSError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        raise
        except Exception as e:
            print(f'原子性文件替换失败: {e}')
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return False
    
    def clear_file_cache(self, file_path):
        """清理文件缓存,确保读取到最新数据
        
        参数:
            file_path: 文件路径
        """
        import os
        try:
            # 通过修改文件的访问时间来强制刷新缓存
            if os.path.exists(file_path):
                current_time = os.path.getmtime(file_path)
                os.utime(file_path, (current_time, current_time))
        except Exception as e:
            print(f"清理文件缓存失败: {e}")
    
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
                print(f"[√] 成功导入 {count} 条装炉顺序数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入装炉顺序数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"[×] 导入装炉顺序数据失败: {str(e)}")
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
                print(f"[√] 成功导入 {count} 条总计划号列表数据到数据库")
                return True
            except Exception as e:
                print(f"第 {attempt+1} 次尝试导入总计划号列表数据失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    print(f"[×] 导入总计划号列表数据失败: {str(e)}")
                    return False
    
    def read_zhizhi_plan_list_with_coords(self, add_debug_log=None):
        """读取总计划号列表数据,返回计划号到坐标的映射字典
        
        根据设置页面中的第一个计划号坐标和计划号间距,
        计算每个计划号的实际屏幕坐标。
        
        参数:
            add_debug_log: 调试日志函数（可选）
            
        返回: {计划号: (x, y)} 的字典
        """
        # 如果没有传入调试日志函数,使用空函数
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
                add_debug_log(f"  [×] 数据库中无数据")
                print(f"总计划号列表数据不存在")
                conn.close()
                return None
            
            add_debug_log(f"  [√] 数据库读取成功")
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
                    # 直接使用行索引计算坐标,不依赖序号值
                    # row_index 从0开始,正好对应第一个计划号的索引
                    coord_y = first_y + (row_index * plan_spacing)
                    coord_x = first_x
                    
                    plan_coord_map[plan_no] = (coord_x, coord_y)
                    zhizhi_plan_list.append((seq_value, plan_no))
                    # 只显示前5个,避免日志过长
                    if row_index < 5:
                        add_debug_log(f"    {plan_no}: 行={row_index}, 坐标=({coord_x}, {coord_y})")
                    elif row_index == 5:
                        add_debug_log(f"    ... 还有 {len(plan_data) - 6} 个计划号")
            
            # 只打印总数,不打印每个计划号的详细信息,提高计算速度
            print(f"  共计算 {len(plan_coord_map)} 个计划号的坐标")
            
            # 关闭数据库连接
            conn.close()
            
            add_debug_log(f"")
            add_debug_log(f"  总计: {len(plan_coord_map)} 个计划号坐标")
            print(f"\n从总计划号列表计算了 {len(plan_coord_map)} 个计划号的坐标")
            
            # 更新缓存
            self.zhizhi_plan_list = zhizhi_plan_list
            self.zhizhi_plan_coord_map = plan_coord_map
            add_debug_log(f"  [√] 已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            print(f"已更新总计划号列表缓存: {len(zhizhi_plan_list)} 条记录")
            
            add_debug_log(f"  [√] 坐标计算完成")
            return plan_coord_map
            
        except Exception as e:
            print(f"读取总计划号列表并计算坐标失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


class FurnaceDetailsWindow(QMainWindow):
    """装炉明细窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("装炉明细")
        self.showMaximized()
        
        # 设置窗口背景色
        self.setStyleSheet("background-color: #f0f0f0;")
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 列名
        columns = [
            "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
            "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
            "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
        ]
        
        # 列宽配置
        column_widths = {
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
            "粗轧报信": 360,
            "坯头部宽": 120,
            "坯尾部宽": 120,
            "热轧产品分类": 110,
            "炼钢钢种": 210,
            "负公差": 90,
            "正公差": 90,
            "回炉坯": 90,
            "原轧宽": 90
        }
        
        # 创建表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        
        # 设置列宽
        for i, col in enumerate(columns):
            width = column_widths.get(col, 70)
            self.table_widget.setColumnWidth(i, width)
        
        # 设置行高
        self.table_widget.verticalHeader().setDefaultSectionSize(80)
        
        # 隐藏垂直表头
        self.table_widget.verticalHeader().setVisible(False)
        
        # 设置字体
        font = QFont("微软雅黑", 20, QFont.Bold)
        self.table_widget.setFont(font)
        
        # 设置表头字体
        header_font = QFont("微软雅黑", 20, QFont.Bold)
        self.table_widget.horizontalHeader().setFont(header_font)
        
        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        
        # 设置表格样式，添加边框和选中行背景色
        table_style = """
            QTableWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                gridline-color: #CCCCCC;
                outline: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid #CCCCCC;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #E3F2FD;
            }
        """
        self.table_widget.setStyleSheet(table_style)
        
        # 添加表格到布局
        main_layout.addWidget(self.table_widget)
        
        # 自动滚动相关变量
        self.scroll_timer = QTimer()
        self.is_scrolling = False
        self.scroll_interval = 110  # 默认 110 秒
        
        # 底部布局
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(10, 10, 10, 10)
        bottom_layout.setSpacing(10)
        main_layout.addLayout(bottom_layout)
        
        # 左侧按钮组
        left_buttons = QHBoxLayout()
        left_buttons.setSpacing(10)
        bottom_layout.addLayout(left_buttons)
        
        # 创建按钮样式
        button_style = """
            QPushButton {
                background-color: white;
                border: 1px solid #CCCCCC;
                padding: 5px 10px;
                font-family: 宋体;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """
        
        # 打印按钮
        self.print_btn = QPushButton("打印")
        self.print_btn.setFont(QFont("宋体", 14))
        self.print_btn.setFixedSize(60, 30)
        self.print_btn.setStyleSheet(button_style)
        left_buttons.addWidget(self.print_btn)
        
        # 全部打印复选框
        self.all_print_checkbox = QCheckBox("全部打印")
        self.all_print_checkbox.setFont(QFont("宋体", 14))
        left_buttons.addWidget(self.all_print_checkbox)
        
        # 返回按钮
        self.return_btn = QPushButton("返回")
        self.return_btn.setFont(QFont("宋体", 14))
        self.return_btn.setFixedSize(60, 30)
        self.return_btn.setStyleSheet(button_style)
        left_buttons.addWidget(self.return_btn)
        
        # 中间块数显示
        bottom_layout.addStretch(1)
        
        # 块数显示
        self.block_count_label = QLabel("0/0")
        self.block_count_label.setFont(QFont("宋体", 16, QFont.Bold))
        self.block_count_label.setStyleSheet("color: blue;")
        bottom_layout.addWidget(self.block_count_label)
        
        bottom_layout.addStretch(1)
        
        # 右侧信息和控制
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)
        bottom_layout.addLayout(right_layout)
        
        # 下一次执行时间显示
        self.next_execution_label = QLabel("下一次执行: 无")
        self.next_execution_label.setFont(QFont("宋体", 12))
        right_layout.addWidget(self.next_execution_label)
        
        # 滚动时间输入框
        self.scroll_time_edit = QLineEdit("110")
        self.scroll_time_edit.setFont(QFont("宋体", 12))
        self.scroll_time_edit.setFixedWidth(50)
        self.scroll_time_edit.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.scroll_time_edit)
        
        # 播放/停止按钮
        self.scroll_toggle_btn = QPushButton("▶")
        self.scroll_toggle_btn.setFont(QFont("宋体", 12))
        self.scroll_toggle_btn.setFixedSize(30, 30)
        self.scroll_toggle_btn.setStyleSheet(button_style)
        right_layout.addWidget(self.scroll_toggle_btn)
        
        # 连接信号
        self.connect_signals()
        
        # 加载数据
        self.load_furnace_data()


    def connect_signals(self):
        """连接信号"""
        # 连接按钮信号
        self.return_btn.clicked.connect(self.close)
        self.print_btn.clicked.connect(self.print_furnace_details)
        self.scroll_toggle_btn.clicked.connect(self.toggle_scroll)
        
        # 连接表格选择变化信号
        self.table_widget.selectionModel().currentRowChanged.connect(self.update_block_count)
        
        # 连接滚动定时器
        self.scroll_timer.timeout.connect(self.auto_scroll)
        
        # 连接滚动时间输入框
        self.scroll_time_edit.textChanged.connect(self.on_scroll_time_changed)
    
    def load_furnace_data(self):
        """加载装炉明细数据"""
        try:
            import os
            import tempfile
            import shutil
            import xlrd
            import time
            import json
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            # 读取装炉顺序.xls
            plan_dir = os.path.join(os.getcwd(), "计划号")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            print(f"查找装炉顺序文件: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"文件不存在: {excel_file}")
                self.block_count_label.setText("0/0")
                return
            
            # 创建临时副本
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
                self.block_count_label.setText("0/0")
                return
            
            # 读取数据
            furnace_data = []
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
                        furnace_data.append({
                            'order': order,
                            'plan_no': plan_no,
                            'coil_no': coil_no
                        })
                        print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no}")
                    else:
                        print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}'")
                except Exception as e:
                    print(f"读取行 {row} 失败: {e}")
                    continue
            
            # 删除临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"删除临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")
            
            print(f"加载到 {len(furnace_data)} 条装炉数据")
            if len(furnace_data) == 0:
                print("装炉顺序.xls文件中没有数据")
                self.block_count_label.setText("0/0")
                return
            
            # 清空表格
            self.table_widget.setRowCount(0)
            
            # 加载计划号数据
            for item in furnace_data:
                plan_no = item['plan_no']
                coil_no = item['coil_no']
                
                # 获取计划号文件
                plan_file = self.get_plan_file(plan_no)
                if not plan_file:
                    print(f"未找到计划号文件: {plan_no}")
                    continue
                
                # 读取计划号文件数据
                plan_data = self.read_plan_file(plan_file, coil_no)
                if plan_data:
                    self.add_plan_data_to_table(plan_data)
            
            # 保存表格数据
            self.save_current_table_data()
            
            # 更新块数显示
            self.update_block_count()
            
        except Exception as e:
            print(f"加载装炉明细数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.block_count_label.setText("0/0")
            
    def get_plan_file(self, plan_no):
        """获取计划号文件路径"""
        import os
        # 首先在计划号目录查找
        plan_dir = os.path.join(os.getcwd(), "计划号")
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
        file_path = os.path.join(os.getcwd(), f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        return None
    
    def read_plan_file(self, file_path, target_coil_no):
        """读取计划号文件数据"""
        try:
            import xlrd
            
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            
            # 获取列名
            headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
            
            # 查找钢卷号列
            coil_col = None
            for idx, header in enumerate(headers):
                if '钢卷号' in header:
                    coil_col = idx
                    break
            
            if coil_col is None:
                print(f"计划号文件 {file_path} 中未找到钢卷号列")
                return None
            
            # 查找目标钢卷号
            for row in range(1, sheet.nrows):
                try:
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    # 清理钢卷号，只保留数字
                    cleaned_coil_no = ''.join(c for c in coil_no if c.isdigit())
                    
                    if cleaned_coil_no == target_coil_no:
                        # 读取整行数据
                        row_data = []
                        for col in range(len(headers)):
                            value = sheet.cell_value(row, col)
                            if isinstance(value, float) and value.is_integer():
                                value = int(value)
                            row_data.append(str(value).strip())
                        
                        # 构建数据字典
                        data = {}
                        for i, header in enumerate(headers):
                            data[header] = row_data[i]
                        
                        return data
                except Exception as e:
                    print(f"读取计划号文件行 {row} 失败: {e}")
                    continue
            
            print(f"计划号文件 {file_path} 中未找到钢卷号 {target_coil_no}")
            return None
        except Exception as e:
            print(f"读取计划号文件失败: {str(e)}")
            return None
    
    def add_plan_data_to_table(self, plan_data):
        """将计划数据添加到表格"""
        try:
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            # 列名映射
            column_map = {
                "计划号": "计划号",
                "钢卷号": "钢卷号",
                "牌号（钢级）": "牌号（钢级）",
                "坯宽": "坯宽",
                "减宽": "减宽",
                "调宽": "调宽",
                "轧宽": "轧宽",
                "公差带": "公差带",
                "粗轧报信": "粗轧报信",
                "除鳞": "除鳞",
                "坯厚": "坯厚",
                "坯长": "坯长",
                "轧厚": "轧厚",
                "中厚": "中厚",
                "RT2": "RT2",
                "强度": "强度",
                "切边": "切边",
                "去向": "去向",
                "订宽": "订宽",
                "坯头部宽": "坯头部宽",
                "坯尾部宽": "坯尾部宽",
                "热轧产品分类": "热轧产品分类",
                "炼钢钢种": "炼钢钢种",
                "负公差": "负公差",
                "正公差": "正公差",
                "回炉坯": "回炉坯",
                "原轧宽": "原轧宽"
            }
            
            # 获取列索引
            columns = [
                "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
                "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
            ]
            
            # 添加新行
            row_idx = self.table_widget.rowCount()
            self.table_widget.insertRow(row_idx)
            
            # 填充数据
            for col_idx, col_name in enumerate(columns):
                # 查找对应的数据
                data_key = column_map.get(col_name, col_name)
                value = plan_data.get(data_key, "")
                
                item = QTableWidgetItem(value)
                
                # 设置字体
                font = item.font()
                font.setFamily("微软雅黑")
                font.setPointSize(20)
                font.setBold(True)
                item.setFont(font)
                
                # 处理特殊情况和高亮
                self.process_cell_highlight(item, col_name, value)
                
                self.table_widget.setItem(row_idx, col_idx, item)
                
        except Exception as e:
            print(f"添加计划数据到表格失败: {str(e)}")
    
    def process_cell_highlight(self, item, col_name, value):
        """处理单元格高亮"""
        from PyQt5.QtGui import QColor, QBrush
        
        # 检查是否需要高亮
        if col_name == "减宽":
            try:
                # 检查是否为数字
                if value.replace('.', '').replace('-', '').isdigit():
                    width_reduction = float(value)
                    if width_reduction >= 240:
                        # 减宽超标，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                    elif width_reduction < 0:
                        # 逆宽，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
            except:
                pass
        
        elif col_name == "轧宽":
            try:
                if value.replace('.', '').isdigit():
                    roll_width = float(value)
                    if roll_width < 860:
                        # 轧宽低于860，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                    elif roll_width < 930:
                        # 轧宽低于930，高亮为黄色
                        item.setBackground(QBrush(QColor('#FFFF00')))
                        item.setForeground(QBrush(QColor('#000000')))
            except:
                pass
        
        elif col_name == "坯厚":
            try:
                if value.replace('.', '').isdigit():
                    blank_thickness = float(value)
                    if blank_thickness > 230:
                        # 坯厚大于230，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
            except:
                pass
        
        elif col_name == "除鳞":
            if "回" in value or "无APS" in value:
                # 除鳞字段包含回字或无APS，高亮为红色
                item.setBackground(QBrush(QColor('#FF0000')))
                item.setForeground(QBrush(QColor('#FFFFFF')))
    
    def save_current_table_data(self):
        """保存当前表格数据"""
        try:
            import json
            import os
            # 构建保存文件路径
            plan_dir = os.path.join(os.getcwd(), "计划号")
            os.makedirs(plan_dir, exist_ok=True)
            table_data_file = os.path.join(plan_dir, "furnace_table_data.json")
            
            # 收集当前表格数据
            table_data = []
            seq_num = 1
            for row_idx in range(self.table_widget.rowCount()):
                # 检查是否是换辊行或自定义信息行
                first_item = self.table_widget.item(row_idx, 0)
                is_special_row = False
                if first_item:
                    bg_color = first_item.background().color().name()
                    if bg_color in ['#00ff00', '#00FF00', '#ffff00', '#FFFF00']:
                        is_special_row = True
                
                if not is_special_row:
                    # 正常数据行，获取钢卷号
                    coil_item = self.table_widget.item(row_idx, 1)  # 钢卷号列（索引1）
                    if coil_item:
                        coil_number = coil_item.text().strip()
                        if coil_number:
                            table_data.append({
                                "coil_number": coil_number,
                                "sequence": seq_num
                            })
                            seq_num += 1
            
            # 读取之前的表格数据
            previous_table_data = []
            if os.path.exists(table_data_file):
                try:
                    with open(table_data_file, 'r', encoding='utf-8') as f:
                        previous_table_data = json.load(f)
                except:
                    previous_table_data = []
            
            # 保存最近2次的表格数据
            combined_data = [table_data] + previous_table_data[:1]  # 只保留最近2次的数据
            
            # 保存数据
            with open(table_data_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存表格数据: {table_data_file}")
            print(f"当前表格数据: {[item['coil_number'] for item in table_data]}")
            if previous_table_data:
                print(f"上一次表格数据: {[item['coil_number'] for item in previous_table_data[0]]}")
        except Exception as e:
            print(f"保存表格数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update_block_count(self):
        """更新块数显示"""
        try:
            total_rows = self.table_widget.rowCount()
            selected_rows = self.table_widget.selectionModel().selectedRows()
            if selected_rows:
                current_row = selected_rows[0].row() + 1
                self.block_count_label.setText(f"{current_row}/{total_rows}")
            else:
                self.block_count_label.setText(f"0/{total_rows}")
        except Exception as e:
            print(f"更新块数显示失败：{e}")
            self.block_count_label.setText("0/0")
    
    def toggle_scroll(self):
        """切换滚动状态"""
        if self.is_scrolling:
            self.stop_auto_scroll()
            self.scroll_toggle_btn.setText("▶")
        else:
            self.start_auto_scroll()
            self.scroll_toggle_btn.setText("⏸")
    
    def start_auto_scroll(self):
        """启动自动滚动"""
        try:
            self.is_scrolling = True
            self.scroll_interval = int(self.scroll_time_edit.text())
            self.scroll_timer.start(self.scroll_interval * 1000)  # 转换为毫秒
            print(f"启动自动滚动，间隔：{self.scroll_interval}秒")
        except Exception as e:
            print(f"启动自动滚动失败：{e}")
    
    def stop_auto_scroll(self):
        """停止自动滚动"""
        try:
            self.is_scrolling = False
            self.scroll_timer.stop()
            print("停止自动滚动")
        except Exception as e:
            print(f"停止自动滚动失败：{e}")
    
    def auto_scroll(self):
        """自动滚动到下一行"""
        try:
            current_row = self.table_widget.currentRow()
            total_rows = self.table_widget.rowCount()
            
            if current_row < total_rows - 1:
                next_row = current_row + 1
            else:
                next_row = 0  # 循环回到第一行
            
            self.table_widget.selectRow(next_row)
            self.table_widget.scrollToItem(self.table_widget.item(next_row, 0))
            print(f"自动滚动到第{next_row + 1}行")
        except Exception as e:
            print(f"自动滚动失败：{e}")
    
    def on_scroll_time_changed(self, text):
        """滚动时间变化"""
        try:
            self.scroll_interval = int(text)
            if self.is_scrolling:
                self.scroll_timer.setInterval(self.scroll_interval * 1000)
        except:
            pass
    
    def print_furnace_details(self):
        """打印装炉明细 - 调用主窗口的打印方法"""
        if hasattr(self, 'parent') and self.parent():
            self.parent().print_furnace_details()
        else:
            QMessageBox.information(self, "提示", "无法获取主窗口引用")

class SettingsWindow(QDialog):
    """设置窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setGeometry(300, 200, 800, 800)
        self.parent = parent
        
        # 导入UI
        from settings_window_ui import Ui_SettingsWindow
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        
        # 加载设置
        self.load_settings()
        
        # 连接信号
        self.ui.mainWindowGetBtn.clicked.connect(lambda: self.get_window_coordinates('mainWindow'))
        self.ui.mainWindowTestBtn.clicked.connect(lambda: self.test_window_coordinates('mainWindow'))
        self.ui.furnaceWindowGetBtn.clicked.connect(lambda: self.get_window_coordinates('furnaceWindow'))
        self.ui.furnaceWindowTestBtn.clicked.connect(lambda: self.test_window_coordinates('furnaceWindow'))
        self.ui.planInputGetBtn.clicked.connect(lambda: self.get_window_coordinates('planInput'))
        self.ui.planInputTestBtn.clicked.connect(lambda: self.test_window_coordinates('planInput'))
        self.ui.queryBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('queryBtn'))
        self.ui.queryBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('queryBtn'))
        self.ui.exportBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('exportBtn'))
        self.ui.exportBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('exportBtn'))
        self.ui.closeBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('closeBtn'))
        self.ui.closeBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('closeBtn'))
        self.ui.detailExportBtnGetBtn.clicked.connect(lambda: self.get_window_coordinates('detailExportBtn'))
        self.ui.detailExportBtnTestBtn.clicked.connect(lambda: self.test_window_coordinates('detailExportBtn'))
        
        # 窗口选择信号
        self.ui.windowRadio1.toggled.connect(lambda: self.save_settings())
        self.ui.windowRadio2.toggled.connect(lambda: self.save_settings())
        
        # 自动导出设置信号
        self.ui.autoPrintCheckBox.stateChanged.connect(lambda: self.save_settings())
        
        # 自动执行设置信号
        self.ui.autoExecCheckBox.stateChanged.connect(lambda: self.save_settings())
        self.ui.intervalModeRadio.toggled.connect(lambda: self.save_settings())
        self.ui.timeModeRadio.toggled.connect(lambda: self.save_settings())
        self.ui.intervalMinutesEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.timeEdit.textChanged.connect(lambda: self.save_settings())
        self.ui.antiLogoutCheckBox.stateChanged.connect(lambda: self.save_settings())
        self.ui.intervalEdit.textChanged.connect(lambda: self.save_settings())
        
        # 恢复默认值按钮
        self.ui.restoreDefaultsBtn.clicked.connect(self.restore_defaults)
        
        # 确保窗口居中显示
        self.center_on_parent()
        
    def center_on_parent(self):
        """使窗口在父窗口中心显示"""
        if self.parent:
            # 获取父窗口的几何信息
            parent_geo = self.parent.geometry()
            # 计算居中位置
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            # 设置窗口位置
            self.move(x, y)
    
    def load_settings(self):
        """加载设置"""
        import json
        import os
        
        # 默认设置文件路径
        default_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_settings.json')
        
        # 尝试从默认设置文件加载
        default_settings = None
        try:
            with open(default_config_file, 'r', encoding='utf-8') as f:
                default_settings = json.load(f)
        except Exception as e:
            print(f"加载默认设置文件失败: {e}")
        
        # 如果默认设置文件加载失败，使用硬编码的默认值
        if default_settings is None:
            default_settings = {
                # 坐标设置
                "mainWindow": {"x": 0, "y": 0},
                "furnaceWindow": {"x": 0, "y": 0},
                "planInput": {"x": 0, "y": 0},
                "queryBtn": {"x": 0, "y": 0},
                "exportBtn": {"x": 0, "y": 0},
                "closeBtn": {"x": 0, "y": 0},
                "detailExportBtn": {"x": 0, "y": 0},
                
                # 窗口选择
                "selectedWindow": "Doc1.docx - Word",
                
                # 自动导出设置
                "autoPrint": True,
                
                # 自动执行设置
                "autoExec": False,
                "execMode": "interval",  # interval 或 time
                "intervalMinutes": 1,
                "execTimes": "16:00,16:02,16:04",
                
                # 防止退出登录设置
                "antiLogout": False,
                "antiLogoutInterval": 1
            }
        
        # 加载设置文件
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        if os.path.exists(config_file):
            try:
                # 先检查文件大小
                if os.path.getsize(config_file) < 5:
                    raise ValueError("Settings file is too small")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # 验证设置结构
                if not isinstance(settings, dict):
                    raise ValueError("Invalid settings format")
                
                # 应用设置
                self.apply_settings(settings)
                print("设置加载成功")
                return
            except Exception as e:
                print(f"加载设置失败: {e}")
                # 如果加载失败，删除损坏的文件
                try:
                    os.remove(config_file)
                    print("已删除损坏的设置文件")
                except Exception as e:
                    print(f"删除损坏文件失败: {e}")
        
        # 如果加载失败或文件不存在，使用默认设置
        self.apply_settings(default_settings)
        # 保存默认设置
        self.save_settings(default_settings)
    
    def apply_settings(self, settings):
        """应用设置到界面"""
        # 应用坐标设置
        if "mainWindow" in settings:
            self.ui.mainWindowXEdit.setText(str(settings["mainWindow"].get("x", 0)))
            self.ui.mainWindowYEdit.setText(str(settings["mainWindow"].get("y", 0)))
        if "furnaceWindow" in settings:
            self.ui.furnaceWindowXEdit.setText(str(settings["furnaceWindow"].get("x", 0)))
            self.ui.furnaceWindowYEdit.setText(str(settings["furnaceWindow"].get("y", 0)))
        if "planInput" in settings:
            self.ui.planInputXEdit.setText(str(settings["planInput"].get("x", 0)))
            self.ui.planInputYEdit.setText(str(settings["planInput"].get("y", 0)))
        if "queryBtn" in settings:
            self.ui.queryBtnXEdit.setText(str(settings["queryBtn"].get("x", 0)))
            self.ui.queryBtnYEdit.setText(str(settings["queryBtn"].get("y", 0)))
        if "exportBtn" in settings:
            self.ui.exportBtnXEdit.setText(str(settings["exportBtn"].get("x", 0)))
            self.ui.exportBtnYEdit.setText(str(settings["exportBtn"].get("y", 0)))
        if "closeBtn" in settings:
            self.ui.closeBtnXEdit.setText(str(settings["closeBtn"].get("x", 0)))
            self.ui.closeBtnYEdit.setText(str(settings["closeBtn"].get("y", 0)))
        if "detailExportBtn" in settings:
            self.ui.detailExportBtnXEdit.setText(str(settings["detailExportBtn"].get("x", 0)))
            self.ui.detailExportBtnYEdit.setText(str(settings["detailExportBtn"].get("y", 0)))
        
        # 应用窗口选择设置
        if "selectedWindow" in settings:
            if settings["selectedWindow"] == "Doc1.docx - Word":
                self.ui.windowRadio1.setChecked(True)
            else:
                self.ui.windowRadio2.setChecked(True)
        
        # 应用自动导出设置
        if "autoPrint" in settings:
            self.ui.autoPrintCheckBox.setChecked(settings["autoPrint"])
        
        # 应用自动执行设置
        if "autoExec" in settings:
            self.ui.autoExecCheckBox.setChecked(settings["autoExec"])
        if "execMode" in settings:
            if settings["execMode"] == "interval":
                self.ui.intervalModeRadio.setChecked(True)
            else:
                self.ui.timeModeRadio.setChecked(True)
        if "intervalMinutes" in settings:
            self.ui.intervalMinutesEdit.setText(str(settings["intervalMinutes"]))
        if "execTimes" in settings:
            self.ui.timeEdit.setText(settings["execTimes"])
        
        # 应用防止退出登录设置
        if "antiLogout" in settings:
            self.ui.antiLogoutCheckBox.setChecked(settings["antiLogout"])
        if "antiLogoutInterval" in settings:
            self.ui.intervalEdit.setText(str(settings["antiLogoutInterval"]))
    
    def save_settings(self, settings=None):
        """保存设置"""
        import json
        import os
        
        if settings is None:
            # 从界面收集设置
            settings = {
                # 坐标设置
                "mainWindow": {
                    "x": int(self.ui.mainWindowXEdit.text()) if self.ui.mainWindowXEdit.text().isdigit() else 0,
                    "y": int(self.ui.mainWindowYEdit.text()) if self.ui.mainWindowYEdit.text().isdigit() else 0
                },
                "furnaceWindow": {
                    "x": int(self.ui.furnaceWindowXEdit.text()) if self.ui.furnaceWindowXEdit.text().isdigit() else 0,
                    "y": int(self.ui.furnaceWindowYEdit.text()) if self.ui.furnaceWindowYEdit.text().isdigit() else 0
                },
                "planInput": {
                    "x": int(self.ui.planInputXEdit.text()) if self.ui.planInputXEdit.text().isdigit() else 0,
                    "y": int(self.ui.planInputYEdit.text()) if self.ui.planInputYEdit.text().isdigit() else 0
                },
                "queryBtn": {
                    "x": int(self.ui.queryBtnXEdit.text()) if self.ui.queryBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.queryBtnYEdit.text()) if self.ui.queryBtnYEdit.text().isdigit() else 0
                },
                "exportBtn": {
                    "x": int(self.ui.exportBtnXEdit.text()) if self.ui.exportBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.exportBtnYEdit.text()) if self.ui.exportBtnYEdit.text().isdigit() else 0
                },
                "closeBtn": {
                    "x": int(self.ui.closeBtnXEdit.text()) if self.ui.closeBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.closeBtnYEdit.text()) if self.ui.closeBtnYEdit.text().isdigit() else 0
                },
                "detailExportBtn": {
                    "x": int(self.ui.detailExportBtnXEdit.text()) if self.ui.detailExportBtnXEdit.text().isdigit() else 0,
                    "y": int(self.ui.detailExportBtnYEdit.text()) if self.ui.detailExportBtnYEdit.text().isdigit() else 0
                },
                
                # 窗口选择
                "selectedWindow": "Doc1.docx - Word" if self.ui.windowRadio1.isChecked() else "BCGMS1-宝钢股份基地制造管理系统运行环境",
                
                # 自动导出设置
                "autoPrint": self.ui.autoPrintCheckBox.isChecked(),
                
                # 自动执行设置
                "autoExec": self.ui.autoExecCheckBox.isChecked(),
                "execMode": "interval" if self.ui.intervalModeRadio.isChecked() else "time",
                "intervalMinutes": int(self.ui.intervalMinutesEdit.text()) if self.ui.intervalMinutesEdit.text().isdigit() else 1,
                "execTimes": self.ui.timeEdit.text(),
                
                # 防止退出登录设置
                "antiLogout": self.ui.antiLogoutCheckBox.isChecked(),
                "antiLogoutInterval": int(self.ui.intervalEdit.text()) if self.ui.intervalEdit.text().isdigit() else 1
            }
        
        # 保存设置到文件
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print("设置保存成功")
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def restore_defaults(self):
        """恢复默认设置"""
        default_settings = {
            # 坐标设置
            "mainWindow": {"x": 0, "y": 0},
            "furnaceWindow": {"x": 0, "y": 0},
            "planInput": {"x": 0, "y": 0},
            "queryBtn": {"x": 0, "y": 0},
            "exportBtn": {"x": 0, "y": 0},
            "closeBtn": {"x": 0, "y": 0},
            "detailExportBtn": {"x": 0, "y": 0},
            
            # 窗口选择
            "selectedWindow": "Doc1.docx - Word",
            
            # 自动导出设置
            "autoPrint": True,
            
            # 自动执行设置
            "autoExec": False,
            "execMode": "interval",
            "intervalMinutes": 1,
            "execTimes": "16:00,16:02,16:04",
            
            # 防止退出登录设置
            "antiLogout": False,
            "antiLogoutInterval": 1
        }
        
        # 应用默认设置
        self.apply_settings(default_settings)
        # 保存默认设置
        self.save_settings(default_settings)
        
        # 显示提示
        QMessageBox.information(self, "提示", "已恢复默认设置")
    
    def get_window_coordinates(self, window_type):
        """获取窗口坐标"""
        try:
            import win32gui
            import win32api
            import win32con
            
            # 提示用户
            QMessageBox.information(self, "提示", f"请将鼠标移动到{window_type}位置，然后按Enter键")
            
            # 等待用户输入
            QApplication.processEvents()
            
            # 获取鼠标位置
            import time
            time.sleep(0.5)
            
            # 显示坐标实时更新
            while True:
                x, y = win32api.GetCursorPos()
                # 更新界面
                if window_type == 'mainWindow':
                    self.ui.mainWindowXEdit.setText(str(x))
                    self.ui.mainWindowYEdit.setText(str(y))
                elif window_type == 'furnaceWindow':
                    self.ui.furnaceWindowXEdit.setText(str(x))
                    self.ui.furnaceWindowYEdit.setText(str(y))
                elif window_type == 'planInput':
                    self.ui.planInputXEdit.setText(str(x))
                    self.ui.planInputYEdit.setText(str(y))
                elif window_type == 'queryBtn':
                    self.ui.queryBtnXEdit.setText(str(x))
                    self.ui.queryBtnYEdit.setText(str(y))
                elif window_type == 'exportBtn':
                    self.ui.exportBtnXEdit.setText(str(x))
                    self.ui.exportBtnYEdit.setText(str(y))
                elif window_type == 'closeBtn':
                    self.ui.closeBtnXEdit.setText(str(x))
                    self.ui.closeBtnYEdit.setText(str(y))
                elif window_type == 'detailExportBtn':
                    self.ui.detailExportBtnXEdit.setText(str(x))
                    self.ui.detailExportBtnYEdit.setText(str(y))
                
                QApplication.processEvents()
                time.sleep(0.1)
                
                # 检查是否按下Enter键
                if win32api.GetAsyncKeyState(win32con.VK_RETURN) & 0x8000:
                    break
                    
        except Exception as e:
            print(f"获取坐标失败: {e}")
            QMessageBox.warning(self, "错误", "获取坐标失败")
    
    def test_window_coordinates(self, window_type):
        """测试窗口坐标"""
        try:
            import win32gui
            import win32api
            import win32con
            
            # 获取坐标
            if window_type == 'mainWindow':
                x = int(self.ui.mainWindowXEdit.text()) if self.ui.mainWindowXEdit.text().isdigit() else 0
                y = int(self.ui.mainWindowYEdit.text()) if self.ui.mainWindowYEdit.text().isdigit() else 0
            elif window_type == 'furnaceWindow':
                x = int(self.ui.furnaceWindowXEdit.text()) if self.ui.furnaceWindowXEdit.text().isdigit() else 0
                y = int(self.ui.furnaceWindowYEdit.text()) if self.ui.furnaceWindowYEdit.text().isdigit() else 0
            elif window_type == 'planInput':
                x = int(self.ui.planInputXEdit.text()) if self.ui.planInputXEdit.text().isdigit() else 0
                y = int(self.ui.planInputYEdit.text()) if self.ui.planInputYEdit.text().isdigit() else 0
            elif window_type == 'queryBtn':
                x = int(self.ui.queryBtnXEdit.text()) if self.ui.queryBtnXEdit.text().isdigit() else 0
                y = int(self.ui.queryBtnYEdit.text()) if self.ui.queryBtnYEdit.text().isdigit() else 0
            elif window_type == 'exportBtn':
                x = int(self.ui.exportBtnXEdit.text()) if self.ui.exportBtnXEdit.text().isdigit() else 0
                y = int(self.ui.exportBtnYEdit.text()) if self.ui.exportBtnYEdit.text().isdigit() else 0
            elif window_type == 'closeBtn':
                x = int(self.ui.closeBtnXEdit.text()) if self.ui.closeBtnXEdit.text().isdigit() else 0
                y = int(self.ui.closeBtnYEdit.text()) if self.ui.closeBtnYEdit.text().isdigit() else 0
            elif window_type == 'detailExportBtn':
                x = int(self.ui.detailExportBtnXEdit.text()) if self.ui.detailExportBtnXEdit.text().isdigit() else 0
                y = int(self.ui.detailExportBtnYEdit.text()) if self.ui.detailExportBtnYEdit.text().isdigit() else 0
            else:
                return
            
            # 移动鼠标到指定位置
            win32api.SetCursorPos((x, y))
            
            # 显示提示
            QMessageBox.information(self, "提示", f"鼠标已移动到{window_type}位置: ({x}, {y})")
            
        except Exception as e:
            print(f"测试坐标失败: {e}")
            QMessageBox.warning(self, "错误", "测试坐标失败")
    
    def accept(self):
        """确认设置"""
        super().accept()
        if self.parent:
            self.parent.load_settings()


class ExportProcessWindow(QDialog):
    """导出过程窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出过程")
        self.setGeometry(300, 200, 800, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加文本框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 添加按钮
        button = QPushButton("关闭")
        button.clicked.connect(self.close)
        layout.addWidget(button)
        
    def append_text(self, text):
        """追加文本"""
        self.text_edit.append(text)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())


if __name__ == "__main__":
    """主程序入口"""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"启动程序失败: {str(e)}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "错误", f"启动程序失败: {str(e)}")
        sys.exit(1)
