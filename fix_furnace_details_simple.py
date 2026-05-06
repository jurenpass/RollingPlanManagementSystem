# -*- coding: utf-8 -*-
"""
修复装炉明细窗口的方法归属问题
将connect_signals等方法从SettingsWindow移到FurnaceDetailsWindow
"""

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 首先删除重复的SettingsWindow类定义
import re
# 匹配所有SettingsWindow类定义
settings_windows = re.findall(r'class SettingsWindow\(QDialog\):.*?def accept\(self\):.*?super\(\).accept\(\).*?if self.parent:\n.*?self\.parent\.load_settings\(\).*?\n    \n', content, re.DOTALL)

# 保留第一个SettingsWindow，删除其余的
if len(settings_windows) > 1:
    # 找到第一个SettingsWindow的结束位置
    first_settings_end = content.find(settings_windows[0]) + len(settings_windows[0])
    # 找到最后一个SettingsWindow的开始位置
    last_settings_start = content.rfind('class SettingsWindow(QDialog):')
    # 保留第一个SettingsWindow，删除中间的所有内容
    content = content[:first_settings_end] + content[last_settings_start:]

# 2. 找到FurnaceDetailsWindow类的结束位置
furnace_details_end = content.find('class SettingsWindow(QDialog):')

# 3. 提取需要的方法
methods = '''
    def connect_signals(self):
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
'''

# 4. 插入方法到FurnaceDetailsWindow类中
new_content = content[:furnace_details_end] + methods + content[furnace_details_end:]

# 5. 修复SettingsWindow类
# 移除SettingsWindow中错误的方法
settings_start = new_content.find('class SettingsWindow(QDialog):')
if settings_start != -1:
    # 找到SettingsWindow类的结束
    settings_end = new_content.find('class ExportProcessWindow', settings_start)
    if settings_end == -1:
        settings_end = len(new_content)
    
    # 重建SettingsWindow类
    new_settings = '''class SettingsWindow(QDialog):
    """设置窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setGeometry(300, 200, 600, 400)
        self.parent = parent
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加标签
        label = QLabel("设置选项")
        label.setFont(QFont("宋体", 16))
        layout.addWidget(label)
        
        # 添加按钮
        button = QPushButton("确定")
        button.clicked.connect(self.accept)
        layout.addWidget(button)
        
    def accept(self):
        """确认设置"""
        super().accept()
        if self.parent:
            self.parent.load_settings()
'''
    
    new_content = new_content[:settings_start] + new_settings + new_content[settings_end:]

# 6. 写入文件
with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已修复装炉明细窗口的方法归属问题")
