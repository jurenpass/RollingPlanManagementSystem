# -*- coding: utf-8 -*-
"""
完善装炉明细窗口功能
从原程序复刻：主题切换、自动滚动、块数显示、高亮标记等功能
"""

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 FurnaceDetailsWindow 类的__init__方法，在设置表格属性后添加功能
old_table_setup = '''        # 设置表格属性
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        
        # 添加表格到布局
        main_layout.addWidget(self.table_widget)'''

new_table_setup = '''        # 设置表格属性
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
        
        # 主题配色方案
        self.主题配色 = {
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
            }
        }
        
        # 当前主题
        self.当前主题 = "默认"
        
        # 自动滚动相关变量
        self.scroll_timer = QTimer()
        self.is_scrolling = False
        self.scroll_interval = 110  # 默认 110 秒
        
        # 连接信号
        self.connect_signals()
        
        # 加载数据
        self.load_furnace_data()'''

content = content.replace(old_table_setup, new_table_setup)

# 在按钮添加后添加更多功能按钮
old_buttons = '''        # 主题按钮
        self.theme_btn = QPushButton("主题")
        self.theme_btn.setFont(QFont("微软雅黑", 14))
        self.theme_btn.setFixedSize(100, 40)
        self.theme_btn.setStyleSheet(button_style)
        center_buttons.addWidget(self.theme_btn)'''

new_buttons = '''        # 主题按钮
        self.theme_btn = QPushButton("主题")
        self.theme_btn.setFont(QFont("微软雅黑", 14))
        self.theme_btn.setFixedSize(100, 40)
        self.theme_btn.setStyleSheet(button_style)
        center_buttons.addWidget(self.theme_btn)
        
        # 自动滚动复选框
        self.auto_scroll_checkbox = QCheckBox("自动滚动")
        self.auto_scroll_checkbox.setFont(QFont("微软雅黑", 14))
        center_buttons.addWidget(self.auto_scroll_checkbox)'''

content = content.replace(old_buttons, new_buttons)

# 添加方法
old_class_end = '''class SettingsWindow(QDialog):
    """设置窗口"""'''

new_methods = '''    def connect_signals(self):
        """连接信号"""
        # 连接按钮信号
        self.return_btn.clicked.connect(self.close)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.auto_scroll_checkbox.stateChanged.connect(self.toggle_auto_scroll)
        
        # 连接表格选择变化信号
        self.table_widget.selectionModel().currentRowChanged.connect(self.update_block_count)
        
        # 连接滚动定时器
        self.scroll_timer.timeout.connect(self.auto_scroll)
        
        # 连接滚动时间输入框
        self.scroll_time_edit.textChanged.connect(self.on_scroll_time_changed)
    
    def load_furnace_data(self):
        """加载装炉明细数据"""
        try:
            # TODO: 从数据库或文件加载数据
            # 这里先填充测试数据
            print("加载装炉明细数据...")
        except Exception as e:
            print(f"加载数据失败：{e}")
    
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
    
    def toggle_theme(self):
        """切换主题"""
        themes = list(self.主题配色.keys())
        current_index = themes.index(self.当前主题)
        next_index = (current_index + 1) % len(themes)
        self.当前主题 = themes[next_index]
        self.apply_theme(self.当前主题)
    
    def apply_theme(self, theme_name):
        """应用主题"""
        colors = self.主题配色[theme_name]
        
        # 设置窗口背景
        self.setStyleSheet(f"background-color: {colors['窗口背景']};")
        
        # 设置表格背景和文字
        self.table_widget.setStyleSheet(f"""
            QTableWidget {{ 
                background-color: {colors['表格背景']}; 
                color: {colors['表格文字']};
                border: 1px solid {colors['边框']};
                gridline-color: {colors['边框']};
            }}
            QHeaderView::section {{ 
                background-color: {colors['表头背景']}; 
                color: {colors['表头文字']};
            }}
            QTableWidget::item:selected {{ 
                background-color: {colors['选中行']}; 
                color: {colors['选中行文字']}; 
            }}
            QTableWidget::item:hover {{ 
                background-color: {colors['悬停行']}; 
                color: {colors['悬停行文字']}; 
            }}
        """)
        
        # 更新右侧容器背景
        if hasattr(self, 'right_container'):
            self.right_container.setStyleSheet(f"background-color: {colors['窗口背景']};")
        
        print(f"已切换到主题：{theme_name}")
    
    def toggle_auto_scroll(self, state):
        """切换自动滚动"""
        if state == Qt.Checked:
            self.start_auto_scroll()
        else:
            self.stop_auto_scroll()
    
    def start_auto_scroll(self):
        """启动自动滚动"""
        try:
            self.is_scrolling = True
            self.scroll_interval = int(self.scroll_time_edit.text())
            self.scroll_timer.start(self.scroll_interval * 1000)  # 转换为毫秒
            self.scroll_status_label.setText(f" [自动滚动：{self.scroll_interval}秒]")
            print(f"启动自动滚动，间隔：{self.scroll_interval}秒")
        except Exception as e:
            print(f"启动自动滚动失败：{e}")
    
    def stop_auto_scroll(self):
        """停止自动滚动"""
        try:
            self.is_scrolling = False
            self.scroll_timer.stop()
            self.scroll_status_label.setText("")
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
                self.scroll_status_label.setText(f" [自动滚动：{self.scroll_interval}秒]")
        except:
            pass
    
    def print_furnace_details(self):
        """打印装炉明细 - 调用主窗口的打印方法"""
        if hasattr(self, 'parent') and self.parent():
            self.parent().print_furnace_details()
        else:
            QMessageBox.information(self, "提示", "无法获取主窗口引用")


class SettingsWindow(QDialog):
    """设置窗口"""'''

content = content.replace(old_class_end, new_methods)

# 写入文件
with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已完善装炉明细窗口功能")
