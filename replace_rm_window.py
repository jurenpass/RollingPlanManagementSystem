#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到RMMainWindow类的开始和结束位置
start_marker = 'class RMMainWindow(QMainWindow):'
end_marker = '    def init_data(self):\n        """初始化数据"""\n        print("粗轧主画面窗口已初始化")'

# 新的简化RMMainWindow类
new_class = '''class RMMainWindow(QMainWindow):
    """粗轧主画面窗口 - 复刻西门子WinCC粗轧主画面"""
    
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("粗轧主画面")
        self.resize(1400, 800)
        
        # 设置窗口背景色为WinCC风格的灰色
        self.setStyleSheet("background-color: #c8c8c8;")
        
        try:
            # 创建中心部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 主布局
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # 标题
            title_label = QLabel("粗轧主画面 (Roughing Mill Main Screen)")
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("color: #000080; padding: 10px;")
            main_layout.addWidget(title_label)
            
            # 简单的状态显示
            status_text = QLabel("系统状态: 正常运行")
            status_text.setFont(QFont("Arial", 12))
            status_text.setStyleSheet("color: #008000; padding: 10px; background-color: #e0e0e0;")
            main_layout.addWidget(status_text)
            
            # 添加一些简单的按钮
            btn_layout = QHBoxLayout()
            
            btn1 = QPushButton("Mill Mode")
            btn1.setStyleSheet("background-color: #c0c0c0; border: 1px solid #808080; padding: 10px;")
            btn_layout.addWidget(btn1)
            
            btn2 = QPushButton("Stand Mode")
            btn2.setStyleSheet("background-color: #c0c0c0; border: 1px solid #808080; padding: 10px;")
            btn_layout.addWidget(btn2)
            
            btn3 = QPushButton("Sizing Press Mode")
            btn3.setStyleSheet("background-color: #c0c0c0; border: 1px solid #808080; padding: 10px;")
            btn_layout.addWidget(btn3)
            
            main_layout.addLayout(btn_layout)
            
            # 添加一些数据显示
            data_group = QGroupBox("轧机参数")
            data_layout = QGridLayout(data_group)
            
            param_labels = ["入口温度", "出口温度", "机架1厚度", "机架2厚度", "速度"]
            param_values = ["1100°C", "600°C", "20.5 mm", "15.2 mm", "3.5 m/s"]
            
            for i, (label, value) in enumerate(zip(param_labels, param_values)):
                lbl = QLabel(label + ":")
                lbl.setFont(QFont("Arial", 10))
                val = QLabel(value)
                val.setFont(QFont("Arial", 10, QFont.Bold))
                val.setStyleSheet("color: #0000ff;")
                data_layout.addWidget(lbl, i, 0)
                data_layout.addWidget(val, i, 1)
            
            main_layout.addWidget(data_group)
            
            main_layout.addStretch()
            
            print("粗轧主画面窗口创建成功")
        except Exception as e:
            print(f"创建粗轧主画面窗口时出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"创建窗口失败: {str(e)}")'''

# 找到开始和结束的索引
start_idx = content.find(start_marker)
if start_idx == -1:
    print("未找到RMMainWindow类")
    exit(1)

# 从开始位置往后找，找到文件中该类之后的内容结束位置
# 这里我们假设类一直到文件末尾，或者找到某个特定标记
# 让我们用更精确的方式，找到这个类的结束位置

# 找到这个类开始之后，下一个顶级定义或者文件末尾
# 简单的方法是替换从start_marker开始到文件末尾，
# 但我们需要先确认

# 先看看这个类有多长
# 让我们用简单的方法：找到第一个RMMainWindow，然后替换到文件末尾

# 但这样会破坏后面的内容，所以我们需要更精确

# 我们先搜索到这个类的结束位置
# 找到在这个类之后，下一个class出现的位置，或者文件末尾

next_class_marker = None
# 搜索在start_idx之后的下一个class
possible_markers = ['\nclass ', '\nif __name__', '\ndef ']
min_pos = len(content)

for marker in possible_markers:
    pos = content.find(marker, start_idx + len(start_marker))
    if pos != -1 and pos < min_pos:
        min_pos = pos
        next_class_marker = marker

# 现在提取需要替换的部分
end_idx = min_pos

# 进行替换
old_content = content[start_idx:end_idx]
content = content[:start_idx] + new_class + content[end_idx:]

# 写入文件
with open(r'g:\newplan\furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("替换完成！")
